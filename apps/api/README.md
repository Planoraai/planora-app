# `apps/api/` — FastAPI integration shell

This directory is the **deployable Python service**. Feature code does **not** live here:

- Platform layer (config, logging, app factory, `/healthz`, `/readyz`) — `../../packages/platform/`
- Domain contracts — `../../packages/domain_contracts/`
- Orchestrator (parser + LangGraph + `Agent` base) — `../../packages/orchestrator/`
- Tool layer — `../../packages/tools/`
- Worker agents — `../../packages/agents/{destination,logistics,budget,synthesis,validator,repair}/`
- Memory + personalization — `../../packages/memory/`
- Reliability + hardening — `../../packages/reliability/`

Here you **install dependencies**, run **`uvicorn`** + **`pytest`**, and keep shared assets (`data/`, `scripts/`).

## Layout

| Path | Role |
|---|---|
| `app/main.py` | ASGI entrypoint — composes the platform shell and mounts domain routers |
| `app/api/` | Domain HTTP routers (e.g. `trip_planning.py` for `/api/v1/trips/plan`) |
| `tests/` | API integration / wiring tests (unit tests for individual packages live next to those packages) |
| `requirements.txt` | Runtime deps **and** editable installs of every `packages/*` |
| `data/`, `scripts/` | Shared KB fixtures, CI helper scripts |

## Setup

From this directory (`apps/api/`):

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp ../../packages/platform/.env.example .env   # optional; tests use safe defaults
```

Install Git hooks **once from the repository root**:

```bash
cd ../.. && pre-commit install && cd apps/api
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# or: make dev
```

Open http://localhost:8000/docs

## Quality

```bash
make check          # ruff (api + packages) + mypy + pytest
# or: invoke check   (run from this directory)
```
