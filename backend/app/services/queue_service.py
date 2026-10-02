"""
In-memory data store standing in for PostgreSQL during development.
Swap this module's storage for real DB queries (SQLAlchemy models) without
changing the route signatures -- routes only call the functions below.
"""
from datetime import datetime
from itertools import count
from app.models.schemas import Doctor, DoctorCreate, Patient, PatientRegister, QueueEntry
from app.services import ml_predictor

_doctor_ids = count(1)
_patient_ids = count(1)
_token_counter = count(1)

doctors: dict[int, Doctor] = {}
patients: dict[int, Patient] = {}
queue: list[QueueEntry] = []

AVG_CONSULT = {"general": 15, "specialist": 22, "followup": 10, "emergency": 8}


def seed():
    """Populate starter doctors so the API isn't empty on first run."""
    for name, specialty in [("Dr. Mehta", "General Medicine"), ("Dr. Iyer", "General Medicine")]:
        d = Doctor(id=next(_doctor_ids), name=name, specialty=specialty)
        doctors[d.id] = d


def available_doctor_count() -> int:
    return max(1, sum(1 for d in doctors.values() if d.is_available))


def add_doctor(payload: DoctorCreate) -> Doctor:
    d = Doctor(id=next(_doctor_ids), **payload.model_dump())
    doctors[d.id] = d
    return d


def predict_wait(queue_size: int, doctors_available: int, appointment_type: str) -> tuple[float, int]:
    """Delegates to the trained ML model (app/services/ml_predictor.py),
    which itself falls back to the old heuristic if the model file is missing."""
    return ml_predictor.predict(queue_size, doctors_available, appointment_type)


def register_patient(payload: PatientRegister) -> QueueEntry:
    patient = Patient(
        id=next(_patient_ids),
        name=payload.name,
        phone=payload.phone,
        appointment_type=payload.appointment_type,
        notes=payload.notes,
        registered_at=datetime.utcnow(),
    )
    patients[patient.id] = patient

    ahead = len([q for q in queue if q.status in ("waiting", "almost")])
    wait, _ = predict_wait(ahead, available_doctor_count(), payload.appointment_type)

    entry = QueueEntry(
        token=f"Q-{next(_token_counter):03d}",
        patient=patient,
        position=ahead + 1,
        estimated_wait_minutes=wait,
        status="waiting",
    )
    queue.append(entry)
    _recompute_positions()
    return entry


def get_queue_entry(token: str) -> QueueEntry | None:
    return next((q for q in queue if q.token == token), None)


def list_active_queue() -> list[QueueEntry]:
    """For the admin dashboard: everyone still waiting or in consultation, in order."""
    return [q for q in queue if q.status in ("waiting", "almost", "in_consultation")]


def _recompute_positions():
    """Recalculate position/wait for everyone still waiting, after any status change."""
    active = [q for q in queue if q.status in ("waiting", "almost")]
    for i, entry in enumerate(active):
        entry.position = i + 1
        wait, _ = predict_wait(i, available_doctor_count(), entry.patient.appointment_type)
        entry.estimated_wait_minutes = wait
        entry.status = "almost" if entry.position <= 2 else "waiting"


def update_status(token: str, status: str) -> QueueEntry | None:
    entry = get_queue_entry(token)
    if not entry:
        return None
    entry.status = status
    _recompute_positions()
    return entry


def cancel_entry(token: str) -> bool:
    entry = get_queue_entry(token)
    if not entry:
        return False
    entry.status = "cancelled"
    _recompute_positions()
    return True


def current_queue_snapshot() -> dict:
    waiting = [q for q in queue if q.status in ("waiting", "almost")]
    avg_wait, avg_consult = predict_wait(len(waiting), available_doctor_count(), "general")
    return {
        "patients_waiting": len(waiting),
        "doctors_available": available_doctor_count(),
        "avg_consult_minutes": avg_consult,
        "estimated_wait_minutes": avg_wait,
    }
