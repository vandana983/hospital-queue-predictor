"""
Builds wait_time_model.pkl using whatever pandas/scikit-learn version is
installed in THIS environment -- run this after installing requirements.txt
(or as a Docker build step) so the pickled model always matches the
scikit-learn version that will actually load it. Shipping a .pkl built in a
different environment is exactly how you get
"InconsistentVersionWarning" / "No module named '_loss'" errors.

This mirrors ml_model/train.py's logic but is self-contained (no import
from ../ml_model) so it works from inside a Docker build context that only
has the backend/ folder available.
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

HERE = Path(__file__).parent
RNG = np.random.default_rng(42)
N = 6000
APPOINTMENT_TYPES = ["general", "specialist", "followup", "emergency"]
BASE_CONSULT = {"general": 15, "specialist": 22, "followup": 10, "emergency": 8}
TYPE_WEIGHTS = [0.55, 0.20, 0.20, 0.05]
FEATURES = ["queue_size", "doctors_available", "appointment_type",
            "hour_of_day", "day_of_week", "is_emergency", "historical_consult_minutes"]


def generate(n=N) -> pd.DataFrame:
    appointment_type = RNG.choice(APPOINTMENT_TYPES, size=n, p=TYPE_WEIGHTS)
    queue_size = RNG.integers(0, 25, size=n)
    hour_of_day = RNG.integers(8, 20, size=n)
    day_of_week = RNG.integers(0, 7, size=n)
    is_emergency = (appointment_type == "emergency").astype(int)
    doctors_available = np.clip(RNG.integers(1, 4, size=n) + (queue_size // 8), 1, 6)
    base_consult = np.array([BASE_CONSULT[t] for t in appointment_type])
    historical_consult_minutes = np.clip(RNG.normal(base_consult, 3.0), 5, None)
    is_peak_hour = ((hour_of_day >= 9) & (hour_of_day <= 12)) | ((hour_of_day >= 16) & (hour_of_day <= 18))
    is_weekday = day_of_week < 5
    congestion = 1 + 0.18 * is_peak_hour + 0.08 * is_weekday
    raw_wait = (queue_size / doctors_available) * historical_consult_minutes * congestion
    raw_wait = raw_wait * np.where(is_emergency == 1, 0.3, 1.0)
    noise = RNG.normal(0, raw_wait * 0.12 + 2)
    actual_waiting_minutes = np.clip(raw_wait + noise, 2, 180).round(1)
    return pd.DataFrame({
        "queue_size": queue_size, "doctors_available": doctors_available,
        "appointment_type": appointment_type, "hour_of_day": hour_of_day,
        "day_of_week": day_of_week, "is_emergency": is_emergency,
        "historical_consult_minutes": historical_consult_minutes.round(1),
        "actual_waiting_minutes": actual_waiting_minutes,
    })


def main():
    df = generate()
    X, y = df[FEATURES], df["actual_waiting_minutes"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), ["appointment_type"])],
                             remainder="passthrough")
    pipe = Pipeline([("pre", pre), ("model", GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=42))])
    pipe.fit(X_train, y_train)
    mae = mean_absolute_error(y_test, pipe.predict(X_test))
    print(f"Built wait_time_model.pkl in this environment -- test MAE: {mae:.1f} min")

    joblib.dump(pipe, HERE / "wait_time_model.pkl")


if __name__ == "__main__":
    main()
