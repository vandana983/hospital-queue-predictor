# ML Model

## Files
```
ml_model/
  generate_data.py        -> synthetic historical queue records
  train.py                -> trains + compares 3 models, saves the best
  predict_model.py        -> inference wrapper (used by backend on Day 5)
  data/synthetic_queue_data.csv
  trained_models/
    wait_time_model.pkl   -> trained scikit-learn pipeline (preprocessing + model)
    feature_list.pkl
    metrics.json
```

## Retrain
```bash
cd ml_model
pip install -r requirements.txt
python train.py
```

## Results (synthetic data, 6000 records, 80/20 split)
| Model              | MAE (min) | RMSE (min) | R²    |
|---------------------|-----------|------------|-------|
| Linear Regression    | 15.86     | 20.67      | 0.785 |
| Random Forest         | 9.45      | 13.20      | 0.912 |
| **Gradient Boosting** | **9.19**  | **12.47**  | **0.922** |

Gradient Boosting is selected automatically by `train.py` (lowest MAE) and
saved to `trained_models/wait_time_model.pkl`. On data with a median wait of
~60 minutes, this means predictions are typically off by under 10 minutes.

**Note on XGBoost:** the original proposal lists XGBoost as a candidate.
It isn't installed in this environment (no network access to `pip install`
it here). Scikit-learn's `GradientBoostingRegressor` — a very similar
gradient-boosted-trees algorithm — stands in for it. To compare against real
XGBoost later: `pip install xgboost`, then add `from xgboost import
XGBRegressor` as another candidate in `train.py`'s `candidates` dict.

**Known limitation (fixed):** the raw model can extrapolate to physically
impossible values (e.g. negative minutes) for rare feature combinations,
such as high-queue emergencies, which are under-represented in the training
data. `predict_model.py` clips output to `[2, 180]` minutes before returning
it — real deployments should keep this kind of physical sanity check
regardless of which model is used.
