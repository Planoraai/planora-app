"""Logistics Planning capability: turns destination recommendations into a concrete stay/transit
plan (cities -> nights, intercity hops, daily transit notes) for downstream budgeting.

Originally lived as `phases/phase4/src/phase4/logistics.py`; moved to
`packages/agents/logistics/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.logistics.agent import LogisticsPlanningAgent, build_logistics_agent

__all__ = ["LogisticsPlanningAgent", "build_logistics_agent"]
