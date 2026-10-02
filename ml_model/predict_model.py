"""
Loads the trained model once and exposes a simple predict() function.
Day 5 will import this from the backend's /predict route, replacing the
current heuristic in app/services/queue_service.py.
"""
from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).parent / "trained_models" / "wait_time_model.pkl"
_model = None


def _load():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def predict(queue_size: int, doctors_available: int, appointment_type: str,
            hour_of_day: int, day_of_week: int, historical_consult_minutes: float) -> float:
    model = _load()
    is_emergency = 1 if appointment_type == "emergency" else 0
    row = pd.DataFrame([{
        "queue_size": queue_size,
        "doctors_available": doctors_available,
        "appointment_type": appointment_type,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_emergency": is_emergency,
        "historical_consult_minutes": historical_consult_minutes,
    }])
    raw = float(model.predict(row)[0])
    # a wait time can never be negative or absurdly long -- clip to physical bounds
    # rather than trusting the model's raw extrapolation on rare feature combos
    return round(max(2.0, min(raw, 180.0)), 1)


if __name__ == "__main__":
    # quick manual check
    print(predict(12, 2, "general", 10, 1, 15))
    print(predict(3, 2, "emergency", 10, 1, 8))
