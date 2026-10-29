# Implementation Status — Smart Airbnb Pricing System

## Result

The Kaggle `train.csv` training and prediction workflow is reproducible and ready
for a Flask backend to call. The original dataset was not modified. The existing
notebook's analysis was retained, its dataset-writing mock cell was removed, and
the notebook now uses the same feature extraction and prediction contract as
the Python pipeline.

## Audit findings and fixes

- The notebook previously wrote synthetic data to `train.csv`, retried the same
  missing path on load failure, dropped valid zero-valued `log_price` rows, and
  used stale amenity/pipeline names. These were corrected.
- The earlier `College_Notes/airbnb-prediction/src` scripts use a separate
  AB_NYC_2019 dataset and a different `price` target. They were not changed;
  this implementation uses the Kaggle 29-column `train.csv` beside this
  notebook.
- Preprocessing is now part of one fitted scikit-learn pipeline, and is fit
  only on the training partition. Categorical missing values use the
  most-frequent training value; numeric missing values use the training
  median; unknown categories are tolerated by the encoder. Invalid target
  rows and duplicate IDs are excluded. A `log_price` of zero is retained.

## Files changed or created

- `Airbnb_Price_Prediction.ipynb` — removed dataset overwrite behavior and
  blanket warning suppression, fixed data loading/target handling, aligned
  features and pipeline references, and executed all cells to refresh outputs.
- `src/train.py` — dataset validation, reproducible split, baseline and Linear
  Regression training, USD metrics, joblib save/reload verification, and
  held-out sample prediction.
- `src/predict_price.py` — canonical feature ordering, artifact validation,
  input checks, conversion from predicted `log_price` to finite positive
  USD nightly price, and an interactive listing prompt.
- `src/__init__.py` — enables module execution from the project directory.
- `tests/test_model.py` — 13 `unittest` cases, including interactive prediction.
- `requirements.txt` — exact versions of the installed runtime dependencies.
- `.gitignore` — excludes the local source dataset, generated model, and Python
  environment/cache files from Git.
- `README.md` — setup, training, testing, metric scales, and prediction-helper
  guidance.
- `models/airbnb_price_model.joblib` — generated local model artifact; ignored
  by Git and not added to source control.

## Evaluation

The run used all 74,111 rows, with an 80/20 split using random seed 42:
59,288 training rows and 14,823 test rows. The target is natural-log
`log_price`, so user-facing prices and price-based metrics use `exp(log_price)`.

| Model | MAE (USD) | RMSE (USD) | R² (`log_price` scale) |
|---|---:|---:|---:|
| Median-log-price baseline | 88.71 | 178.69 | -0.014976 |
| Linear Regression | 61.70 | 133.97 | 0.563957 |

MAE/RMSE compare test prices in USD after inverse-transforming predictions.
R² is calculated against log-price targets and is not an accuracy percentage.
These are measured held-out results, not hardcoded model claims.

The pipeline reloaded successfully and returned **$59.13/night** for a complete
real held-out listing row. Its prediction matched the in-memory model.

## Commands executed

Run these from this project directory:

```bash
python3 -m nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 Airbnb_Price_Prediction.ipynb
python3 -m src.train
python3 -m src.predict_price
python3 -m unittest discover -s tests -v
```

Additional verification:

- `nbformat.validate` — passed; no saved notebook cell errors.
- `git diff --check` — passed.
- Dataset integrity check — unchanged at 101,546,498 bytes with SHA-256
  `ff0b0e3ccc3cda4213ae5621e55b4933afd009ba35f49b31af06543ea5b00bff`.
- Test result — **12 tests passed**, including a fresh Python process loading
  the model, prediction validation, missing/invalid inputs, missing dataset or
  model files, and feature ordering.

The `jupyter` executable was not on `PATH`; running nbconvert as a Python
module worked. An initial notebook execution exposed a stale amenity-column
reference; it was fixed before the successful full execution. No unresolved
training, notebook, or test errors remain.

## Commands to use

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.train
python -m src.predict_price
python -m unittest discover -s tests -v
```

Keep the original Kaggle `train.csv` in this directory. Training creates or
replaces the generated model under `models/`, but does not write to the dataset.
Run `python -m src.predict_price` to enter listing details interactively. The
backend can load the artifact once with `src.predict_price.load_model()` and
call `src.predict_price.predict_price(listing, model)` for validated
predictions.

## Remaining scope and limitations

- A Flask API and frontend are not part of this ML verification task. The
  prediction helper is ready to be loaded once by a backend.
- Estimates represent historical Kaggle listing prices, not current market
  demand or guaranteed achievable rates.
- The source CSV and generated model are local and intentionally ignored by
  Git. Train the model before running tests in a fresh checkout.
- The separate AB_NYC_2019 experiment under `College_Notes/airbnb-prediction`
  remains unchanged and is not used by this Kaggle training pipeline.
