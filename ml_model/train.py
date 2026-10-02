"""
Trains and compares candidate regression models for wait-time prediction,
then saves the best one to trained_models/wait_time_model.pkl.

Run:
    cd ml_model
    python train.py

Note: xgboost is listed as a candidate in the project spec but isn't
installed here (no network access in this environment). GradientBoostingRegressor
(scikit-learn's built-in boosting model) stands in for it below -- swap it for
XGBRegressor later with `pip install xgboost` if you want to compare against it.
"""
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from generate_data import generate

HERE = Path(__file__).parent
FEATURES = ["queue_size", "doctors_available", "appointment_type",
            "hour_of_day", "day_of_week", "is_emergency", "historical_consult_minutes"]
TARGET = "actual_waiting_minutes"
CATEGORICAL = ["appointment_type"]
NUMERIC = [f for f in FEATURES if f not in CATEGORICAL]


def build_pipeline(model):
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ], remainder="passthrough")
    return Pipeline([("pre", pre), ("model", model)])


def evaluate(pipeline, X_test, y_test):
    preds = pipeline.predict(X_test)
    return {
        "MAE_minutes": round(mean_absolute_error(y_test, preds), 2),
        "RMSE_minutes": round(np.sqrt(mean_squared_error(y_test, preds)), 2),
        "R2": round(r2_score(y_test, preds), 4),
    }


def main():
    df = generate()
    df.to_csv(HERE / "data" / "synthetic_queue_data.csv", index=False)

    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    candidates = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
        "gradient_boosting": GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42),
    }

    results = {}
    pipelines = {}
    for name, model in candidates.items():
        pipe = build_pipeline(model)
        pipe.fit(X_train, y_train)
        results[name] = evaluate(pipe, X_test, y_test)
        pipelines[name] = pipe
        print(f"{name:20s} -> {results[name]}")

    best_name = min(results, key=lambda k: results[k]["MAE_minutes"])
    best_pipeline = pipelines[best_name]
    print(f"\nBest model: {best_name} (lowest MAE)")

    trained_dir = HERE / "trained_models"
    trained_dir.mkdir(exist_ok=True)
    joblib.dump(best_pipeline, trained_dir / "wait_time_model.pkl")
    joblib.dump(FEATURES, trained_dir / "feature_list.pkl")

    with open(trained_dir / "metrics.json", "w") as f:
        json.dump({"results": results, "best_model": best_name}, f, indent=2)

    print(f"Saved: {trained_dir / 'wait_time_model.pkl'}")


if __name__ == "__main__":
    main()
