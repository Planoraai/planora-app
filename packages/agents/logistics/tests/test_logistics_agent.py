"""Phase 4 logistics planning agent tests."""

from __future__ import annotations

import pytest
from agents.destination import build_destination_agent
from agents.logistics import LogisticsPlanningAgent, build_logistics_agent
from domain_contracts import Recommendations, TripBrief


def _sample_trip() -> TripBrief:
    return TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=3000,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )


def _sample_recommendations() -> Recommendations:
    destination_agent = build_destination_agent()
    return destination_agent.run_for_trip(_sample_trip())


def test_logistics_agent_returns_typed_plan() -> None:
    agent = build_logistics_agent()
    plan = agent.run_for_trip(_sample_trip(), _sample_recommendations())
    assert len(plan.day_skeleton) == 5
    assert len(plan.stay_plan) == 2
    assert sum(item.nights for item in plan.stay_plan) == 5
    assert all(day.blocks for day in plan.day_skeleton)


def test_logistics_respects_max_intercity_transfers() -> None:
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto", "Osaka"],
        duration_days=6,
        budget_usd=3500,
        preferences=["food"],
        avoidances=["crowds"],
        constraints={"max_intercity_transfers": 1},
    )
    recommendations = _sample_recommendations()
    agent = build_logistics_agent()
    plan = agent.run_for_trip(trip, recommendations)
    assert len(plan.stay_plan) <= 2
    assert len(plan.intercity) <= 1
    assert sum(item.nights for item in plan.stay_plan) == trip.duration_days


@pytest.mark.asyncio
async def test_logistics_agent_async_run_updates_state() -> None:
    agent = build_logistics_agent()
    state = {"trip_brief": _sample_trip(), "recommendations": _sample_recommendations()}
    updated = await agent.run(state)
    assert "logistics_plan" in updated
    assert updated["logistics_plan"].day_skeleton


def test_logistics_uses_default_area_when_recommendations_missing() -> None:
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo"],
        duration_days=2,
        budget_usd=1200,
        preferences=["food"],
        avoidances=["crowds"],
    )
    empty_recommendations = Recommendations(cities={})
    agent = LogisticsPlanningAgent(tool_registry=build_logistics_agent().tool_registry)
    plan = agent.run_for_trip(trip, empty_recommendations)
    assert plan.stay_plan[0].area


def test_logistics_caps_selected_cities_when_trip_days_are_lower_than_city_count() -> None:
    trip = TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto", "Osaka"],
        duration_days=2,
        budget_usd=2000,
        preferences=["food"],
        avoidances=["crowds"],
        constraints={"max_intercity_transfers": 5},
    )
    recommendations = _sample_recommendations()
    agent = build_logistics_agent()
    plan = agent.run_for_trip(trip, recommendations)
    assert len(plan.stay_plan) == 2
    assert [stay.city for stay in plan.stay_plan] == ["Tokyo", "Kyoto"]
    assert sum(item.nights for item in plan.stay_plan) == trip.duration_days
    assert len(plan.day_skeleton) == trip.duration_days
