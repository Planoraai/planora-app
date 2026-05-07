# Weekly Release Cadence

This project follows a weekly release train from `develop` to `main`.

## Cadence

- **Mon-Tue:** feature work merged into `develop`
- **Wed:** stabilization and bug fixes on `develop`
- **Thu:** release candidate validation on staging
- **Fri:** promotion PR `develop -> main` and production smoke checks

## Roles

- **Release Driver (weekly):** owns release PR and go/no-go
- **Reviewer:** validates test evidence and rollback readiness
- **Deployer:** runs production promotion checklist

One person can fill all roles when solo, but keep the checklist discipline.

## Release PR requirements

- Base: `main`
- Compare: `develop`
- Must include:
  - scope summary
  - known risks
  - test evidence (staging)
  - rollback plan links

## Go/No-Go Criteria

Release is **GO** only if:
- staging smoke checks pass
- auth flow is stable
- planner API from web works
- no unresolved P1/P2 bugs

Otherwise mark **NO-GO**, fix on `develop`, and retry next window.

## Hotfix path

For production incidents:
- branch from `main`: `hotfix/<short-description>`
- PR directly to `main`
- after merge, back-merge `main -> develop`
