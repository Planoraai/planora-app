# travel-planner-agent-synthesis

Itinerary Synthesis worker: merges `Recommendations` + `LogisticsPlan` + `BudgetReport`
into a coherent day-by-day `Itinerary` contract handed to the validator.

## Layout

```
src/agents/synthesis/
  __init__.py        # public surface: ItinerarySynthesisAgent, build_synthesis_agent
  agent.py           # day-by-day stitching
tests/
  test_synthesis_agent.py
```

## Public API

```python
from agents.synthesis import ItinerarySynthesisAgent, build_synthesis_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/synthesis -q
```

## Origin

Originally `phases/phase5/src/phase5/synthesise.py` (see `docs/implementationPlan.md` Phase 5).
Moved here in Pass 3 and split off from budget.
