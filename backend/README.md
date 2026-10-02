# Backend (FastAPI)

In-memory data store for now (swap `app/services/queue_service.py` storage
for real PostgreSQL queries later without touching the routes).

## Run locally
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Then open http://127.0.0.1:8000/docs for interactive Swagger docs.

## Endpoints
- `GET  /queue/status` — live snapshot (queue size, doctors, avg wait) for the homepage monitor
- `POST /queue/register` — register a patient, returns a token + position + estimated wait
- `GET  /queue/track/{token}` — track a specific token
- `POST /queue/cancel/{token}` — cancel a token
- `GET  /doctors/` / `POST /doctors/` — list / add doctors
- `PATCH /doctors/{id}/availability` — toggle a doctor on/off duty
- `POST /predict/` — wait-time prediction (heuristic now, trained ML model from Day 4)

## Authentication (Day 7+)
Staff-only endpoints require a JWT from `/auth/login`.
```bash
curl -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
# -> {"access_token": "...", "token_type": "bearer"}

curl http://127.0.0.1:8000/queue/ -H "Authorization: Bearer <token_from_above>"
```
Protected: `GET /queue/`, `PATCH /queue/{token}/status`, `POST /doctors/`,
`PATCH /doctors/{id}/availability`. Public: everything patients need
(`/queue/status`, `/queue/register`, `/queue/track/{token}`, `/predict/`,
`GET /doctors/`).

Set a real `JWT_SECRET` environment variable before deploying anywhere
persistent -- without it, a new random secret is generated on every
restart, which invalidates all existing sessions (fine for local dev).

## Staff registration
`POST /auth/register` with `{"username", "password", "signup_code"}` creates
a new staff account (password hashed, never stored in plaintext) and
returns a session token, same as login. The signup code defaults to
`HOSPITAL-STAFF-2026` -- set a real one via the `STAFF_SIGNUP_CODE`
environment variable before deploying, and share it only with people your
hospital has actually hired.

## Real-time updates
`GET /ws/queue` is a WebSocket that pushes the live queue snapshot every 2
seconds. The homepage monitor connects here directly instead of polling
`/queue/status` on a timer.

## If you see "InconsistentVersionWarning" or the model won't load
This means the shipped `.pkl` was built with a different scikit-learn
version than the one you have installed -- pickled models are tied to the
exact library version. Rebuild it in your own environment:
```bash
cd backend
pip install -r requirements.txt
python app/ml/build_model.py
```
Docker builds do this automatically (see the Dockerfile) so this only
matters for manual/non-Docker setup.

## Staff registration (updated)
No signup code required anymore. `POST /auth/register` takes
`{"username", "password", "full_name", "role"}` where role is one of
`receptionist`, `nurse`, `doctor`, `admin`. Returns a session token
immediately, same as login. `GET /auth/me` (with a valid Bearer token)
returns the signed-in staff member's profile.
