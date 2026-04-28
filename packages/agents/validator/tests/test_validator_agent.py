"""Phase 6 validator tests."""

from __future__ import annotations

import pytest
from agents.budget import build_budget_agent
from agents.destination import build_destination_agent
from agents.logistics import build_logistics_agent
from agents.synthesis import build_synthesis_agent
from agents.validator import build_validator_agent
from domain_contracts import TripBrief


def _build_itinerary(budget_usd: float = 3000):
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=budget_usd,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )
    recs = build_destination_agent().run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    budget = build_budget_agent().run_for_trip(trip, recs, logistics)
    itinerary = build_synthesis_agent().run_for_trip(trip, recs, logistics, budget)
    return trip, itinerary


def test_validator_approves_valid_itinerary() -> None:
    trip, itinerary = _build_itinerary()
    request = build_validator_agent().validate(trip, itinerary)
    assert request.approved is True


def test_validator_rejects_over_budget_itinerary() -> None:
    trip, itinerary = _build_itinerary(budget_usd=200)
    request = build_validator_agent().validate(trip, itinerary)
    assert request.approved is False
    assert any("exceeds budget" in issue.lower() for issue in request.issues)
    assert request.requested_changes


def test_validator_rejects_when_required_city_missing() -> None:
    trip, itinerary = _build_itinerary()
    itinerary.day_by_day = [day for day in itinerary.day_by_day if day.city != "Kyoto"]
    request = build_validator_agent().validate(trip, itinerary)
    assert request.approved is False
    assert any("missing required cities" in issue.lower() for issue in request.issues)


@pytest.mark.asyncio
async def test_validator_async_wrapper_updates_state() -> None:
    trip, itinerary = _build_itinerary()
    state = await build_validator_agent().run({"trip_brief": trip, "itinerary": itinerary})
    assert "revision_request" in state
