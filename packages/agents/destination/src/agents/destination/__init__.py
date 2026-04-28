"""Destination Research capability: surfaces candidate cities, neighborhoods, and activity ideas
grounded in tool calls (web + vector search) for the orchestrator's destination node.

Originally lived as `phases/phase3/src/phase3/destination.py`; moved to
`packages/agents/destination/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.destination.agent import DestinationResearchAgent, build_destination_agent

__all__ = ["DestinationResearchAgent", "build_destination_agent"]
