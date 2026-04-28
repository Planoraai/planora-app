"""LangGraph orchestrator skeleton for Phase 1.

Graph shape:
    parse -> destination -> logistics -> budget -> synthesise -> validate -> repair -> END
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypedDict

from domain_contracts import (
    BudgetCategoryBreakdown,
    BudgetReport,
    CityRecommendations,
    DayBlock,
    DaySkeleton,
    Itinerary,
    ItineraryDay,
    LogisticsPlan,
    RecommendationItem,
    Recommendations,
    RevisionRequest,
    StayAllocation,
    TripBrief,
)

from orchestrator.parser import parse_trip_request


class OrchestratorState(TypedDict, total=False):
    request_text: str
    trip_brief: TripBrief
    recommendations: Recommendations
    logistics_plan: LogisticsPlan
    budget_report: BudgetReport
    itinerary: Itinerary
    revision_request: RevisionRequest


def build_graph() -> Callable[[OrchestratorState], OrchestratorState]:
    """Build and compile the LangGraph state machine.

    Falls back to a deterministic linear runner when `langgraph` is unavailable.
    """
    try:
        from langgraph.graph import END, StateGraph
    except Exception:  # pragma: no cover - exercised only without dependency
        return _LinearGraphFallback()

    graph = StateGraph(OrchestratorState)
    graph.add_node("parse", _parse_node)
    graph.add_node("destination", _destination_node)
    graph.add_node("logistics", _logistics_stub_node)
    graph.add_node("budget", _budget_stub_node)
    graph.add_node("synthesise", _synthesise_node)
    graph.add_node("validate", _validate_node)
    graph.add_node("repair", _repair_node)

    graph.set_entry_point("parse")
    graph.add_edge("parse", "destination")
    graph.add_edge("destination", "logistics")
    graph.add_edge("logistics", "budget")
    graph.add_edge("budget", "synthesise")
    graph.add_edge("synthesise", "validate")
    graph.add_edge("validate", "repair")
    graph.add_edge("repair", END)
    return graph.compile()


class _LinearGraphFallback:
    """Minimal invoke-compatible fallback used in local environments."""

    def invoke(self, state: OrchestratorState) -> OrchestratorState:
        next_state: OrchestratorState = dict(state)
        for node in (
            _parse_node,
            _destination_node,
            _logistics_stub_node,
            _budget_stub_node,
            _synthesise_node,
            _validate_node,
            _repair_node,
        ):
            next_state.update(node(next_state))
        return next_state


def run_orchestrator(request_text: str) -> OrchestratorState:
    """Invoke the phase-1 graph for a request."""
    app = build_graph()
    state: OrchestratorState = {"request_text": request_text}
    return app.invoke(state)


def _parse_node(state: OrchestratorState) -> OrchestratorState:
    text = state.get("request_text", "")
    return {"trip_brief": parse_trip_request(text)}


def _destination_node(state: OrchestratorState) -> OrchestratorState:
    """Destination stage aligned to architecture data-flow.

    Uses Phase 3 `DestinationResearchAgent` when available and falls back
    to deterministic local recommendations in standalone environments.
    """
    try:
        from agents.destination import build_destination_agent
    except Exception:
        return _destination_stub_node(state)

    agent = build_destination_agent()
    recommendations = agent.run_for_trip(state["trip_brief"])
    return {"recommendations": recommendations}


def _destination_stub_node(state: OrchestratorState) -> OrchestratorState:
    trip = state["trip_brief"]
    city_map: dict[str, CityRecommendations] = {}
    for city in trip.cities:
        city_map[city] = CityRecommendations(
            neighborhoods=[
                RecommendationItem(
                    name=f"{city} Old Quarter",
                    why="Walkable base with local food options",
                    tags=["food", "culture"],
                    crowd_level="low",
                    priority="must_do",
                )
            ],
            experiences=[
                RecommendationItem(
                    name=f"{city} Temple Circuit",
                    why="Matches temple preference and can be done early to avoid crowds",
                    tags=["temples", "quiet"],
                    crowd_level="low",
                    priority="must_do",
                )
            ],
            food=[
                RecommendationItem(
                    name=f"{city} Market Street",
                    why="High variety local food in one area",
                    tags=["food"],
                    crowd_level="medium",
                    priority="nice_to_have",
                )
            ],
        )
    return {"recommendations": Recommendations(cities=city_map)}


def _logistics_stub_node(state: OrchestratorState) -> OrchestratorState:
    """Logistics stage aligned to architecture data-flow.

    Uses Phase 4 `LogisticsPlanningAgent` when available and falls back to
    deterministic local logistics in standalone environments.
    """
    try:
        from agents.logistics import build_logistics_agent
    except Exception:
        return _logistics_fallback_node(state)

    agent = build_logistics_agent()
    logistics_plan = agent.run_for_trip(state["trip_brief"], state["recommendations"])
    return {"logistics_plan": logistics_plan}


def _logistics_fallback_node(state: OrchestratorState) -> OrchestratorState:
    trip = state["trip_brief"]
    cities = trip.cities or ["Tokyo"]
    stay_plan: list[StayAllocation] = []
    if len(cities) == 1:
        stay_plan.append(StayAllocation(city=cities[0], nights=trip.duration_days, area="Central"))
    else:
        first_nights = max(1, trip.duration_days // 2)
        second_nights = max(1, trip.duration_days - first_nights)
        stay_plan.append(StayAllocation(city=cities[0], nights=first_nights, area="Central"))
        stay_plan.append(StayAllocation(city=cities[1], nights=second_nights, area="Historic"))

    day_skeleton = [
        DaySkeleton(
            day=i + 1,
            city=cities[min(i, len(cities) - 1)],
            blocks=[
                DayBlock(period="morning", activity="Neighborhood walk"),
                DayBlock(period="afternoon", activity="Temple / cultural site"),
                DayBlock(period="evening", activity="Local food district"),
            ],
        )
        for i in range(trip.duration_days)
    ]

    return {
        "logistics_plan": LogisticsPlan(
            stay_plan=stay_plan, intercity=[], day_skeleton=day_skeleton
        )
    }


def _budget_stub_node(state: OrchestratorState) -> OrchestratorState:
    """Budget stage aligned to architecture data-flow.

    Uses Phase 5 `BudgetPlanningAgent` when available and falls back to
    deterministic local budgeting in standalone environments.
    """
    try:
        from agents.budget import build_budget_agent
    except Exception:
        return _budget_fallback_node(state)

    agent = build_budget_agent()
    budget_report = agent.run_for_trip(
        trip_brief=state["trip_brief"],
        recommendations=state["recommendations"],
        logistics_plan=state["logistics_plan"],
    )
    return {"budget_report": budget_report}


def _budget_fallback_node(state: OrchestratorState) -> OrchestratorState:
    trip = state["trip_brief"]
    estimate = min(trip.budget_usd * 0.88, trip.budget_usd - 50)
    by_category = BudgetCategoryBreakdown(
        stay=round(estimate * 0.42, 2),
        transport=round(estimate * 0.23, 2),
        food=round(estimate * 0.22, 2),
        activities=round(estimate * 0.09, 2),
        buffer=round(estimate * 0.04, 2),
    )
    return {
        "budget_report": BudgetReport(
            total_estimate_usd=round(estimate, 2),
            by_category=by_category,
            flags=[],
            within_budget=estimate <= trip.budget_usd,
        )
    }


def _synthesise_node(state: OrchestratorState) -> OrchestratorState:
    """Synthesis stage aligned to architecture data-flow.

    Uses Phase 5 `ItinerarySynthesisAgent` when available and falls back to
    deterministic local synthesis in standalone environments.
    """
    try:
        from agents.synthesis import build_synthesis_agent
    except Exception:
        return _synthesise_fallback_node(state)

    agent = build_synthesis_agent()
    itinerary = agent.run_for_trip(
        trip_brief=state["trip_brief"],
        recommendations=state["recommendations"],
        logistics_plan=state["logistics_plan"],
        budget_report=state["budget_report"],
    )
    return {"itinerary": itinerary}


def _synthesise_fallback_node(state: OrchestratorState) -> OrchestratorState:
    trip = state["trip_brief"]
    logistics = state["logistics_plan"]
    itinerary_days = [
        ItineraryDay(
            day=day.day,
            city=day.city,
            summary=f"{day.city} highlights focused on {', '.join(trip.preferences or ['local culture'])}.",
            highlights=[b.activity for b in day.blocks],
        )
        for day in logistics.day_skeleton
    ]
    itinerary = Itinerary(
        title=f"{trip.duration_days}-day {trip.destination_country} trip",
        trip_brief=trip,
        recommendations=state["recommendations"],
        logistics_plan=logistics,
        budget_report=state["budget_report"],
        day_by_day=itinerary_days,
        notes=["Phase 1 stub itinerary - replace with specialist-agent outputs in later phases."],
    )
    return {"itinerary": itinerary}


def _validate_node(state: OrchestratorState) -> OrchestratorState:
    """Validation stage aligned to architecture data-flow.

    Uses Phase 6 `ItineraryValidatorAgent` when available and falls back to
    deterministic local approval in standalone environments.
    """
    try:
        from agents.validator import build_validator_agent
    except Exception:
        return _validate_fallback_node(state)

    agent = build_validator_agent()
    revision_request = agent.validate(
        trip_brief=state["trip_brief"],
        itinerary=state["itinerary"],
    )
    return {"revision_request": revision_request}


def _validate_fallback_node(state: OrchestratorState) -> OrchestratorState:
    return {
        "revision_request": RevisionRequest(
            approved=True,
            issues=[],
            requested_changes=[],
        )
    }


def _repair_node(state: OrchestratorState) -> OrchestratorState:
    """Repair stage aligned to architecture data-flow.

    Uses Phase 7 `RepairLoopAgent` when available and falls back to pass-through
    when running without phase integrations.
    """
    try:
        from agents.repair import build_repair_loop_agent
    except Exception:
        return _repair_fallback_node(state)

    agent = build_repair_loop_agent(max_retries=2)
    repair_updates = agent.run(dict(state))
    return repair_updates


def _repair_fallback_node(state: OrchestratorState) -> OrchestratorState:
    return {
        "itinerary": state["itinerary"],
        "revision_request": state["revision_request"],
    }


def _format_output(state: OrchestratorState) -> str:
    payload = {
        "trip_brief": state["trip_brief"].model_dump(mode="json"),
        "itinerary": state["itinerary"].model_dump(mode="json"),
        "revision_request": state["revision_request"].model_dump(mode="json"),
    }
    return json.dumps(payload, indent=2)


def main() -> None:
    """CLI entrypoint for `python -m orchestrator.graph`."""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 1 orchestrator demo")
    parser.add_argument("request", nargs="+", help="Travel request text")
    args = parser.parse_args()
    request_text = " ".join(args.request)
    final_state = run_orchestrator(request_text)
    print(_format_output(final_state))


if __name__ == "__main__":
    main()
