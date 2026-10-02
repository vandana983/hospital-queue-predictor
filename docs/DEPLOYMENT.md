# Deploying QueueSense (Render + Netlify)

Two separate deployments: the FastAPI backend goes on **Render** (it's a
real server that needs to stay running), the static frontend goes on
**Netlify** (it's just HTML/CSS/JS, no server needed). Netlify alone can't
run the backend — it only serves static files.

## 1. Deploy the backend to Render

1. Push this project to a GitHub repo (Render deploys from Git).
2. Go to https://render.com → **New +** → **Blueprint**, connect the repo,
   and point it at `backend/render.yaml`. Render reads it automatically and
   creates the service (Docker build, free plan, auto-generated `JWT_SECRET`).
   - No blueprint? Create a **Web Service** manually instead: runtime
     "Docker", root directory `backend`, leave build/start commands as the
     Dockerfile's defaults.
3. Wait for the build to finish, then copy the URL Render gives you, e.g.
   `https://queuesense-backend.onrender.com`.
4. Confirm it's live: open `https://<your-url>/docs` in a browser.

**Free-tier note:** Render's free web services sleep after 15 minutes of
inactivity and take 30-60 seconds to wake up on the next request. Fine for
a portfolio demo, worth mentioning if a recruiter says "it's slow at first."

## 2. Point the frontend at the deployed backend

Open `frontend/public/app.html`, find this line near the top of the
`<script>` block:
```js
const API_BASE = 'http://127.0.0.1:8000';
```
Change it to your Render URL:
```js
const API_BASE = 'https://queuesense-backend.onrender.com';
```
This is the only change needed — everything else already calls `API_BASE`.

## 3. Deploy the frontend to Netlify

**Fastest way (no account setup beyond signing in):**
1. Go to https://app.netlify.com/drop
2. Drag the `frontend/public` folder onto the page.
3. Netlify gives you a live URL immediately, e.g. `random-name.netlify.app`.

**Git-connected way (auto-redeploys on push):**
1. Push to GitHub, go to Netlify → **Add new site** → **Import an existing project**.
2. Base directory: `frontend`. Netlify reads `netlify.toml` and publishes `public/` automatically.

## 4. Test the deployed version end-to-end

Open your Netlify URL and check:
- The connection badge on the homepage turns green ("Live") — confirms it reached Render.
- The estimator says "Predicted by gradient_boosting_v1" — confirms the real model answered.
- Register a patient, then sign in to the Staff dashboard (`admin` / `admin123`) and confirm it appears.

## 5. Before putting this on a resume/LinkedIn

- **Tighten CORS**: in `backend/app/main.py`, change
  `allow_origins=["*"]` to `allow_origins=["https://your-site.netlify.app"]`
  once you know your real frontend URL — `"*"` is fine for a quick demo,
  not for something you're showing off as production-minded.
- **Change the demo password**: `admin` / `admin123` is fine to leave for
  reviewers to try the dashboard, but say so explicitly in your README so
  it doesn't look like an oversight.
- **Put both live links in your README and resume** — a clickable demo
  beats a "clone and run" project every time for a first job search.
