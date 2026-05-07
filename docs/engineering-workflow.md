# Engineering Workflow (PR-First)

This project follows a release-safe workflow:

1. Create a feature branch from `main`
2. Implement one focused change
3. Open a PR
4. Validate checks + staging behavior
5. Merge to `main` only after review + green checks

## Branch naming

- `feat/<short-description>`
- `fix/<short-description>`
- `chore/<short-description>`
- `docs/<short-description>`

Examples:
- `feat/supabase-usage-persistence`
- `fix/auth-cors-origin`

## Rules

- Never push directly to `main`
- Keep PRs small and single-purpose
- Include test evidence in every PR
- If a change impacts deploy/runtime, include rollback notes

## PR checklist (minimum)

- Scope is clear and single-purpose
- CI checks pass
- Staging smoke tests pass
- No secrets committed
- Docs updated if behavior changed

## Staging validation checklist

- Web app loads
- API `/healthz` and `/readyz` are healthy
- Auth flow works (sign-up/sign-in/sign-out)
- Planner request succeeds from web
- No CORS or environment regression

## Production promotion checklist

- Merge PR to `main`
- Verify deployment starts with expected commit SHA
- Run production smoke tests:
  - Home loads
  - Auth flow works
  - Planner request succeeds
- Confirm observability/error logs are normal

## Rollback

- Re-deploy previous stable Vercel deployment
- Re-deploy previous stable Render deployment
- If needed, revert the merge commit in `main` with a new PR
