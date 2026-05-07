# AI Travel Planner — Monorepo

A multi-agent system that turns a short, natural-language travel request into a
complete, budget-aware, day-by-day itinerary.

This repository follows a **domain-driven monorepo layout**:

| Area | Path | Stack | Status |
|---|---|---|---|
| **API service** (deployable) | [`apps/api/`](apps/api/) | FastAPI entrypoint, editable installs of every package, CI, `data/`, `scripts/` | Live |
| **Web client** (deployable) | [`apps/web/`](apps/web/) | Next.js 14 + Tailwind | Live |
| **Platform** | [`packages/platform/`](packages/platform/) | Typed config, structured logging, correlation IDs, FastAPI app factory, health/readiness (Python module: `app_platform`) | Done |
| **Domain contracts** | [`packages/domain_contracts/`](packages/domain_contracts/) | Pydantic schemas — `TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport`, `Itinerary`, `RevisionRequest` | Done |
| **Orchestrator** | [`packages/orchestrator/`](packages/orchestrator/) | Trip-request parser, LangGraph state graph, `Agent` base contract | Done |
| **Tools** | [`packages/tools/`](packages/tools/) | Typed tool layer with retries, caching, real-timeout, `ToolRegistry` | Done |
| **Agents** | [`packages/agents/`](packages/agents/) | One package per capability: `destination`, `logistics`, `budget`, `synthesis`, `validator`, `repair` | Done |
| **Memory** | [`packages/memory/`](packages/memory/) | Run-state store, planner-result cache (TTL/LRU), user-preference profile, `MemoryAwarePlanner` | Done |
| **Reliability** | [`packages/reliability/`](packages/reliability/) | `ModelTierPolicy`, `with_retry`, `CircuitBreaker`, `HardenedPlannerService` | Done |
| **Docs** | [`docs/`](docs/) | Problem statement, architecture, plan, changelog, file map | — |

> **Example input:** *"Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds."*  
> **Output:** validated day-by-day itinerary with neighbourhoods, transport, and budget.

---

## Documentation

| Doc | Purpose |
|---|---|
| [`docs/problemStatement.md`](docs/problemStatement.md) | Original problem statement |
| [`docs/architecture.md`](docs/architecture.md) | Reference architecture |
| [`docs/implementationPlan.md`](docs/implementationPlan.md) | Phase-wise delivery plan |
| [`docs/deployment-foundation.md`](docs/deployment-foundation.md) | Staging-first deployment runbook |
| [`docs/supabase-usage-setup.md`](docs/supabase-usage-setup.md) | SQL setup for persisted daily usage limits |
| [`docs/projectFileMap.md`](docs/projectFileMap.md) | Interview-friendly file map |
| [`docs/CHANGELOG.md`](docs/CHANGELOG.md) | Version history |

---

## Quick start

### API (Python / FastAPI)

```bash
cd apps/api
python -m venv .venv
# macOS / Linux:  source .venv/bin/activate
# Windows:        .venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt
cp ../../packages/platform/.env.example .env   # optional; tests use safe defaults

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

From the **repository root** (with GNU Make):

```bash
make api-dev
```

API: http://localhost:8000/docs

### Web (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

UI: http://localhost:3000  (env template: `apps/web/.env.local.example`)

### Git hooks (once per clone)

Pre-commit is configured at the **repo root** so it can see `apps/` and `packages/`:

```bash
pip install pre-commit
pre-commit install
```

---

## Root Makefile shortcuts

| Target | Action |
|---|---|
| `make api-dev` | Run FastAPI with reload |
| `make api-check` | Ruff + mypy + pytest (same as CI) |
| `make api-test` | Pytest only |
| `make web-dev` | Next.js dev server |
| `make hooks` | `pre-commit install` |

---

## Project layout

```text
Multi-agentic-system/
├── apps/
│   ├── api/                       # FastAPI service (uvicorn entrypoint, integration tests)
│   │   ├── app/main.py
│   │   ├── app/api/               # domain HTTP routers (e.g. trip_planning.py)
│   │   ├── tests/                 # wiring / integration tests
│   │   └── requirements*.txt      # editable installs of every packages/* below
│   └── web/                       # Next.js 14 + Tailwind UI
├── packages/
│   ├── platform/                  # app_platform — config, logging, app factory, health
│   ├── domain_contracts/          # Pydantic schemas (single source of truth)
│   ├── orchestrator/              # parser + LangGraph + Agent base contract
│   ├── tools/                     # typed tool layer + ToolRegistry
│   ├── agents/                    # one package per capability:
│   │   ├── destination/           #   research worker
│   │   ├── logistics/             #   stay/transit planner
│   │   ├── budget/                #   cost estimator
│   │   ├── synthesis/             #   day-by-day itinerary stitcher
│   │   ├── validator/             #   hard-rule checker
│   │   └── repair/                #   bounded revision loop
│   ├── memory/                    # run-state, cache, preference profile
│   └── reliability/               # tier policy, retry, circuit breaker, hardened planner
├── docs/
├── .github/workflows/
├── Makefile
└── README.md
```

Every `packages/*` directory is a self-contained Python project with its own
`pyproject.toml`, `src/`, `tests/`, and `README.md`. The phase-wise build narrative
(Phases 0–10) lives in `docs/implementationPlan.md`; the code is organised by domain.

---

## Current delivery status

| Phase | Goal | Lives at | State |
|---|---|---|---|
| **0** | Project foundation | `packages/platform/` | Done |
| 1 | Schemas + orchestrator skeleton | `packages/domain_contracts/`, `packages/orchestrator/` | Done |
| 2 | Tool layer (typed errors, retries, cache, real-timeout) | `packages/tools/` | Done |
| 3 | Destination research agent | `packages/agents/destination/` | Done |
| 4 | Logistics agent | `packages/agents/logistics/` | Done |
| 5 | Budget agent + itinerary synthesis | `packages/agents/budget/`, `packages/agents/synthesis/` | Done |
| 6 | Validator agent | `packages/agents/validator/` | Done |
| 7 | Repair loop | `packages/agents/repair/` | Done |
| 8 | Web UI + trip planning API | `apps/web/`, `apps/api/app/api/trip_planning.py` | Done |
| 9 | Memory + personalization | `packages/memory/` | Done |
| 10 | Production hardening | `packages/reliability/` | Done |

See [`docs/implementationPlan.md`](docs/implementationPlan.md) for the full plan plus the
edge-case hardening status update.

---

## License

MIT.
