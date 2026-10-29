import json
import subprocess
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.predict_price import (
    FEATURE_COLUMNS,
    MODEL_PATH,
    NUMERIC_FEATURES,
    interactive_prediction,
    load_model,
    predict_price,
    prediction_frame,
)
from src.train import DATASET_PATH, load_dataset, prepare_features


class InvalidOutputModel:
    def __init__(self, value):
        self.value = value

    def predict(self, features):
        return np.array([self.value])


class PredictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_model()
        raw_sample = pd.read_csv(DATASET_PATH, nrows=200)
        features = prepare_features(raw_sample)
        complete_rows = features.dropna(subset=list(NUMERIC_FEATURES))
        if complete_rows.empty:
            raise AssertionError("The first 200 dataset rows contain no complete sample.")
        cls.sample = complete_rows.iloc[0].to_dict()

    def test_artifact_loads_and_has_canonical_feature_order(self):
        model = load_model()
        self.assertEqual(tuple(model.feature_names_in_), FEATURE_COLUMNS)

    def test_successful_prediction_is_finite_and_positive(self):
        price = predict_price(self.sample, self.model)
        self.assertTrue(np.isfinite(price))
        self.assertGreater(price, 0)

    def test_interactive_prediction_prompts_for_listing_and_returns_price(self):
        answers = iter(
            [
                self.sample["city"],
                self.sample["room_type"],
                self.sample["property_type"],
                str(self.sample["accommodates"]),
                str(self.sample["bedrooms"]),
                str(self.sample["bathrooms"]),
                str(self.sample["beds"]),
                str(self.sample["cleaning_fee"]),
                str(self.sample["instant_bookable"]),
                *[str(self.sample[feature]) for feature in FEATURE_COLUMNS[9:]],
            ]
        )
        output = []
        price = interactive_prediction(
            input_fn=lambda _prompt: next(answers),
            output_fn=output.append,
        )
        self.assertTrue(np.isfinite(price))
        self.assertGreater(price, 0)
        self.assertTrue(any("Estimated price:" in line for line in output))
        self.assertTrue(any("historical listing data" in line for line in output))

    def test_missing_feature_is_rejected(self):
        listing = dict(self.sample)
        listing.pop(FEATURE_COLUMNS[0])
        with self.assertRaisesRegex(ValueError, "missing features"):
            prediction_frame(listing)

    def test_invalid_feature_is_rejected(self):
        listing = dict(self.sample)
        listing["accommodates"] = -1
        with self.assertRaisesRegex(ValueError, "at least 1"):
            prediction_frame(listing)

    def test_invalid_feature_type_is_rejected(self):
        listing = dict(self.sample)
        listing["bathrooms"] = "not-a-number"
        with self.assertRaisesRegex(ValueError, "finite numeric value"):
            prediction_frame(listing)

    def test_non_finite_input_feature_is_rejected(self):
        listing = dict(self.sample)
        listing["bathrooms"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite numeric value"):
            prediction_frame(listing)

    def test_unexpected_feature_is_rejected(self):
        listing = dict(self.sample, undocumented_field=1)
        with self.assertRaisesRegex(ValueError, "unexpected features"):
            prediction_frame(listing)

    def test_missing_dataset_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            load_dataset(DATASET_PATH.parent / "missing-train.csv")

    def test_missing_model_is_reported(self):
        with self.assertRaises(FileNotFoundError):
            load_model(MODEL_PATH.parent / "missing-model.joblib")

    def test_non_finite_model_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid log-price"):
            predict_price(self.sample, InvalidOutputModel(float("nan")))

    def test_non_finite_price_after_inverse_transform_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not a finite positive price"):
            predict_price(self.sample, InvalidOutputModel(1000.0))

    def test_fresh_python_process_loads_and_predicts(self):
        payload = json.dumps(self.sample)
        code = (
            "import json; from src.predict_price import load_model, predict_price; "
            f"print(predict_price(json.loads({payload!r}), load_model()))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=Path(__file__).resolve().parents[1],
            check=True,
            capture_output=True,
            text=True,
        )
        prediction = float(completed.stdout.strip())
        self.assertTrue(np.isfinite(prediction))
        self.assertGreater(prediction, 0)


if __name__ == "__main__":
    unittest.main()
