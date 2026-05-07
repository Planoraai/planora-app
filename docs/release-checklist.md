# Release Checklist

Use this before every production release.

## Pre-merge

- [ ] PR approved
- [ ] CI checks green
- [ ] Staging smoke checks complete
- [ ] Change notes added to PR

## Deploy

- [ ] Merged commit SHA is the one being deployed
- [ ] Vercel production deployment successful
- [ ] Render production deployment successful

## Post-deploy smoke

- [ ] Web homepage loads
- [ ] API `/healthz` returns `ok`
- [ ] API `/readyz` returns `ready`
- [ ] Sign-up / sign-in / sign-out work
- [ ] Planner request succeeds from production web

## Observability and rollback readiness

- [ ] Error rate normal after deploy window
- [ ] No major auth/API/CORS issues
- [ ] Previous stable deployment links captured for rollback
