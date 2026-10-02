"""
Loads the Day-4 trained model and exposes predict(). Falls back to the
simple heuristic if the model file is missing or fails to load, so the API
never crashes just because the .pkl wasn't copied over.
"""
from pathlib import Path
from datetime import datetime
import pandas as pd

MODEL_PATH = Path(__file__).parent.parent / "ml" / "wait_time_model.pkl"
AVG_CONSULT = {"general": 15, "specialist": 22, "followup": 10, "emergency": 8}

_model = None
_load_attempted = False


def _get_model():
    global _model, _load_attempted
    if not _load_attempted:
        _load_attempted = True
        try:
            import joblib
            _model = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"[ml_predictor] Could not load trained model, using heuristic fallback: {e}")
            _model = None
    return _model


def _heuristic(queue_size: int, doctors_available: int, appointment_type: str) -> tuple[float, int]:
    avg_consult = AVG_CONSULT[appointment_type]
    wait = (queue_size / max(1, doctors_available)) * avg_consult
    if appointment_type == "emergency":
        wait = max(5, wait * 0.3)
    return round(wait, 1), avg_consult


def predict(queue_size: int, doctors_available: int, appointment_type: str) -> tuple[float, int]:
    """Returns (estimated_wait_minutes, avg_consult_minutes)."""
    avg_consult = AVG_CONSULT[appointment_type]
    model = _get_model()
    if model is None:
        return _heuristic(queue_size, doctors_available, appointment_type)

    now = datetime.now()
    row = pd.DataFrame([{
        "queue_size": queue_size,
        "doctors_available": doctors_available,
        "appointment_type": appointment_type,
        "hour_of_day": now.hour,
        "day_of_week": now.weekday(),
        "is_emergency": 1 if appointment_type == "emergency" else 0,
        "historical_consult_minutes": avg_consult,
    }])
    try:
        raw = float(model.predict(row)[0])
        wait = round(max(2.0, min(raw, 180.0)), 1)  # clip to physical bounds, see Day 4 notes
        return wait, avg_consult
    except Exception as e:
        print(f"[ml_predictor] Prediction failed, using heuristic fallback: {e}")
        return _heuristic(queue_size, doctors_available, appointment_type)


def model_name() -> str:
    return "gradient_boosting_v1" if _get_model() is not None else "heuristic-fallback"
