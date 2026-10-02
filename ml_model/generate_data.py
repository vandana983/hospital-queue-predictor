"""
Generates a synthetic dataset of historical queue records for training the
wait-time regression model. Replace this with a real data export (from the
PostgreSQL `queue_history` table) once the system has been live long enough
to have real records -- keep the same column names so train.py needs no changes.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N = 6000

APPOINTMENT_TYPES = ["general", "specialist", "followup", "emergency"]
BASE_CONSULT = {"general": 15, "specialist": 22, "followup": 10, "emergency": 8}
TYPE_WEIGHTS = [0.55, 0.20, 0.20, 0.05]  # emergencies are rarer


def generate(n=N) -> pd.DataFrame:
    appointment_type = RNG.choice(APPOINTMENT_TYPES, size=n, p=TYPE_WEIGHTS)
    queue_size = RNG.integers(0, 25, size=n)
    hour_of_day = RNG.integers(8, 20, size=n)          # clinic hours 8am-8pm
    day_of_week = RNG.integers(0, 7, size=n)            # 0=Mon ... 6=Sun
    is_emergency = (appointment_type == "emergency").astype(int)

    # hospitals roster more doctors when the queue is bigger, so the two are
    # correlated rather than independent -- avoids unrealistic 1-doctor/30-patient rows
    doctors_available = np.clip(
        RNG.integers(1, 4, size=n) + (queue_size // 8), 1, 6
    )

    # historical consult time varies per record around the type's baseline
    base_consult = np.array([BASE_CONSULT[t] for t in appointment_type])
    historical_consult_minutes = np.clip(
        RNG.normal(base_consult, 3.0), 5, None
    )

    # peak hours (9-12, 16-18) and weekdays add congestion
    is_peak_hour = ((hour_of_day >= 9) & (hour_of_day <= 12)) | ((hour_of_day >= 16) & (hour_of_day <= 18))
    is_weekday = day_of_week < 5
    congestion = 1 + 0.18 * is_peak_hour + 0.08 * is_weekday

    # core relationship: wait scales with queue ahead of you per doctor,
    # times how long each consult takes, times congestion -- with noise
    raw_wait = (queue_size / doctors_available) * historical_consult_minutes * congestion
    raw_wait = raw_wait * np.where(is_emergency == 1, 0.3, 1.0)  # emergencies fast-tracked
    noise = RNG.normal(0, raw_wait * 0.12 + 2)  # heteroscedastic noise
    # real clinics triage/reassign beyond ~3 hours, so cap the target there
    actual_waiting_minutes = np.clip(raw_wait + noise, 2, 180).round(1)

    return pd.DataFrame({
        "queue_size": queue_size,
        "doctors_available": doctors_available,
        "appointment_type": appointment_type,
        "hour_of_day": hour_of_day,
        "day_of_week": day_of_week,
        "is_emergency": is_emergency,
        "historical_consult_minutes": historical_consult_minutes.round(1),
        "actual_waiting_minutes": actual_waiting_minutes,
    })


if __name__ == "__main__":
    df = generate()
    df.to_csv("data/synthetic_queue_data.csv", index=False)
    print(f"Generated {len(df)} rows -> data/synthetic_queue_data.csv")
    print(df.head())
