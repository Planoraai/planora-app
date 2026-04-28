"""Itinerary Synthesis capability: merges destination recommendations, logistics, and budget
into a coherent day-by-day Itinerary contract handed off to the validator.

Originally lived as `phases/phase5/src/phase5/synthesise.py`; moved to
`packages/agents/synthesis/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.synthesis.agent import ItinerarySynthesisAgent, build_synthesis_agent

__all__ = ["ItinerarySynthesisAgent", "build_synthesis_agent"]
