# Frontend — Phase 8

Next.js + Tailwind implementation of the planner interface.

## What is implemented

- Request form and submit flow
- Agent status cards (research, budget, preference)
- Itinerary detail view with day-by-day cards
- Budget insight panel and validation feedback panel
- API wiring to backend route `POST /api/v1/trips/plan`
- Correlation ID display from response headers

## Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Default URL: `http://localhost:3000`

Backend base URL is read from:
- `NEXT_PUBLIC_API_BASE_URL` (preferred)
- `NEXT_PUBLIC_API_URL` (fallback for compatibility)
# frontend/

Next.js + Tailwind UI for the AI Travel Planner. Lives alongside the Python API in **`backend/`** at the repository root.

**Phase:** 8  
**Status:** placeholder until the app is scaffolded.

## Environment

Copy the example env file before implementing API calls:

```bash
cp .env.local.example .env.local
```

`NEXT_PUBLIC_API_URL` should point at the FastAPI server (default `http://localhost:8000` when you run `make backend-dev` or `uvicorn` from `backend/`).

## Planned features

See `docs/implementationPlan.md` §10:

* Single-page input and “Plan my trip”
* Live progress via Server-Sent Events from `/trips/{id}/events`
* Day-by-day accordion with budget breakdown
* “Replay this run” and “Save as PDF”

## Bootstrap (Phase 8)

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir
```
