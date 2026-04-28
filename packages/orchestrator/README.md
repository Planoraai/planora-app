# `packages/orchestrator/` — Hub-and-spoke orchestration

Drives the run from a free-text user prompt to an approved itinerary.

## What lives here

| Module | Role |
|---|---|
| `parser.py` | `parse_trip_request(prompt) -> TripBrief` — turns free text into the typed brief contract |
| `graph.py` | `build_graph()`, `run_orchestrator()` — LangGraph state machine wiring every specialist agent (with a deterministic linear fallback when LangGraph isn't available) |
| `agents/base.py` | `Agent` ABC every specialist agent in `packages/agents/*` implements |
| `prompts/` | Versioned prompt templates referenced by `graph.py` |

## Verify

```bash
cd apps/api
pytest ../../packages/orchestrator/tests -q
```

Originally lived as `phases/phase1/src/phase1/{orchestrator,agents}/`.
