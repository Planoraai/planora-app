"""Budget Planning capability: estimates per-category costs (stay/transport/food/activities/buffer),
flags outliers, and signals whether the plan fits the trip's stated budget.

Originally lived as `phases/phase5/src/phase5/budget.py`; moved to
`packages/agents/budget/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.budget.agent import BudgetPlanningAgent, build_budget_agent

__all__ = ["BudgetPlanningAgent", "build_budget_agent"]
