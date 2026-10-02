from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import doctors, queue, predict, auth, ws
from app.services import queue_service as svc

app = FastAPI(
    title="Hospital Queue & Waiting-Time Predictor API",
    version="0.1.0",
    description="Backend for QueueSense -- patients, doctors, queue tracking, wait-time prediction.",
)

# Allow the frontend (any origin during development) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctors.router)
app.include_router(queue.router)
app.include_router(predict.router)
app.include_router(auth.router)
app.include_router(ws.router)


@app.on_event("startup")
def startup():
    svc.seed()


@app.get("/")
def root():
    return {"status": "ok", "service": "hospital-queue-predictor-api"}
