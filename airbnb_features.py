"""
airbnb_features.py
------------------
Feature engineering used by BOTH the training notebook and the Streamlit app.

Why a separate .py file?
    joblib/pickle stores custom classes *by reference* (module name + class name).
    If the class lived only inside the notebook (module "__main__"), the saved
    model could not be re-loaded from another script such as app.py.
    Keeping it here makes the saved pipeline fully portable.

Everything that LEARNS something from data (the amenity vocabulary and the
neighbourhood centroids) does so in .fit(), i.e. on TRAINING DATA ONLY.
"""
import ast
import re

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Reference "today" for date features. The scrape ended on 2017-10-05
# (latest review / host_since date in the data), so we measure time against it.
REFERENCE_DATE = pd.Timestamp("2017-10-05")

# Approximate city-centre coordinates (public domain knowledge, not learned from the target).
CITY_CENTRES = {
    "NYC": (40.7580, -73.9855),      # Times Square
    "LA": (34.0522, -118.2437),      # Downtown LA
    "SF": (37.7749, -122.4194),      # Downtown San Francisco
    "DC": (38.9072, -77.0369),       # Downtown Washington DC
    "Chicago": (41.8781, -87.6298),  # The Loop
    "Boston": (42.3601, -71.0589),   # Downtown Boston
}


