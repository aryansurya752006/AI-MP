# Staywise Airbnb Price Estimator

A small Flask application that serves the trained Linear Regression model from the Airbnb pricing notebook. The form's dropdowns are loaded from the saved model bundle, and the API converts the model's log-price output back to a nightly price in USD.

## Run locally

Use Python 3.10 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The trained model must be present at `models/airbnb_price_model.joblib`. The included model was exported by the notebook and is version-sensitive; use a model file you trust and the scikit-learn version in `requirements.txt`.

## API

- `GET /api/options` returns the cities, neighborhoods, property types, room types, bed types, cancellation policies, and amenities stored with the model.
- `POST /api/predict` accepts listing details as JSON and returns `predicted_price` in USD per night. Invalid selections or values return a JSON error with HTTP 400.

The estimate reflects historical listing data and is not a guarantee of current market prices.

## Tests

```bash
python -m unittest discover -s tests
```
