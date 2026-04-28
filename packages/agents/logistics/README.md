# travel-planner-agent-logistics

Logistics Planning worker: turns `Recommendations` into a concrete `LogisticsPlan` (cities -> nights,
intercity hops with mode + duration + cost estimate, daily transit notes) for the budget agent.

## Layout

```
src/agents/logistics/
  __init__.py        # public surface: LogisticsPlanningAgent, build_logistics_agent
  agent.py           # routing + transit estimate logic
tests/
  test_logistics_agent.py
```

## Public API

```python
from agents.logistics import LogisticsPlanningAgent, build_logistics_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/logistics -q
```

## Origin

Originally `phases/phase4/src/phase4/logistics.py` (see `docs/implementationPlan.md` Phase 4).
Moved here in Pass 3.
