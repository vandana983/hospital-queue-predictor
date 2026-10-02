# Hospital Queue & Waiting-Time Predictor (QueueSense)

An AI/ML-based system that predicts patient waiting time at hospitals and
clinics, with patient-facing registration/tracking and a staff dashboard.

## What's built (Days 1-7)

| Day | What |
|---|---|
| 1 | Dark-theme, fully responsive frontend shell (single HTML/CSS/JS file) |
| 2 | Patient registration + queue-tracking pages, mobile nav |
| 3 | FastAPI backend — patients, doctors, queue endpoints (in-memory store) |
| 4 | ML model — synthetic data + trained Gradient Boosting regressor (MAE ~9 min, R² 0.92) |
| 5 | Integration — frontend calls the real backend, backend calls the real model |
| 6 | Staff dashboard (call in / mark done / cancel, doctor toggles) + browser notifications |
| 7 | Docker + docker-compose, this document |

## Folder structure
```
hospital-queue-predictor/
├── docker-compose.yml       ← run everything with one command
├── frontend/
│   ├── Dockerfile
│   └── public/app.html      ← the entire frontend (self-contained)
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          ← FastAPI entrypoint
│       ├── ml/wait_time_model.pkl   ← trained model, shipped in the image
│       ├── models/schemas.py
│       ├── routes/          ← doctors.py, queue.py, predict.py
│       └── services/        ← queue_service.py, ml_predictor.py
├── ml_model/                ← training pipeline (not needed to run the app)
│   ├── generate_data.py
│   ├── train.py
│   ├── predict_model.py
│   └── trained_models/
└── docs/
```

## Run with Docker (recommended)
Requires Docker Desktop installed and running.
```bash
cd hospital-queue-predictor
docker compose up --build
```
Then open:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

Stop with `docker compose down` (add `-v` to also clear volumes, though this
project doesn't use any — the in-memory queue resets on every restart either way).

## Run without Docker
See `backend/README.md` and `ml_model/README.md` for manual setup, or the
quick version:
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend — just double-click frontend/public/app.html, no server needed
```

## Known limitations / what's next
- **Storage**: the backend uses an in-memory Python list, not PostgreSQL as
  originally planned — everything resets when the server restarts. Swapping
  in real Postgres means replacing the storage in `queue_service.py` with
  SQLAlchemy queries; route signatures don't need to change.
- **Auth**: staff sign-in now uses a real backend-checked username/password
  (PBKDF2-hashed, not plaintext) and short-lived JWT session tokens — the
  password is never checked in the browser. The one demo account is
  `admin` / `admin123`, stored hashed in `auth_service.py`; swap
  `STAFF_USERS` for a real `staff` database table before real deployment,
  and set a `JWT_SECRET` environment variable in production instead of
  relying on the auto-generated fallback.
- **XGBoost**: the original proposal named XGBoost as a candidate model;
  this build used scikit-learn's GradientBoostingRegressor instead since
  xgboost couldn't be installed in the development sandbox (no network
  access there). Swapping it in is a small change in `ml_model/train.py`.
- **Notifications**: browser notifications only, as built. SMS/WhatsApp
  (from the original "Future Enhancements" list) would need a provider
  like Twilio wired into the backend.
- **Cloud deployment**: docker-compose covers running it anywhere Docker
  is available. Pushing the images to AWS/GCP (ECS, Cloud Run, etc.) is the
  remaining step for the "Deployment: Docker + AWS/GCP" line in the
  original proposal.
