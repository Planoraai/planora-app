# Planora Student Zero-Cost Guide

**Scope:** local / learning / zero-variable-cost runs only. For **one clear production direction** (deploy, user honesty, v2 order), read [COMPASS.md](./COMPASS.md) first.

This guide is the practical "$0 spend" path distilled from:
- `docs/implementationPlan.md`
- `docs/architecture.md`
- `docs/conciergeProductPlan.md`

## Goal

Run and test the current project without paying for LLM/API providers.

## Agreed Plan (Final)

We will use free tiers everywhere possible, and avoid paid APIs until there is real traction.

- Development now: run in `MOCK_MODE=true` (zero variable cost)
- Hosting later: free tiers only
- LLM later (when needed): free-tier-first providers only
- Student Pack perks: use them before any paid subscription

## Current Reality (Important)

- v1 (Phases 0-10) is delivered and already works in `MOCK_MODE=true`.
- Real-API mode is documented, but not required for student/no-budget usage.
- v2 concierge features in the product plan are proposed; most are not yet built.

## Zero-Cost Rules

1. Keep backend in mock mode: `MOCK_MODE=true`
2. Do not configure paid provider keys (OpenAI, Amadeus, Tavily, etc.)
3. Use local development run for both backend and frontend
4. Focus on product flow, UI, and logic validation first

## What You Need (Only Free)

- Python + pip
- Node.js + npm
- Local machine (Windows is fine)
- No paid API keys

Optional free services later (from product docs):
- Supabase free tier (auth + db)
- Vercel free tier (frontend hosting)
- Render free tier (backend hosting)
- Resend free tier (email, later phases)
- Cloudflare free (DNS/SSL, when deploying)

## Student Pack Activation Checklist

Since your GitHub Student Developer Pack is approved, prioritize this order:

1. Claim free `.me` domain (Namecheap, if available in your region)
2. Connect DNS to Cloudflare free
3. Claim Sentry student/free benefits (error monitoring)
4. Keep DigitalOcean credits as backup, not primary
5. Do not buy paid LLM/API plans yet

## Minimal Local Setup

### 1) Backend env

Create `apps/api/.env` from `apps/api/.env.example` and ensure:

```env
MOCK_MODE=true
API_HOST=0.0.0.0
API_PORT=8000
API_CORS_ORIGINS=http://localhost:3000
```

Leave paid keys empty:
- `OPENAI_API_KEY=`
- `ANTHROPIC_API_KEY=`
- `GOOGLE_API_KEY=`
- tool keys (`TAVILY_API_KEY`, `AMADEUS_API_KEY`, etc.)

### 2) Frontend env

Create `apps/web/.env.local` from `apps/web/.env.local.example` and ensure:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run Commands

### Backend

From `apps/api`:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

From `apps/web`:

```bash
npm run dev
```

Open:
- Frontend: `http://localhost:3000`
- Backend docs: `http://localhost:8000/docs`

## What You Can Test at $0

- End-to-end trip planning flow in mock mode
- Sign-in/sign-up UI and sign-out behavior
- Usage gating:
  - guest: 2 free plans
  - signed-in: 5 plans/day
- Responsive UI behavior
- API wiring between frontend and backend

## What Not To Do (If You Want $0)

- Do not set `MOCK_MODE=false`
- Do not add paid provider keys
- Do not start real external tool integrations

## If You Want Deployment at $0 (Later)

From the product plan's student-budget stack:
- Frontend: Vercel free
- Backend: Render free
- Auth/DB: Supabase free
- Email: Resend free
- Domain: free `.me` via GitHub Student Pack (or cheap domain later)

You can postpone this until local testing is stable.

## Free-Tier LLM Strategy (When You Move Beyond Mock)

Only after your mock-mode product flow is stable:

1. Start with free-tier model access (Gemini Flash free tier as documented in product plan)
2. Add strict daily caps (already aligned with your frontend policy)
3. Keep expensive providers disabled
4. Re-enable `MOCK_MODE=true` anytime costs or reliability become an issue

Important: while building core features, keep `MOCK_MODE=true` to preserve zero-cost development.

## Simple Decision

- If budget is zero: stay on `MOCK_MODE=true` and keep building.
- Only switch to real APIs when you are ready to pay and monitor costs.
