# travel-planner-agent-repair

Repair-Loop worker: routes a `RevisionRequest` to the offending worker
(destination/logistics/budget/synthesis), re-validates, and bounds the number of revision
passes (`max_retries`).

## Layout

```
src/agents/repair/
  __init__.py        # public surface: RepairLoopAgent, build_repair_loop_agent
  agent.py           # dispatch + retry counter
tests/
  test_repair_agent.py
```

## Public API

```python
from agents.repair import RepairLoopAgent, build_repair_loop_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/repair -q
```

## Origin

Originally `phases/phase7/src/phase7/repair_loop.py` (see `docs/implementationPlan.md` Phase 7).
Moved here in Pass 3.
