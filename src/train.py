"""Reproducible training and evaluation for the Airbnb log-price dataset."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from .predict_price import (
    AMENITIES,
    AMENITY_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    MODEL_PATH,
    NUMERIC_FEATURES,
    load_model,
    predict_price,
)


RANDOM_STATE = 42
TEST_SIZE = 0.2
DATASET_PATH = Path(__file__).resolve().parents[1] / "train.csv"
TARGET_COLUMN = "log_price"
REQUIRED_DATASET_COLUMNS = (
    "id",
    TARGET_COLUMN,
    *CATEGORICAL_FEATURES,
    "amenities",
    *NUMERIC_FEATURES[:-len(AMENITY_FEATURES)],
)


def load_dataset(data_path: str | Path = DATASET_PATH) -> pd.DataFrame:
    """Load the original CSV, with a clear error if it is missing."""
    path = Path(data_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Place the original Kaggle train.csv "
            "in the project directory or pass its path with --data."
        )
    return pd.read_csv(path)


def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """Extract model features in the one canonical order used at prediction time."""
    missing = [column for column in REQUIRED_DATASET_COLUMNS if column not in data]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    features = data.loc[:, CATEGORICAL_FEATURES].copy()
    for column in NUMERIC_FEATURES:
        if column in AMENITY_FEATURES:
            amenity = next(
                name
                for name, feature in zip(AMENITIES, AMENITY_FEATURES)
                if feature == column
            )
            listed_amenities = data["amenities"]
            features[column] = (
                listed_amenities.fillna("")
                .astype(str)
                .str.contains(amenity, case=False, regex=False)
                .astype(float)
                .where(listed_amenities.notna(), np.nan)
            )
        elif column in ("cleaning_fee", "instant_bookable"):
            normalized = data[column].astype("string").str.strip().str.lower()
            converted = normalized.map(
                {
                    "true": 1,
                    "t": 1,
                    "1": 1,
                    "false": 0,
                    "f": 0,
                    "0": 0,
                }
            )
            invalid = data[column].notna() & converted.isna()
            if invalid.any():
                examples = data.loc[invalid, column].astype(str).unique()[:5].tolist()
                raise ValueError(
                    f"Column {column} contains invalid boolean values: {examples}"
                )
            features[column] = converted
        else:
            converted = pd.to_numeric(data[column], errors="coerce")
            invalid = data[column].notna() & converted.isna()
            if invalid.any():
                examples = data.loc[invalid, column].astype(str).unique()[:5].tolist()
                raise ValueError(
                    f"Column {column} contains invalid numeric values: {examples}"
                )
            features[column] = converted

    return features.loc[:, FEATURE_COLUMNS]


def build_pipeline() -> Pipeline:
    """Build the preprocessing/model pipeline; all learned transforms fit on train rows."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                list(CATEGORICAL_FEATURES),
            ),
            (
                "numeric",
                SimpleImputer(strategy="median"),
                list(NUMERIC_FEATURES),
            ),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )


def _price_scale(log_prices: np.ndarray, label: str) -> np.ndarray:
    with np.errstate(over="ignore", invalid="ignore"):
        prices = np.exp(np.asarray(log_prices, dtype=float))
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError(f"{label} contains a non-finite or non-positive price.")
    return prices


def train_model(
    data_path: str | Path = DATASET_PATH,
    model_path: str | Path = MODEL_PATH,
) -> dict[str, Any]:
    """Train, evaluate, save, reload, and sample-predict the fitted pipeline."""
    raw_data = load_dataset(data_path)
    missing = [column for column in REQUIRED_DATASET_COLUMNS if column not in raw_data]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    data = raw_data.drop_duplicates(subset=["id"], keep="first").copy()
    target = pd.to_numeric(data[TARGET_COLUMN], errors="coerce")
    valid_target = target.notna() & np.isfinite(target) & (target >= 0)
    data = data.loc[valid_target].copy()
    target = target.loc[valid_target].astype(float)
    if data.empty:
        raise ValueError("Dataset contains no rows with a finite, non-negative log_price.")

    features = prepare_features(data)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    baseline = DummyRegressor(strategy="median")
    baseline.fit(np.zeros((len(y_train), 1)), y_train)
    baseline_log_predictions = baseline.predict(np.zeros((len(y_test), 1)))

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)
    model_log_predictions = pipeline.predict(x_test)

    actual_prices = _price_scale(y_test.to_numpy(), "Test targets")
    baseline_prices = _price_scale(baseline_log_predictions, "Baseline predictions")
    model_prices = _price_scale(model_log_predictions, "Linear Regression predictions")

    metrics = {
        "baseline": {
            "mae_usd": float(mean_absolute_error(actual_prices, baseline_prices)),
            "rmse_usd": float(np.sqrt(mean_squared_error(actual_prices, baseline_prices))),
            "r2_log_price": float(r2_score(y_test, baseline_log_predictions)),
        },
        "linear_regression": {
            "mae_usd": float(mean_absolute_error(actual_prices, model_prices)),
            "rmse_usd": float(np.sqrt(mean_squared_error(actual_prices, model_prices))),
            "r2_log_price": float(r2_score(y_test, model_log_predictions)),
        },
    }

    artifact_path = Path(model_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact_path)

    reloaded = load_model(artifact_path)
    complete_rows = x_test.dropna(subset=list(NUMERIC_FEATURES))
    if complete_rows.empty:
        raise ValueError("No complete held-out feature row is available for sample prediction.")
    sample = complete_rows.iloc[0].to_dict()
    loaded_price = predict_price(sample, reloaded)
    in_memory_log_prediction = float(pipeline.predict(complete_rows.iloc[[0]])[0])
    in_memory_price = float(
        _price_scale(np.array([in_memory_log_prediction]), "Sample")[0]
    )
    if not np.isclose(loaded_price, in_memory_price, rtol=1e-12, atol=1e-12):
        raise RuntimeError("Reloaded model prediction differs from the in-memory model.")

    return {
        "metrics": metrics,
        "rows_total": len(raw_data),
        "rows_used": len(data),
        "rows_train": len(x_train),
        "rows_test": len(x_test),
        "model_path": str(artifact_path),
        "sample_prediction_usd": loaded_price,
        "sample_features": sample,
        "model": pipeline,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATASET_PATH, help="Path to train.csv")
    parser.add_argument("--model", type=Path, default=MODEL_PATH, help="Output joblib path")
    args = parser.parse_args()

    result = train_model(args.data, args.model)
    print(f"Rows used: {result['rows_used']:,} / {result['rows_total']:,}")
    print(f"Train/test rows: {result['rows_train']:,} / {result['rows_test']:,}")
    print("MAE and RMSE are measured in USD after exp(log_price).")
    print("R² is measured on the log_price target scale (not a percentage accuracy).")
    for name, values in result["metrics"].items():
        print(
            f"{name}: MAE=${values['mae_usd']:.2f}, "
            f"RMSE=${values['rmse_usd']:.2f}, "
            f"R²(log_price)={values['r2_log_price']:.6f}"
        )
    print(f"Saved and reloaded model: {result['model_path']}")
    print(f"Sample prediction: ${result['sample_prediction_usd']:.2f} per night")


if __name__ == "__main__":
    main()
