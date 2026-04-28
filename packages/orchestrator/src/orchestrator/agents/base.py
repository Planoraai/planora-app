"""Shared abstract base for every specialist agent (destination, logistics, budget, validator, repair).

Concrete agents live in `packages/agents/<capability>/` and are wired into the LangGraph
state machine in `orchestrator.graph`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Abstract base for every specialist agent.

    Sub-classes must implement `run`, which receives the shared graph state
    and returns an updated state.
    """

    name: str = "agent"

    @abstractmethod
    async def run(self, state: Any) -> Any:
        """Execute this agent against the shared run state."""
        raise NotImplementedError
