# Deployment Plan: AI-Powered Restaurant Recommendation System

> **Stack:** FastAPI (Python) backend · Next.js (React/TypeScript) frontend  
> **LLM:** Groq (`llama-3.3-70b-versatile`) · **Dataset:** HuggingFace `ManikaSaini/zomato-restaurant-recommendation`  
> **Backend Platform:** Railway · **Frontend Platform:** Vercel

---

## 1. Platform Recommendations (Free Tier)

| Layer | Platform | Free Tier | Why |
|---|---|---|---|
| **Backend** (FastAPI + Python) | **[Railway](https://railway.app)** ✅ | $5 free credit/month, always-on, no sleep | No cold starts, native Python, simple env vars, auto-deploys from GitHub |
| **Frontend** (Next.js) | **[Vercel](https://vercel.com)** ✅ | Unlimited personal projects, 100 GB bandwidth | Built by Next.js creators, zero-config, global CDN, preview URLs |
| Alternative Backend | [Render](https://render.com) | 750 hrs/month, sleeps after 15 min idle | Good fallback; has cold-start problem |
| Alternative Backend | [Fly.io](https://fly.io) | 3 VMs, 256 MB RAM each | Always-on but needs Docker config |
| Alternative Frontend | [Netlify](https://netlify.com) | 100 GB bandwidth, 300 build min/month | Good for static Next.js |

> **Chosen Combo: Railway (backend) + Vercel (frontend)**  
> Railway's free $5 credit keeps the service **always-on** (no cold-start sleep), and Vercel is purpose-built for Next.js.

---

## 2. Architecture Overview (Deployed)

```
User Browser
     |
     v
+---------------------------+
|   Vercel (Frontend)       |  <- Next.js App (SSR + CSR)
|   https://*.vercel.app    |     NEXT_PUBLIC_API_URL -> Railway
+------------+--------------+
             |  HTTPS POST /api/recommend
             |  HTTPS GET  /api/options
             |  HTTPS GET  /api/health
             v
+---------------------------+
|   Railway (Backend)       |  <- FastAPI + Uvicorn (Python 3.11)
|   https://*.railway.app   |     Always-on, auto-redeploys on git push
+------------+--------------+
             |
      +------+----------+
      |                 |
      v                 v
+----------+   +--------------------+
| Groq API |   | HuggingFace        |
| (LLM)    |   | Dataset (on start) |
+----------+   +--------------------+
```

---

## 3. Files Added for Deployment

| File | Purpose |
|---|---|
| `railway.toml` | Railway build & start config (nixpacks builder) |
| `Procfile` | Fallback start command for Railway |
| `.python-version` | Pins Python 3.11.9 for nixpacks |
| `requirements.txt` | Updated with version ranges for reproducible builds |
| `src/api/routes.py` | CORS updated to support `ALLOWED_ORIGINS` env var |
| `frontend/next.config.ts` | Comment added for `NEXT_PUBLIC_API_URL` setup |

---

## 4. Pre-Deployment Checklist

### 4.1 Backend
- [x] `railway.toml` created with start command and health check
- [x] `Procfile` created as fallback
- [x] `.python-version` pinned to `3.11.9`
- [x] `requirements.txt` updated with version ranges
- [x] CORS updated to read `ALLOWED_ORIGINS` from env var
- [x] Health check endpoint at `GET /api/health` -> `{"status": "ok"}`
- [x] `.env` is in `.gitignore` — no secrets in repo

### 4.2 Frontend
- [x] `lib/api.ts` already reads `NEXT_PUBLIC_API_URL || "http://localhost:8000"`
- [x] No hardcoded `localhost` URLs other than the fallback default
- [ ] `npm run build` passes locally (verify before pushing)
- [ ] `NEXT_PUBLIC_API_URL` env var set in Vercel project settings

### 4.3 GitHub Repository
- [x] Repo: `https://github.com/singhkarmveer1010/Ai-restaurant-recommender`
- [x] All deployment config files committed and pushed to `main`

---

## 5. Backend Deployment — Railway

### 5.1 Create Railway Account & Project

1. Go to [railway.app](https://railway.app) -> **Sign up with GitHub**
2. Click **New Project** -> **Deploy from GitHub repo**
3. Select `singhkarmveer1010/Ai-restaurant-recommender`
4. Railway auto-detects Python via `nixpacks` and picks up `railway.toml`

### 5.2 Railway Configuration (already committed to repo)

**`railway.toml`** (repo root):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

**`.python-version`**:
```
3.11.9
```

**`Procfile`** (fallback):
```
web: uvicorn src.api.routes:app --host 0.0.0.0 --port $PORT
```

### 5.3 Set Environment Variables in Railway

In Railway project -> **Variables** tab:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | `gsk_your_actual_groq_api_key` |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `GROQ_TEMPERATURE` | `0.3` |
| `MAX_CANDIDATES` | `20` |
| `TOP_K` | `5` |
| `DATASET_CACHE_PATH` | `/tmp/restaurants_cache.json` |
| `ALLOWED_ORIGINS` | *(leave blank now — set after Vercel URL is known)* |

> **IMPORTANT:** `GROQ_API_KEY` must be set in Railway's Variables UI. Never commit it to the repo.

> **TIP:** `DATASET_CACHE_PATH=/tmp/restaurants_cache.json` caches the HuggingFace dataset to disk on first run, speeding up subsequent starts.

### 5.4 Note Your Backend URL

After deployment, Railway provides a URL like:
```
https://ai-restaurant-recommender-production.up.railway.app
```
Copy this — it is needed as the Vercel `NEXT_PUBLIC_API_URL`.

---

## 6. Frontend Deployment — Vercel

### 6.1 Import Project into Vercel

1. Go to [vercel.com](https://vercel.com) -> **Sign up with GitHub**
2. Click **Add New -> Project**
3. Import `singhkarmveer1010/Ai-restaurant-recommender`
4. Configure build settings:

| Setting | Value |
|---|---|
| **Framework Preset** | `Next.js` (auto-detected) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `.next` |

### 6.2 Set Environment Variables in Vercel

In Vercel project -> **Settings -> Environment Variables**:

| Key | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://ai-restaurant-recommender-production.up.railway.app` | Production, Preview |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Development |

### 6.3 Deploy

Click **Deploy**. Vercel:
1. Runs `npm install` inside `frontend/`
2. Runs `npm run build`
3. Deploys to a global CDN edge network

Your frontend URL:
```
https://ai-restaurant-recommender.vercel.app
```

---

## 7. Post-Deployment: Lock Down CORS

After getting your Vercel URL, go to **Railway -> Variables** and add:

```
ALLOWED_ORIGINS=https://ai-restaurant-recommender.vercel.app,http://localhost:3000
```

This tightens CORS to only allow your frontend. Railway restarts the service automatically — no code change needed.

---

## 8. Verification

### 8.1 Backend Endpoints (Railway)

```bash
# Health check
curl https://ai-restaurant-recommender-production.up.railway.app/api/health
# Expected: {"status":"ok"}

# Filter options (tests dataset loading)
curl https://ai-restaurant-recommender-production.up.railway.app/api/options
# Expected: {"locations":[...],"cuisines":[...]}

# Full recommendation (tests Groq LLM pipeline)
curl -X POST https://ai-restaurant-recommender-production.up.railway.app/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"location":"Banashankari","budget":"medium","min_rating":3.5}'
# Expected: {"summary":"...","recommendations":[...],"metadata":{...}}
```

### 8.2 Frontend Checklist (Vercel)

- [ ] Homepage loads at `https://ai-restaurant-recommender.vercel.app`
- [ ] Location & cuisine dropdowns populate (calls Railway `/api/options`)
- [ ] Form submission returns AI-ranked restaurant cards
- [ ] Loading spinner displays during API call
- [ ] No CORS errors in browser DevTools
- [ ] Mobile layout is responsive

---

## 9. Cost Summary

| Service | Plan | Monthly Cost |
|---|---|---|
| Railway (backend) | Free $5 credit (~500 hrs) | **$0** |
| Vercel (frontend) | Hobby (free) | **$0** |
| Groq API | Free tier (14,400 req/day) | **$0** |
| HuggingFace Dataset | Public dataset | **$0** |
| **Total** | | **$0 / month** |

> Railway's $5/month credit resets every month and is more than enough for a personal/portfolio project.

---

## 10. Troubleshooting

| Issue | Likely Cause | Fix |
|---|---|---|
| Railway: `ModuleNotFoundError: src` | Start command wrong directory | Confirm `railway.toml` `startCommand` runs from repo root |
| `500` on `/api/recommend` | Missing `GROQ_API_KEY` | Add in Railway Variables tab |
| CORS error in browser console | `ALLOWED_ORIGINS` not set | Add Vercel URL to `ALLOWED_ORIGINS` in Railway Variables |
| Dataset download fails / slow | HuggingFace timeout on first boot | Wait 2-3 min; `DATASET_CACHE_PATH` avoids re-downloading |
| Vercel build fails (TS error) | TypeScript compilation error | Run `npm run build` in `frontend/` locally first |
| Vercel build fails (wrong root) | Root directory not set to `frontend` | Vercel project settings -> Root Directory -> `frontend` |
| Dropdowns empty on frontend | Can't reach Railway API | Verify `NEXT_PUBLIC_API_URL` in Vercel env vars |
| `422 Unprocessable Entity` | Pydantic schema mismatch | Check request body vs `UserPreferences` in `src/api/models.py` |

---

## 11. Auto-Redeploy Workflow

Both platforms redeploy on every push to `main`:

```bash
git add .
git commit -m "feat: update something"
git push origin main
# Railway rebuilds and redeploys the backend automatically
# Vercel rebuilds and redeploys the frontend automatically
```

---

*Last updated: 2026-07-02 · Repo: github.com/singhkarmveer1010/Ai-restaurant-recommender*
