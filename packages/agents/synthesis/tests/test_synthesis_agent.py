"""Synthesis agent tests: merging recommendations, logistics, and budget into a day-by-day itinerary."""

from __future__ import annotations

import pytest
from agents.budget import build_budget_agent
from agents.destination import build_destination_agent
from agents.logistics import build_logistics_agent
from agents.synthesis import build_synthesis_agent
from domain_contracts import TripBrief


def _sample_trip() -> TripBrief:
    return TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=3000,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )


def test_synthesis_merges_into_itinerary_with_day_count() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    budget = build_budget_agent().run_for_trip(trip, recs, logistics)
    itinerary = build_synthesis_agent().run_for_trip(trip, recs, logistics, budget)

    assert itinerary.trip_brief.cities == ["Tokyo", "Kyoto"]
    assert len(itinerary.day_by_day) == trip.duration_days
    assert itinerary.budget_report.total_estimate_usd == budget.total_estimate_usd


@pytest.mark.asyncio
async def test_synthesis_async_wrapper() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    budget = build_budget_agent().run_for_trip(trip, recs, logistics)

    synthesis_agent = build_synthesis_agent()
    itinerary_state = await synthesis_agent.run(
        {
            "trip_brief": trip,
            "recommendations": recs,
            "logistics_plan": logistics,
            "budget_report": budget,
        }
    )
    assert "itinerary" in itinerary_state
