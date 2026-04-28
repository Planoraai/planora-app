"""Budget agent tests: per-category cost estimation, over-budget flagging, sanity flags."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from agents.budget import BudgetPlanningAgent, build_budget_agent
from agents.destination import build_destination_agent
from agents.logistics import build_logistics_agent
from domain_contracts import TripBrief


def _sample_trip(budget_usd: float = 3000) -> TripBrief:
    return TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=budget_usd,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )


def test_budget_agent_outputs_valid_report() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    budget = build_budget_agent().run_for_trip(trip, recs, logistics)

    assert budget.total_estimate_usd >= 0
    assert budget.by_category.stay >= 0
    assert budget.by_category.transport >= 0
    assert budget.by_category.food >= 0
    assert budget.by_category.activities >= 0
    assert budget.by_category.buffer >= 0


def test_budget_agent_sets_flags_when_over_budget() -> None:
    trip = _sample_trip(budget_usd=200)
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    budget = build_budget_agent().run_for_trip(trip, recs, logistics)

    assert budget.within_budget is False
    assert budget.flags


def test_budget_agent_flags_all_zero_estimates_as_sanity_issue() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    agent = build_budget_agent()
    with (
        patch.object(BudgetPlanningAgent, "_estimate_stay_cost", return_value=0.0),
        patch.object(BudgetPlanningAgent, "_estimate_transport_cost", return_value=0.0),
        patch.object(BudgetPlanningAgent, "_estimate_daily_category_cost", return_value=0.0),
    ):
        budget = agent.run_for_trip(trip, recs, logistics)

    assert budget.total_estimate_usd == 0
    assert any("all estimated category costs are $0.00" in flag.issue for flag in budget.flags)


def test_budget_agent_flags_outlier_category_share() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)
    agent = build_budget_agent()
    with (
        patch.object(BudgetPlanningAgent, "_estimate_stay_cost", return_value=2000.0),
        patch.object(BudgetPlanningAgent, "_estimate_transport_cost", return_value=50.0),
        patch.object(
            BudgetPlanningAgent,
            "_estimate_daily_category_cost",
            side_effect=[30.0, 20.0],
        ),
    ):
        budget = agent.run_for_trip(trip, recs, logistics)

    assert any("is an outlier" in flag.issue for flag in budget.flags)


@pytest.mark.asyncio
async def test_budget_async_wrapper() -> None:
    trip = _sample_trip()
    destination = build_destination_agent()
    recs = destination.run_for_trip(trip)
    logistics = build_logistics_agent().run_for_trip(trip, recs)

    budget_agent = build_budget_agent()
    budget_state = await budget_agent.run(
        {"trip_brief": trip, "recommendations": recs, "logistics_plan": logistics}
    )
    assert "budget_report" in budget_state
