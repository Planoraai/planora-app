# travel-planner-agent-budget

Budget Planning worker: estimates per-category costs (stay/transport/food/activities/buffer),
flags outliers and zero-cost sanity issues, and signals whether the plan fits the trip's
stated `budget_usd`.

## Layout

```
src/agents/budget/
  __init__.py        # public surface: BudgetPlanningAgent, build_budget_agent
  agent.py           # cost estimation + flag generation
tests/
  test_budget_agent.py
```

## Public API

```python
from agents.budget import BudgetPlanningAgent, build_budget_agent
```

## Verify

```bash
cd ../../../apps/api
.venv\Scripts\Activate.ps1
pytest ../../packages/agents/budget -q
```

## Origin

Originally `phases/phase5/src/phase5/budget.py` (see `docs/implementationPlan.md` Phase 5).
Moved here in Pass 3 and split off from synthesis.
