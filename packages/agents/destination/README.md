# travel-planner-agent-destination

Destination Research worker: takes a `TripBrief`, calls web + vector search tools, and emits a
`Recommendations` contract (candidate cities, neighborhoods, activity ideas) for the
orchestrator's destination node.

## Layout

```
src/agents/destination/
  __init__.py        # public surface: DestinationResearchAgent, build_destination_agent
  agent.py           # behavior + tool wiring
tests/
  test_destination_agent.py
```

## Public API

```python
from agents.destination import DestinationResearchAgent, build_destination_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/destination -q
```

## Origin

Originally `phases/phase3/src/phase3/destination.py` during the phase-wise build-out
(see `docs/implementationPlan.md` Phase 3). Moved to this domain-driven location in Pass 3
of the layout migration.
