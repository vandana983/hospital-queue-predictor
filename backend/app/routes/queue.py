from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import PatientRegister, QueueEntry
from app.services import queue_service as svc
from app.routes.auth import require_staff

router = APIRouter(prefix="/queue", tags=["queue"])


@router.get("/status")
def queue_status():
    """Live snapshot for the homepage monitor widget. Public -- no auth."""
    return svc.current_queue_snapshot()


@router.get("/", response_model=list[QueueEntry])
def list_queue(staff: str = Depends(require_staff)):
    """Staff dashboard only: full active queue, in order."""
    return svc.list_active_queue()


@router.patch("/{token}/status", response_model=QueueEntry)
def set_status(token: str, status: str, staff: str = Depends(require_staff)):
    entry = svc.update_status(token, status)
    if not entry:
        raise HTTPException(status_code=404, detail="Token not found")
    return entry


@router.post("/register", response_model=QueueEntry)
def register(payload: PatientRegister):
    return svc.register_patient(payload)


@router.get("/track/{token}", response_model=QueueEntry)
def track(token: str):
    entry = svc.get_queue_entry(token)
    if not entry:
        raise HTTPException(status_code=404, detail="Token not found")
    return entry


@router.post("/cancel/{token}")
def cancel(token: str):
    ok = svc.cancel_entry(token)
    if not ok:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"cancelled": True}
