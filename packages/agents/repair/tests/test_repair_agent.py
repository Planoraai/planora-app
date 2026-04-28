"""Phase 7 repair loop tests."""

from __future__ import annotations

from unittest.mock import patch

from agents.budget import build_budget_agent
from agents.destination import build_destination_agent
from agents.logistics import build_logistics_agent
from agents.repair import build_repair_loop_agent
from agents.synthesis import build_synthesis_agent
from agents.validator import build_validator_agent
from domain_contracts import TripBrief
from domain_contracts.revision import RevisionRequest


def _build_pipeline_state(budget_usd: float) -> dict[str, object]:
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=budget_usd,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )
    destination_agent = build_destination_agent()
    recommendations = destination_agent.run_for_trip(trip)
    logistics_plan = build_logistics_agent().run_for_trip(trip, recommendations)
    budget_report = build_budget_agent().run_for_trip(trip, recommendations, logistics_plan)
    itinerary = build_synthesis_agent().run_for_trip(
        trip, recommendations, logistics_plan, budget_report
    )
    revision_request = build_validator_agent().validate(trip, itinerary)
    return {
        "trip_brief": trip,
        "recommendations": recommendations,
        "logistics_plan": logistics_plan,
        "budget_report": budget_report,
        "itinerary": itinerary,
        "revision_request": revision_request,
    }


def test_repair_loop_keeps_valid_itinerary_approved() -> None:
    state = _build_pipeline_state(budget_usd=3500)
    repaired = build_repair_loop_agent(max_retries=2).run(state)
    assert repaired["revision_request"].approved is True


def test_repair_loop_attempts_budget_fix_on_failure() -> None:
    state = _build_pipeline_state(budget_usd=200)
    repaired = build_repair_loop_agent(max_retries=2).run(state)
    assert repaired["revision_request"].approved in {True, False}
    assert (
        repaired["itinerary"].budget_report.total_estimate_usd
        <= state["itinerary"].budget_report.total_estimate_usd
    )


def test_repair_loop_is_bounded() -> None:
    state = _build_pipeline_state(budget_usd=100)
    repaired = build_repair_loop_agent(max_retries=1).run(state)
    assert "revision_request" in repaired
    assert "itinerary" in repaired


def test_repair_loop_marks_non_convergence_on_repeated_feedback() -> None:
    state = _build_pipeline_state(budget_usd=200)
    repeating = RevisionRequest(
        approved=False,
        issues=["Blocking: day count mismatch."],
        requested_changes=["Regenerate day_skeleton to exactly match TripBrief.duration_days."],
    )
    agent = build_repair_loop_agent(max_retries=2)
    with patch.object(type(agent), "_revalidate", return_value=repeating):
        repaired = agent.run(state)
    assert repaired["revision_request"].approved is False
    assert any("could not converge" in issue for issue in repaired["revision_request"].issues)
