from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

AppointmentType = Literal["general", "specialist", "followup", "emergency"]


class Doctor(BaseModel):
    id: int
    name: str
    specialty: str
    is_available: bool = True
    avg_consult_minutes: int = 15


class DoctorCreate(BaseModel):
    name: str
    specialty: str
    avg_consult_minutes: int = 15


class Patient(BaseModel):
    id: int
    name: str
    phone: str
    appointment_type: AppointmentType
    notes: Optional[str] = None
    registered_at: datetime


class PatientRegister(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(pattern=r"^[0-9]{10}$")
    appointment_type: AppointmentType = "general"
    notes: Optional[str] = None


class QueueEntry(BaseModel):
    token: str
    patient: Patient
    position: int
    estimated_wait_minutes: float
    status: Literal["waiting", "almost", "in_consultation", "done", "cancelled"] = "waiting"


class PredictionRequest(BaseModel):
    queue_size: int = Field(ge=0)
    doctors_available: int = Field(ge=1)
    appointment_type: AppointmentType = "general"


class PredictionResponse(BaseModel):
    model_config = {"protected_namespaces": ()}  # "model_used" is our field name, not pydantic's reserved "model_*"

    estimated_wait_minutes: float
    avg_consult_minutes: int
    model_used: str = "heuristic-v0"  # becomes "random_forest_v1" etc. after Day 4
