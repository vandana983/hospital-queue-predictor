from fastapi import APIRouter
from app.models.schemas import PredictionRequest, PredictionResponse
from app.services import queue_service as svc
from app.services import ml_predictor

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    """Day 5: now backed by the trained Gradient Boosting model
    (app/ml/wait_time_model.pkl), with an automatic heuristic fallback
    if that file is ever missing."""
    wait, avg_consult = svc.predict_wait(
        payload.queue_size, payload.doctors_available, payload.appointment_type
    )
    return PredictionResponse(
        estimated_wait_minutes=wait,
        avg_consult_minutes=avg_consult,
        model_used=ml_predictor.model_name(),
    )
