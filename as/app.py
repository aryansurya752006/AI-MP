import math
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "airbnb_price_model.joblib"
AMENITY_LABELS = {
    "has_wifi": "Wi-Fi",
    "has_kitchen": "Kitchen",
    "has_ac": "Air conditioning",
    "has_heating": "Heating",
    "has_tv": "TV",
    "has_parking": "Parking",
}
CATEGORICAL_FIELDS = (
    "city",
    "neighbourhood",
    "property_type",
    "room_type",
    "bed_type",
    "cancellation_policy",
)
INTEGER_RANGES = {
    "accommodates": (1, 16),
    "bedrooms": (0, 10),
    "beds": (0, 18),
}


def load_model_bundle():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. "
            "Place airbnb_price_model.joblib in the models folder."
        )

    bundle = joblib.load(MODEL_PATH)
    required_keys = {
        "model",
        "all_features",
        "cities",
        "neighbourhoods_by_city",
        "property_types",
        "room_types",
        "bed_types",
        "cancellation_policies",
        "amenity_map",
    }
    missing_keys = required_keys.difference(bundle)
    if missing_keys:
        raise ValueError(f"Model bundle is missing required fields: {sorted(missing_keys)}")

    expected_features = [
        *CATEGORICAL_FIELDS,
        "accommodates",
        "bathrooms",
        "bedrooms",
        "beds",
        "cleaning_fee",
        "instant_bookable",
        *AMENITY_LABELS,
    ]
    if bundle["all_features"] != expected_features:
        raise ValueError("The model feature schema does not match the website.")
    if set(bundle["amenity_map"]) != set(AMENITY_LABELS):
        raise ValueError("The model amenity schema does not match the website.")

    return bundle


model_bundle = load_model_bundle()
app = Flask(__name__)


def parse_number(payload, field, minimum, maximum, integer=False):
    value = payload.get(field)
    if isinstance(value, bool):
        raise ValueError(f"{field.replace('_', ' ').capitalize()} must be a number.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field.replace('_', ' ').capitalize()} must be a number.") from None

    if not math.isfinite(number):
        raise ValueError(f"{field.replace('_', ' ').capitalize()} must be finite.")
    if integer and not number.is_integer():
        raise ValueError(f"{field.replace('_', ' ').capitalize()} must be a whole number.")
    if not minimum <= number <= maximum:
        raise ValueError(
            f"{field.replace('_', ' ').capitalize()} must be between {minimum} and {maximum}."
        )
    return int(number) if integer else number


def validate_listing(payload):
    if not isinstance(payload, dict):
        raise ValueError("Send the listing details as a JSON object.")

    row = {}
    option_fields = {
        "city": model_bundle["cities"],
        "property_type": model_bundle["property_types"],
        "room_type": model_bundle["room_types"],
        "bed_type": model_bundle["bed_types"],
        "cancellation_policy": model_bundle["cancellation_policies"],
    }
    for field, options in option_fields.items():
        value = payload.get(field)
        if value not in options:
            raise ValueError(f"Choose a valid {field.replace('_', ' ')}.")
        row[field] = value

    neighbourhood = payload.get("neighbourhood")
    valid_neighbourhoods = model_bundle["neighbourhoods_by_city"].get(row["city"], [])
    if neighbourhood not in valid_neighbourhoods:
        raise ValueError("Choose a neighbourhood from the selected city.")
    row["neighbourhood"] = neighbourhood

    row["accommodates"] = parse_number(payload, "accommodates", 1, 16, integer=True)
    row["bathrooms"] = parse_number(payload, "bathrooms", 0, 8)
    row["bedrooms"] = parse_number(payload, "bedrooms", 0, 10, integer=True)
    row["beds"] = parse_number(payload, "beds", 0, 18, integer=True)

    for field in ("cleaning_fee", "instant_bookable"):
        value = payload.get(field)
        if not isinstance(value, bool):
            raise ValueError(f"{field.replace('_', ' ').capitalize()} must be true or false.")
        row[field] = int(value)

    amenities = payload.get("amenities")
    if not isinstance(amenities, list) or any(
        not isinstance(amenity, str) for amenity in amenities
    ):
        raise ValueError("Amenities must be a list of selected options.")
    unknown_amenities = set(amenities).difference(AMENITY_LABELS)
    if unknown_amenities:
        raise ValueError("Choose only amenities shown in the form.")
    for amenity in AMENITY_LABELS:
        row[amenity] = int(amenity in amenities)

    return row


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/options")
def get_options():
    return jsonify(
        {
            "cities": model_bundle["cities"],
            "neighbourhoods_by_city": model_bundle["neighbourhoods_by_city"],
            "property_types": model_bundle["property_types"],
            "room_types": model_bundle["room_types"],
            "bed_types": model_bundle["bed_types"],
            "cancellation_policies": model_bundle["cancellation_policies"],
            "amenities": AMENITY_LABELS,
            "model_name": model_bundle["model_name"],
            "test_mae_dollars": model_bundle["test_mae_dollars"],
            "note": model_bundle["note"],
        }
    )


@app.post("/api/predict")
def predict():
    if not request.is_json:
        return jsonify({"error": "Send the listing details as JSON."}), 415
    try:
        payload = request.get_json()
    except BadRequest:
        return jsonify({"error": "The request body is not valid JSON."}), 400

    try:
        row = validate_listing(payload)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    features = pd.DataFrame([row], columns=model_bundle["all_features"])
    log_price = float(model_bundle["model"].predict(features)[0])
    if not math.isfinite(log_price) or log_price > math.log(float.fromhex("0x1.fffffffffffffp+1023")):
        raise ValueError("The model returned a price outside the supported range.")
    price = math.exp(log_price)
    return jsonify(
        {
            "predicted_price": round(price, 2),
            "currency": "USD",
            "period": "night",
            "model_name": model_bundle["model_name"],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
