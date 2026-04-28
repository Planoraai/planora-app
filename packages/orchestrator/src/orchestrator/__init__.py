"""Orchestrator: parse the request, build the agent graph, drive the run.

Modules:
    parser.py      - free text -> TripBrief
    graph.py       - LangGraph state graph + conditional edges
    agents/base.py - shared abstract Agent contract for every specialist
    prompts/       - versioned prompt templates

Specialist agents (destination, logistics, budget, validator, repair) live in
`packages/agents/*` and are imported by `graph.py`.
"""

from __future__ import annotations

from orchestrator.graph import build_graph, run_orchestrator
from orchestrator.parser import parse_trip_request

__all__ = ["build_graph", "parse_trip_request", "run_orchestrator"]
