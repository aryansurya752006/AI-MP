"""Model loading and validated price predictions for Airbnb listings."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from numbers import Real
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "airbnb_price_model.joblib"

CATEGORICAL_FEATURES = ("city", "room_type", "property_type")
AMENITIES = (
    "Wireless Internet",
    "Kitchen",
    "Air conditioning",
    "Heating",
    "TV",
    "parking",
)
AMENITY_FEATURES = tuple(
    f"has_{amenity.lower().replace(' ', '_')}" for amenity in AMENITIES
)
NUMERIC_FEATURES = (
    "accommodates",
    "bathrooms",
    "bedrooms",
    "beds",
    "cleaning_fee",
    "instant_bookable",
    *AMENITY_FEATURES,
)
FEATURE_COLUMNS = (*CATEGORICAL_FEATURES, *NUMERIC_FEATURES)
BINARY_FEATURES = frozenset(
    ("cleaning_fee", "instant_bookable", *AMENITY_FEATURES)
)
INTEGER_FEATURES = frozenset(("accommodates", "bedrooms", "beds"))


def load_model(model_path: str | Path = MODEL_PATH) -> Pipeline:
    """Load a fitted sklearn pipeline and verify its input feature contract."""
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Model artifact not found at {path}. Train it with "
            "`python -m src.train` from the project directory."
        )

    model = joblib.load(path)
    if not isinstance(model, Pipeline) or not hasattr(model, "feature_names_in_"):
        raise ValueError(f"Model artifact at {path} is not a fitted feature pipeline.")

    actual_features = tuple(str(name) for name in model.feature_names_in_)
    if actual_features != FEATURE_COLUMNS:
        raise ValueError(
            "Model feature contract does not match the prediction helper. "
            f"Expected {FEATURE_COLUMNS}, got {actual_features}."
        )
    return model


def prediction_frame(listing: Mapping[str, Any]) -> pd.DataFrame:
    """Validate a single listing and arrange fields in training feature order."""
    if not isinstance(listing, Mapping):
        raise TypeError("Listing input must be a mapping of feature names to values.")

    missing = [feature for feature in FEATURE_COLUMNS if feature not in listing]
    extra = sorted(set(listing) - set(FEATURE_COLUMNS))
    if missing or extra:
        problems = []
        if missing:
            problems.append(f"missing features: {missing}")
        if extra:
            problems.append(f"unexpected features: {extra}")
        raise ValueError("Invalid listing input (" + "; ".join(problems) + ").")

    row: dict[str, Any] = {}
    for feature in CATEGORICAL_FEATURES:
        value = listing[feature]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{feature} must be a non-empty string.")
        row[feature] = value.strip()

    for feature in NUMERIC_FEATURES:
        value = listing[feature]
        if feature in BINARY_FEATURES and isinstance(value, bool):
            number = int(value)
        elif isinstance(value, Real) and not isinstance(value, bool):
            number = float(value)
        else:
            raise ValueError(f"{feature} must be a finite numeric value.")

        if not isfinite(number):
            raise ValueError(f"{feature} must be a finite numeric value.")
        if feature in BINARY_FEATURES and number not in (0, 1):
            raise ValueError(f"{feature} must be either 0 or 1.")
        if feature == "accommodates" and number < 1:
            raise ValueError("accommodates must be at least 1.")
        if feature in INTEGER_FEATURES and not number.is_integer():
            raise ValueError(f"{feature} must be a whole number.")
        if feature in ("bathrooms", "bedrooms", "beds") and number < 0:
            raise ValueError(f"{feature} cannot be negative.")
        row[feature] = number

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def predict_price(
    listing: Mapping[str, Any],
    model: Pipeline | None = None,
) -> float:
    """Predict nightly USD price from the model's log-price output."""
    features = prediction_frame(listing)
    fitted_model = model if model is not None else load_model()
    log_price = np.asarray(fitted_model.predict(features), dtype=float)
    if log_price.shape != (1,) or not np.isfinite(log_price[0]):
        raise ValueError("The model returned an invalid log-price prediction.")

    with np.errstate(over="ignore", invalid="ignore"):
        price = float(np.exp(log_price[0]))
    if not isfinite(price) or price <= 0:
        raise ValueError("The model prediction is not a finite positive price.")
    return price