def parse_amenities(value):
    """Turn the raw amenities cell into a clean list of strings.

    Raw format in the dataset:  {TV,"Wireless Internet","Air conditioning"}
    The function also accepts a Python list/tuple/set (used by the app/widgets).
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip().strip("{}")
    if not text:
        return []
    items = re.findall(r'"([^"]+)"|([^,]+)', text)
    out = []
    for quoted, plain in items:
        name = (quoted or plain).strip()
        # drop the dataset's untranslated placeholders such as "translation missing: en.hosting_amenity_49"
        if name and not name.lower().startswith("translation missing"):
            out.append(name)
    return out


def _haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in kilometres (vectorised)."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def _slug(name):
    return "amen_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _to_bool01(series):
    """'t'/'f', True/False, 1/0, 'true'/'false' -> 1/0 (NaN stays NaN)."""
    mapping = {"t": 1, "true": 1, "1": 1, "yes": 1, "f": 0, "false": 0, "0": 0, "no": 0}
    return series.map(lambda v: np.nan if pd.isna(v) else mapping.get(str(v).strip().lower(), np.nan)).astype(float)


class ListingFeatureEngineer(BaseEstimator, TransformerMixin):
    """Cleans raw listing columns and creates engineered features.

    Learned in fit (training data only):
        * amenity_vocab_      - the `top_amenities` most common amenities
        * neigh_centroids_    - median (lat, lon) of every (city, neighbourhood)
        * city_centroids_     - median (lat, lon) of every city (fallback)
    """

    def __init__(self, top_amenities=25, min_amenity_share=0.02):
        self.top_amenities = top_amenities
        self.min_amenity_share = min_amenity_share

    # ------------------------------------------------------------------ fit
    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        # 1) amenity vocabulary
        counts = {}
        for cell in X["amenities"] if "amenities" in X else []:
            for a in set(parse_amenities(cell)):
                counts[a] = counts.get(a, 0) + 1
        n = max(len(X), 1)
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        self.amenity_vocab_ = [a for a, c in ranked if c / n >= self.min_amenity_share][: self.top_amenities]

        # 2) location fall-backs
        geo = X[["city", "neighbourhood", "latitude", "longitude"]].dropna(subset=["latitude", "longitude"])
        self.neigh_centroids_ = (geo.dropna(subset=["neighbourhood"])
                                 .groupby(["city", "neighbourhood"])[["latitude", "longitude"]].median())
        self.city_centroids_ = geo.groupby("city")[["latitude", "longitude"]].median()
        return self

    # ------------------------------------------------------------ transform
    def transform(self, X):
        X = pd.DataFrame(X).copy()
        out = pd.DataFrame(index=X.index)

        # ---- categorical columns (missing text -> "Unknown")
        for col in ["city", "property_type", "room_type", "bed_type", "cancellation_policy", "neighbourhood"]:
            out[col] = X[col].astype("object").where(X[col].notna(), "Unknown") if col in X else "Unknown"
            out[col] = out[col].astype(str)
        out["property_room"] = out["property_type"] + " | " + out["room_type"]   # combination feature

        # ---- numeric basics, impossible values -> NaN (imputed later in the pipeline)
        def num(col):
            return pd.to_numeric(X[col], errors="coerce") if col in X else pd.Series(np.nan, index=X.index)

        acc = num("accommodates").where(lambda s: (s >= 1) & (s <= 30))
        bath = num("bathrooms").where(lambda s: (s >= 0) & (s <= 15))
        bed_r = num("bedrooms").where(lambda s: (s >= 0) & (s <= 20))
        beds = num("beds").where(lambda s: (s >= 0) & (s <= 30))
        n_rev = num("number_of_reviews").clip(lower=0)
        rating = num("review_scores_rating").where(lambda s: (s >= 0) & (s <= 100))
        out["accommodates"], out["bathrooms"], out["bedrooms"], out["beds"] = acc, bath, bed_r, beds
        out["number_of_reviews"], out["review_scores_rating"] = n_rev, rating

        # ---- binary flags
        for col in ["cleaning_fee", "instant_bookable", "host_identity_verified", "host_has_profile_pic"]:
            out[col] = _to_bool01(X[col]) if col in X else np.nan
        resp = X["host_response_rate"] if "host_response_rate" in X else pd.Series(np.nan, index=X.index)
        resp = pd.to_numeric(resp.astype(str).str.replace("%", "", regex=False), errors="coerce")
        out["host_response_rate"] = resp.where((resp >= 0) & (resp <= 100))

        # ---- location
        lat = num("latitude").copy()
        lon = num("longitude").copy()
        # fill missing coordinates from the neighbourhood centroid, then the city centroid
        miss = (lat.isna() | lon.isna()).to_numpy()
        if miss.any():
            lat_v, lon_v = lat.to_numpy(dtype=float).copy(), lon.to_numpy(dtype=float).copy()
            cities = X["city"].to_numpy() if "city" in X else np.array([None] * len(X))
            neighs = X["neighbourhood"].to_numpy() if "neighbourhood" in X else np.array([None] * len(X))
            for pos in np.flatnonzero(miss):
                key = (cities[pos], neighs[pos])
                if key in self.neigh_centroids_.index:
                    lat_v[pos], lon_v[pos] = self.neigh_centroids_.loc[key].values
                elif cities[pos] in self.city_centroids_.index:
                    lat_v[pos], lon_v[pos] = self.city_centroids_.loc[cities[pos]].values
            lat = pd.Series(lat_v, index=X.index)
            lon = pd.Series(lon_v, index=X.index)
        out["latitude"], out["longitude"] = lat, lon
        centre = out["city"].map(CITY_CENTRES)
        c_lat = centre.map(lambda t: t[0] if isinstance(t, tuple) else np.nan)
        c_lon = centre.map(lambda t: t[1] if isinstance(t, tuple) else np.nan)
        out["dist_to_centre_km"] = _haversine_km(lat, lon, c_lat, c_lon)

        # ---- ratios / capacity features
        out["guests_per_bedroom"] = acc / bed_r.clip(lower=1)
        out["guests_per_bed"] = acc / beds.clip(lower=1)
        out["bath_per_guest"] = bath / acc
        out["total_rooms"] = bed_r + bath

        # ---- date features (relative to the scrape date)
        def days_since(col):
            if col not in X:
                return pd.Series(np.nan, index=X.index)
            return (REFERENCE_DATE - pd.to_datetime(X[col], errors="coerce")).dt.days

        out["host_tenure_years"] = days_since("host_since") / 365.25
        out["days_since_last_review"] = days_since("last_review")
        out["listing_age_days"] = days_since("first_review")
        # allow the app to pass the engineered values directly instead of dates
        for col in ["host_tenure_years", "days_since_last_review", "listing_age_days"]:
            if col in X:
                direct = pd.to_numeric(X[col], errors="coerce")
                out[col] = out[col].where(out[col].notna(), direct)
        out["has_reviews"] = (n_rev.fillna(0) > 0).astype(int)
        out["reviews_per_year"] = n_rev / (out["listing_age_days"].clip(lower=30) / 365.25)
        out["reviews_per_year"] = out["reviews_per_year"].where(out["has_reviews"] == 1, 0)

        # ---- amenities
        parsed = X["amenities"].map(parse_amenities) if "amenities" in X else pd.Series([[]] * len(X), index=X.index)
        out["amenity_count"] = parsed.map(len)
        for a in self.amenity_vocab_:
            out[_slug(a)] = parsed.map(lambda lst, a=a: int(a in lst))
        return out

    # names used by the notebook to build the ColumnTransformer
    @property
    def amenity_columns_(self):
        return [_slug(a) for a in self.amenity_vocab_]


CATEGORICAL_FEATURES = ["city", "property_type", "room_type", "bed_type", "cancellation_policy",
                        "neighbourhood", "property_room"]
NUMERIC_FEATURES = ["accommodates", "bathrooms", "bedrooms", "beds", "number_of_reviews",
                    "review_scores_rating", "host_response_rate", "latitude", "longitude",
                    "dist_to_centre_km", "guests_per_bedroom", "guests_per_bed", "bath_per_guest",
                    "total_rooms", "host_tenure_years", "days_since_last_review", "listing_age_days",
                    "reviews_per_year", "amenity_count"]
BINARY_FEATURES = ["cleaning_fee", "instant_bookable", "host_identity_verified", "host_has_profile_pic",
                   "has_reviews"]


# =====================================================================================
# Prediction helpers (shared by the notebook widgets, the plain-Python function and app.py)
# =====================================================================================
RAW_INPUT_COLUMNS = ["city", "neighbourhood", "property_type", "room_type", "bed_type", "cancellation_policy",
                     "accommodates", "bedrooms", "beds", "bathrooms", "cleaning_fee", "instant_bookable",
                     "host_identity_verified", "host_has_profile_pic", "host_response_rate", "host_since",
                     "number_of_reviews", "review_scores_rating", "first_review", "last_review",
                     "latitude", "longitude", "amenities"]
# A user cannot type exact dates, so the pipeline also accepts these three ready-made values.
PREDICTION_COLUMNS = RAW_INPUT_COLUMNS + ["host_tenure_years", "days_since_last_review", "listing_age_days"]

CATEGORICAL_INPUTS = ["city", "property_type", "room_type", "bed_type", "cancellation_policy"]
NUMERIC_INPUTS = ["accommodates", "bedrooms", "beds", "bathrooms", "number_of_reviews", "review_scores_rating",
                  "host_response_rate", "host_tenure_years", "days_since_last_review", "listing_age_days"]
BOOLEAN_INPUTS = ["cleaning_fee", "instant_bookable", "host_identity_verified", "host_has_profile_pic"]
OPTIONAL_INPUTS = ["review_scores_rating", "host_response_rate", "host_tenure_years",
                   "days_since_last_review", "listing_age_days"]       # may be left empty (None)


def validate_inputs(inputs, spec):
    """Check user input against the specification learned from the TRAINING data.

    Returns (clean_inputs, warnings). Raises ValueError listing every problem found."""
    errors, warns = [], []
    clean = {}
    d = spec["defaults"]

    for f in CATEGORICAL_INPUTS:
        v = inputs.get(f, d[f])
        if v not in spec["categories"][f]:
            errors.append(f"'{f}' = {v!r} is not valid. Choose one of: {spec['categories'][f]}")
        clean[f] = v

    city = clean["city"]
    neigh = inputs.get("neighbourhood", "Unknown") or "Unknown"
    allowed = ["Unknown"] + spec["neighbourhoods"].get(city, [])
    if neigh not in allowed:
        errors.append(f"'neighbourhood' = {neigh!r} is not known for {city}. Use 'Unknown' or one of the "
                      f"{len(allowed)-1} known neighbourhoods.")
    clean["neighbourhood"] = neigh

    for f in NUMERIC_INPUTS:
        v = inputs.get(f, d.get(f) if f not in OPTIONAL_INPUTS else None)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            if f not in OPTIONAL_INPUTS:
                errors.append(f"'{f}' is required.")
            clean[f] = np.nan
            continue
        try:
            v = float(v)
        except (TypeError, ValueError):
            errors.append(f"'{f}' must be a number (got {v!r}).")
            continue
        lo, hi = spec["ranges"][f]
        if not (lo <= v <= hi):
            errors.append(f"'{f}' = {v} is outside the range seen in training data ({lo} to {hi}).")
        clean[f] = v

    for f in BOOLEAN_INPUTS:
        clean[f] = bool(inputs.get(f, d[f]))

    am = inputs.get("amenities", ())
    clean["amenities"] = parse_amenities(list(am) if not isinstance(am, str) else am)

    if errors:
        raise ValueError("Invalid input:\n  - " + "\n  - ".join(errors))

    # cross-field sanity checks (warnings only)
    if clean["bedrooms"] > clean["accommodates"]:
        warns.append("More bedrooms than guests is unusual; the estimate may be less reliable.")
    if clean["beds"] > 2 * clean["accommodates"]:
        warns.append("Many more beds than guests is unusual; the estimate may be less reliable.")
    if clean["number_of_reviews"] == 0:
        for f in ["review_scores_rating", "days_since_last_review", "listing_age_days"]:
            clean[f] = np.nan                      # a listing without reviews has no rating / review dates
    return clean, warns


def build_input_frame(clean):
    """One-row DataFrame with exactly the columns the saved pipeline expects."""
    row = {c: np.nan for c in PREDICTION_COLUMNS}
    row.update(clean)
    return pd.DataFrame([row], columns=PREDICTION_COLUMNS)


def predict_price(model, spec, **inputs):
    """Validate -> DataFrame -> pipeline.predict -> price (+ typical range)."""
    clean, warns = validate_inputs(inputs, spec)
    log_p = float(model.predict(build_input_frame(clean))[0])
    lo_q, hi_q = spec["residual_quantiles"]                  # 16th / 84th percentile of test residuals (log scale)
    return {"price": float(np.exp(log_p)), "log_price": log_p,
            "low": float(np.exp(log_p + lo_q)), "high": float(np.exp(log_p + hi_q)),
            "warnings": warns, "inputs": clean}


def explain_prediction(model, spec, **inputs):
    """Approximate, one-feature-at-a-time explanation.

    For each input we replace ONLY that input by the 'typical' value from the training data and see how the
    prediction changes. effect = (price with your value) - (price with the typical value).
    This is a what-if analysis, not a causal statement."""
    base = predict_price(model, spec, **inputs)
    clean = base["inputs"]
    d = spec["defaults"]
    groups = {
        "neighbourhood": {"neighbourhood": "Unknown"},
        "room_type": {"room_type": d["room_type"]},
        "property_type": {"property_type": d["property_type"]},
        "bed_type": {"bed_type": d["bed_type"]},
        "cancellation_policy": {"cancellation_policy": d["cancellation_policy"]},
        "accommodates": {"accommodates": d["accommodates"]},
        "bedrooms": {"bedrooms": d["bedrooms"]},
        "beds": {"beds": d["beds"]},
        "bathrooms": {"bathrooms": d["bathrooms"]},
        "cleaning_fee": {"cleaning_fee": d["cleaning_fee"]},
        "instant_bookable": {"instant_bookable": d["instant_bookable"]},
        "host_identity_verified": {"host_identity_verified": d["host_identity_verified"]},
        "amenities": {"amenities": spec["default_amenities"]},
        "review history": {"number_of_reviews": d["number_of_reviews"],
                           "review_scores_rating": d["review_scores_rating"],
                           "days_since_last_review": d["days_since_last_review"],
                           "listing_age_days": d["listing_age_days"]},
    }
    rows = []
    for name, change in groups.items():
        alt = dict(clean)
        alt.update(change)
        alt_log = float(model.predict(build_input_frame(alt))[0])
        shown = ", ".join(f"{k}={clean[k]}" for k in change if k != "amenities") if name != "amenities" \
            else f"{len(clean['amenities'])} amenities"
        rows.append({"factor": name, "your value": shown[:60],
                     "effect on price": base["price"] - float(np.exp(alt_log))})
    out = pd.DataFrame(rows).sort_values("effect on price", key=np.abs, ascending=False).reset_index(drop=True)
    return out
