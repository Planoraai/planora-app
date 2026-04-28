"""Phase 1 orchestrator graph tests."""

from __future__ import annotations

from orchestrator.graph import run_orchestrator


def test_graph_runs_end_to_end_with_stub_nodes() -> None:
    state = run_orchestrator(
        "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3,000 budget. Love food and temples, hate crowds."
    )
    assert state["trip_brief"].destination_country == "Japan"
    assert state["itinerary"].trip_brief.cities == ["Tokyo", "Kyoto"]
    assert state["budget_report"].within_budget is True
    assert state["revision_request"].approved is True
