"""Repair Loop capability: feeds validator findings back into the relevant worker agent
(destination/logistics/budget/synthesis) for a bounded number of revision passes.

Originally lived as `phases/phase7/src/phase7/repair_loop.py`; moved to
`packages/agents/repair/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.repair.agent import RepairLoopAgent, build_repair_loop_agent

__all__ = ["RepairLoopAgent", "build_repair_loop_agent"]
