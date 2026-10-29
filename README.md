<<<<<<< Updated upstream
# AI For Business Mini Project
[Dataset](https://www.kaggle.com/datasets/stevezhenghp/airbnb-price-prediction)
Linear Regression -> Model ->predict (regression-> ) -> create simple website ->HTML , CSS , JS FlaskAPI ,NextJS.
=======
# Smart Airbnb Pricing System

This project estimates historical Airbnb nightly prices from listing attributes
using the Kaggle [Airbnb Price Prediction dataset](https://www.kaggle.com/datasets/stevezhenghp/airbnb-price-prediction).
It is a learning project, not a live-market quote.

## Setup

Use Python 3.9 or newer. Put the original Kaggle `train.csv` in this directory;
the training code reads it but does not modify it.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Train and evaluate

From this directory, run:

```bash
python -m src.train
```

The script uses a reproducible 80/20 split (seed 42), fits preprocessing only
on the training split, compares a median-log-price baseline with Linear
Regression, saves the fitted pipeline to `models/airbnb_price_model.joblib`,
reloads it, and makes a prediction using a complete held-out dataset row.
MAE and RMSE are in USD after applying `exp(log_price)`; R² is on the
`log_price` scale.

Run the model tests after training:

```bash
python -m unittest discover -s tests -v
```

The saved artifact and the source dataset are local files and are excluded from
Git. To predict from Python, pass all the model features in the order-independent
mapping expected by `src.predict_price.predict_price`; see
`src/predict_price.py` for the canonical feature names and validation rules.

For an interactive prompt that asks for a city, property/room type, guests,
bedrooms, bathrooms, beds, fees, booking status, and amenities, run:

```bash
python -m src.predict_price
```

The model uses city as its location feature; it does not use a street address or
neighbourhood. Categorical choices are restricted to values present in the
training data.

`IMPLEMENTATION_STATUS.md` records the verified metrics, executed commands, and
current limitations.
>>>>>>> Stashed changes