def _prompt_choice(
    label: str,
    choices: list[str],
    default: str,
    input_fn: Any,
    output_fn: Any,
) -> str:
    while True:
        answer = input_fn(
            f"{label} ({', '.join(choices)}) [{default}]: "
        ).strip()
        if not answer:
            return default
        match = next(
            (choice for choice in choices if choice.casefold() == answer.casefold()),
            None,
        )
        if match is not None:
            return match
        output_fn(f"Please choose one of: {', '.join(choices)}.")


def _prompt_number(
    label: str,
    default: str,
    input_fn: Any,
    output_fn: Any,
    *,
    whole_number: bool,
    minimum: float,
) -> int | float:
    while True:
        answer = input_fn(f"{label} [{default}]: ").strip() or default
        try:
            value = float(answer)
        except ValueError:
            output_fn("Please enter a number.")
            continue
        if not isfinite(value) or value < minimum:
            output_fn(f"Please enter a finite number of at least {minimum:g}.")
            continue
        if whole_number and not value.is_integer():
            output_fn("Please enter a whole number.")
            continue
        return int(value) if whole_number else value


def _prompt_yes_no(
    label: str,
    input_fn: Any,
    output_fn: Any,
    *,
    default: bool = False,
) -> int:
    default_text = "yes" if default else "no"
    while True:
        answer = input_fn(f"{label}? yes/no [{default_text}]: ").strip().lower()
        if not answer:
            return int(default)
        if answer in ("yes", "y", "true", "1", "1.0"):
            return 1
        if answer in ("no", "n", "false", "0", "0.0"):
            return 0
        output_fn("Please answer yes or no.")


def interactive_prediction(
    input_fn: Any = input,
    output_fn: Any = print,
) -> float:
    """Prompt for listing details and print a validated nightly price estimate."""
    model = load_model()
    encoder = (
        model.named_steps["preprocessor"]
        .named_transformers_["categorical"]
        .named_steps["encoder"]
    )
    categories = {
        feature: [str(value) for value in values]
        for feature, values in zip(CATEGORICAL_FEATURES, encoder.categories_)
    }

    output_fn("Smart Airbnb Pricing System")
    output_fn("Enter listing details. Press Enter to use a suggested default.")
    listing: dict[str, Any] = {}
    defaults = {
        "city": "NYC",
        "room_type": "Entire home/apt",
        "property_type": "Apartment",
    }
    for feature in CATEGORICAL_FEATURES:
        choices = categories[feature]
        suggested = defaults[feature]
        default = suggested if suggested in choices else choices[0]
        listing[feature] = _prompt_choice(
            feature.replace("_", " ").capitalize(),
            choices,
            default,
            input_fn,
            output_fn,
        )

    listing["accommodates"] = _prompt_number(
        "Guests the listing accommodates",
        "2",
        input_fn,
        output_fn,
        whole_number=True,
        minimum=1,
    )
    listing["bedrooms"] = _prompt_number(
        "Bedrooms",
        "1",
        input_fn,
        output_fn,
        whole_number=True,
        minimum=0,
    )
    listing["bathrooms"] = _prompt_number(
        "Bathrooms",
        "1",
        input_fn,
        output_fn,
        whole_number=False,
        minimum=0,
    )
    listing["beds"] = _prompt_number(
        "Beds",
        "1",
        input_fn,
        output_fn,
        whole_number=True,
        minimum=0,
    )
    listing["cleaning_fee"] = _prompt_yes_no(
        "Cleaning fee", input_fn, output_fn
    )
    listing["instant_bookable"] = _prompt_yes_no(
        "Instant bookable", input_fn, output_fn
    )
    for amenity, feature in zip(AMENITIES, AMENITY_FEATURES):
        listing[feature] = _prompt_yes_no(amenity, input_fn, output_fn)

    price = predict_price(listing, model)
    output_fn(f"\nEstimated price: ${price:,.2f} USD per night")
    output_fn("Estimate based on historical listing data; not a live market quote.")
    return price


if __name__ == "__main__":
    interactive_prediction()
