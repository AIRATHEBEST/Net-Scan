# NetScan v2.0 — Advanced Network Intelligence Platform

> **Beat Fing.** Real-time network scanning, device intelligence, security analysis, and multi-platform deployment.

[![CI](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/ci.yml/badge.svg)](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/ci.yml)
[![Frontend](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/frontend.yml/badge.svg)](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/frontend.yml)
[![Backend](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/backend.yml/badge.svg)](https://github.com/AIRATHEBEST/Net-Scan/actions/workflows/backend.yml)

---

## Architecture & Deployment Flow

```
GitHub (source of truth)
│
├── push to main
│   │
│   ├── .github/workflows/ci.yml          ← Full integration check (all PRs + main)
│   ├── .github/workflows/frontend.yml    ── Build → Vercel (Web PWA)
│   ├── .github/workflows/backend.yml     ── Test  → Railway (FastAPI)
│   ├── .github/workflows/agent.yml       ── Build → Docker Hub (netscan-agent)
│   └── .github/workflows/mobile.yml      ── EAS Build → Expo (iOS / Android)
│
├── src/                    React + TypeScript frontend (Vite)
├── backend/                FastAPI backend (Python 3.11)
├── netscan-agent/          Lightweight network agent (Docker)
├── app.json / eas.json     Expo mobile app
├── docker-compose.yml      Local full-stack development
└── railway.json            Railway deployment config
```

### Live Services

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend (Web / PWA) | Vercel | https://netscantemp.vercel.app |
| Backend API | Railway | https://netscan-api-production.up.railway.app |
| API Docs (Swagger) | Railway | https://netscan-api-production.up.railway.app/docs |

---

## Quick Start (Local Development)

### Option A — Docker Compose (recommended)

```bash
git clone https://github.com/AIRATHEBEST/Net-Scan.git
cd Net-Scan
cp backend/.env.example backend/.env   # fill in your DB / Redis URLs
docker-compose up -d
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### Option B — Manual

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # edit with your credentials
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

---

## GitHub Secrets Required

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Used by | Description |
|--------|---------|-------------|
| `VERCEL_TOKEN` | frontend.yml | Vercel personal access token |
| `VERCEL_ORG_ID` | frontend.yml | Vercel organisation ID |
| `VERCEL_PROJECT_ID` | frontend.yml | Vercel project ID |
| `VITE_API_URL` | frontend.yml | Railway backend URL |
| `RAILWAY_TOKEN` | backend.yml | Railway API token |
| `RAILWAY_SERVICE_ID` | backend.yml | Railway service ID |
| `DOCKERHUB_USERNAME` | agent.yml | Docker Hub username |
| `DOCKERHUB_TOKEN` | agent.yml | Docker Hub access token |
| `EXPO_TOKEN` | mobile.yml | Expo account token |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Axios, Recharts |
| Backend | Python 3.11, FastAPI, SQLAlchemy, asyncpg |
| Database | PostgreSQL (Neon) |
| Cache | Redis (Upstash) |
| Auth | JWT (python-jose) |
| Agent | Python, Scapy, aiohttp, Docker |
| Mobile | Expo / React Native |
| CI/CD | GitHub Actions |
| Hosting | Vercel (frontend) + Railway (backend) |

---

## API Reference

Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/token` | Login (returns JWT) |
| GET | `/api/networks` | List networks |
| POST | `/api/networks` | Create network |
| GET | `/api/devices` | List devices |
| POST | `/api/scan/network/{id}` | Start network scan |
| POST | `/api/security/scan/{id}` | Security scan device |
| WS | `/ws/updates` | Real-time scan updates |
| GET | `/health` | Health check |

---

## Network Agent

The `netscan-agent` is a lightweight Docker container that runs on any machine in your network and reports device data to the backend.

```bash
docker run -d \
  -e NETSCAN_API_URL=https://netscan-api-production.up.railway.app \
  -e NETSCAN_AGENT_KEY=your-agent-key \
  --network host \
  --cap-add NET_RAW \
  airathebest/netscan-agent:latest
```

---

## License

MIT License — see [LICENSE](LICENSE)

---

*Built with ❤️ by HyperDev*
