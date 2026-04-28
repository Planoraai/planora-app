"""Agent contract.

Exposes the shared `Agent` ABC. Concrete specialist agents (destination, logistics,
budget, validator, repair-loop) live in `packages/agents/<capability>/` and are wired
into the orchestrator graph in `orchestrator.graph`.
"""

from __future__ import annotations

from orchestrator.agents.base import Agent

__all__ = ["Agent"]
