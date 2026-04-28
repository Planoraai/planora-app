# `packages/agents/` — Worker Agent Capabilities

Each subdirectory is a self-contained Python package implementing one **worker agent**
in the orchestrator's hub-and-spoke graph (see `docs/architecture.md` §3–§7).

All capabilities share the same shape:

```text
packages/agents/<capability>/
├── pyproject.toml
├── README.md
├── src/agents/<capability>/
│   ├── __init__.py        # public re-exports (Agent class + build_*_agent factory)
│   └── agent.py           # behavior + tool wiring
└── tests/
    └── test_<capability>_agent.py
```

`agents/` itself is a **PEP-420 namespace package** — there is no `agents/__init__.py`.
Each capability is installed editably as its own distribution and they can be
shipped or versioned independently.

## Capability index

| Capability | Public surface | Reads | Writes | Phase |
|---|---|---|---|---|
| [`destination/`](destination/) | `DestinationResearchAgent`, `build_destination_agent` | `TripBrief` | `Recommendations` | Phase 3 |
| [`logistics/`](logistics/) | `LogisticsPlanningAgent`, `build_logistics_agent` | `TripBrief`, `Recommendations` | `LogisticsPlan` | Phase 4 |
| [`budget/`](budget/) | `BudgetPlanningAgent`, `build_budget_agent` | `TripBrief`, `Recommendations`, `LogisticsPlan` | `BudgetReport` | Phase 5 |
| [`synthesis/`](synthesis/) | `ItinerarySynthesisAgent`, `build_synthesis_agent` | `TripBrief`, `Recommendations`, `LogisticsPlan`, `BudgetReport` | `Itinerary` | Phase 5 |
| [`validator/`](validator/) | `ItineraryValidatorAgent`, `build_validator_agent` | `Itinerary` | `RevisionRequest` | Phase 6 |
| [`repair/`](repair/) | `RepairLoopAgent`, `build_repair_loop_agent` | `RevisionRequest` + upstream state | dispatched re-run of a worker | Phase 7 |

## Public import surface

```python
from agents.destination import build_destination_agent
from agents.logistics  import build_logistics_agent
from agents.budget     import build_budget_agent
from agents.synthesis  import build_synthesis_agent
from agents.validator  import build_validator_agent
from agents.repair     import build_repair_loop_agent
```

The orchestrator wires these factories together inside
`packages/orchestrator/src/orchestrator/graph.py` (lazy imports keep the
build graph easy to reason about and avoid a circular dependency on
`travel-planner-orchestrator` from each capability).

## Adding a new capability

1. Create `packages/agents/<new>/` matching the layout above.
2. Subclass `Agent` from `orchestrator.agents.base` and define a
   `build_<new>_agent(...)` factory in `agent.py`; re-export both from
   `__init__.py`.
3. Add an editable install of the package to
   `apps/api/requirements.txt` and a tests-path entry to
   `apps/api/pyproject.toml`.
4. Wire the new capability into `orchestrator.graph` (lazy import + node).

## Verify the whole agents layer

```bash
cd ../../apps/api
.venv\Scripts\Activate.ps1   # macOS/Linux: source .venv/bin/activate
pytest ../../packages/agents -q
```
