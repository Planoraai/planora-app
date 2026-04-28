"""Itinerary Validation capability: applies hard rules (budget, geography, time) and produces
a typed RevisionRequest enumerating issues for the repair loop to act on.

Originally lived as `phases/phase6/src/phase6/validator.py`; moved to
`packages/agents/validator/` as part of the domain-driven repo layout (see
docs/implementationPlan.md, Pass 3).
"""

from __future__ import annotations

from agents.validator.agent import ItineraryValidatorAgent, build_validator_agent

__all__ = ["ItineraryValidatorAgent", "build_validator_agent"]
