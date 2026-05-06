# Deployment Foundation (Phase -1)

This runbook sets up staging first, then production, using:
- Vercel for `apps/web`
- Render for `apps/api`
- Supabase for auth/data baseline
- Cloudflare for DNS
- Resend reserved for Phase V2.E

## 1) Prerequisites

- GitHub repo connected and push access working
- Accounts created: Vercel, Render, Supabase, Cloudflare, Resend
- Local sanity check passing:
  - API: `http://localhost:8000/healthz`
  - Web: `http://localhost:3000`

## 2) Deploy API to Render (staging first)

1. In Render, create Blueprint deployment from repo root.
2. Use `render.yaml` from repository root.
3. Deploy `planora-api-staging` service first.
4. In service environment variables, set:
   - `API_CORS_ORIGINS` = staging Vercel URL
5. Keep `MOCK_MODE=true`.
6. Verify:
   - `<staging-api-url>/healthz`
   - `<staging-api-url>/readyz`

Smoke command:
```bash
python apps/api/scripts/release_smoke.py <staging-api-url>
```

## 3) Deploy Web to Vercel (staging)

1. Import repo in Vercel.
2. Set root directory to `apps/web`.
3. Vercel will pick up `apps/web/vercel.json`.
4. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = staging Render API URL
   - `NEXT_PUBLIC_API_BASE_URL` = staging Render API URL
5. Deploy preview/staging.
6. Confirm web can call API plan endpoint and health-related UI loads.

## 4) Supabase baseline (optional in Phase -1, recommended)

1. Create project for staging.
2. Capture values:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY` (API only; never frontend)
3. Add keys to API/Web env only if auth features are being validated in staging.

## 5) Promote to production

1. Deploy `planora-api-prod` in Render (defined in `render.yaml`).
2. Create Vercel production deployment for web.
3. Configure production env variables separately from staging.
4. Point domain via Cloudflare DNS.
5. Re-run smoke against production API:

```bash
python apps/api/scripts/release_smoke.py <prod-api-url>
```

## 6) Guardrails (must keep)

- Keep `MOCK_MODE=true` for Phase -1 and V2.A.
- Keep paid provider keys unset.
- Separate staging and production secrets.
- Do not start V2.B provider integrations before V2.A completion.
