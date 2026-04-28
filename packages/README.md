# `packages/` — Reusable Domain Capabilities

Every directory under `packages/` is a self-contained Python project with its own
`pyproject.toml`, `src/`, `tests/`, and `README.md`. They are installed editably
into `apps/api/` (see `apps/api/requirements.txt`) and can be unit-tested in
isolation.

## Layer map

| Package | Public Python module | Role | Origin |
|---|---|---|---|
| [`platform/`](platform/) | `app_platform` | FastAPI app factory, settings, logging, correlation IDs, `/healthz`/`/readyz` | Phase 0 |
| [`domain_contracts/`](domain_contracts/) | `domain_contracts` | Pydantic schemas: `TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport`, `Itinerary`, `RevisionRequest` | Phase 1 |
| [`orchestrator/`](orchestrator/) | `orchestrator` | Trip-request parser + LangGraph state graph + `Agent` base contract | Phase 1 |
| [`tools/`](tools/) | `tools` | Typed tool layer with retries, caching, real-timeout, `ToolRegistry` | Phase 2 |
| [`agents/`](agents/) | `agents.<capability>` | Worker agents (PEP-420 namespace) — see [`agents/README.md`](agents/README.md) | Phases 3–7 |
| [`memory/`](memory/) | `memory` | Run-state store, planner-result cache (TTL/LRU), user-preference profile, `MemoryAwarePlanner` | Phase 9 |
| [`reliability/`](reliability/) | `reliability` | `ModelTierPolicy`, `with_retry`, `CircuitBreaker`, `HardenedPlannerService` | Phase 10 |

## Dependency direction

Lower → upper, never the other way:

```text
       reliability
          │
        memory
          │
   ┌──────┴──────┐
   │             │
agents/*    orchestrator
   │             │
   └──────┬──────┘
        tools
          │
   domain_contracts
          │
       platform
```

`domain_contracts` is the single source of truth for cross-package types;
nothing under `packages/` imports from `apps/`.

## Adding a new package

1. Create `packages/<name>/` matching the layout of an existing sibling
   (e.g. `packages/tools/`).
2. Add an editable install line to `apps/api/requirements.txt` and a
   tests-path to `apps/api/pyproject.toml`.
3. Run `pip install -r requirements.txt` from `apps/api/` and `pytest -q`
   to verify wiring.

## Verify everything at once

```bash
cd ../apps/api
pytest -q          # 82+ tests across all packages
ruff check . ../../packages
```
