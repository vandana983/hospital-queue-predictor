from fastapi import APIRouter, Depends
from app.models.schemas import Doctor, DoctorCreate
from app.services import queue_service as svc
from app.routes.auth import require_staff

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/", response_model=list[Doctor])
def list_doctors():
    """Public -- needed by the homepage/estimator, not just staff."""
    return list(svc.doctors.values())


@router.post("/", response_model=Doctor)
def create_doctor(payload: DoctorCreate, staff: str = Depends(require_staff)):
    return svc.add_doctor(payload)


@router.patch("/{doctor_id}/availability", response_model=Doctor)
def set_availability(doctor_id: int, is_available: bool, staff: str = Depends(require_staff)):
    doctor = svc.doctors[doctor_id]
    doctor.is_available = is_available
    return doctor
