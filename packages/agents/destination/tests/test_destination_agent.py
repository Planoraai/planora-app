"""Phase 3 destination research agent tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from agents.destination import DestinationResearchAgent, build_destination_agent
from domain_contracts import Recommendations, TripBrief


def _sample_trip_brief() -> TripBrief:
    return TripBrief(
        destination_country="Japan",
        cities=["Tokyo", "Kyoto"],
        duration_days=5,
        budget_usd=3000,
        preferences=["food", "temples"],
        avoidances=["crowds"],
    )


def test_destination_agent_returns_typed_recommendations_per_city() -> None:
    agent = build_destination_agent()
    result = agent.run_for_trip(_sample_trip_brief())
    assert isinstance(result, Recommendations)
    assert set(result.cities.keys()) == {"Tokyo", "Kyoto"}
    for city_output in result.cities.values():
        assert city_output.neighborhoods
        assert city_output.experiences
        assert city_output.food


def test_destination_agent_deduplicates_by_item_name() -> None:
    class DuplicateRegistry:
        def call(self, name: str, payload: dict[str, object]) -> object:
            del payload
            if name == "web_search":
                return SimpleNamespace(
                    results=[
                        SimpleNamespace(title="Nishiki Market", snippet="food lane in Kyoto"),
                        SimpleNamespace(title="Nishiki Market", snippet="duplicate entry"),
                    ]
                )
            return SimpleNamespace(
                matches=[
                    SimpleNamespace(doc_id="nishiki-market", text="food district"),
                    SimpleNamespace(doc_id="nishiki-market", text="duplicate kb"),
                ]
            )

    trip_brief = TripBrief(
        destination_country="Japan",
        cities=["Kyoto"],
        duration_days=3,
        budget_usd=1500,
        preferences=["food"],
        avoidances=["crowds"],
    )
    agent = DestinationResearchAgent(tool_registry=DuplicateRegistry())  # type: ignore[arg-type]
    result = agent.run_for_trip(trip_brief)
    names = [
        item.name.lower()
        for city_output in result.cities.values()
        for bucket in (city_output.neighborhoods, city_output.experiences, city_output.food)
        for item in bucket
    ]
    assert len(names) == len(set(names))


@pytest.mark.asyncio
async def test_destination_agent_async_run_updates_state() -> None:
    agent = build_destination_agent()
    state = {"trip_brief": _sample_trip_brief()}
    updated = await agent.run(state)
    assert "recommendations" in updated
    assert isinstance(updated["recommendations"], Recommendations)
