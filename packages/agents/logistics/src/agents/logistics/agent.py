"""Logistics agent implementation for Phase 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain_contracts import (
    CityRecommendations,
    DayBlock,
    DaySkeleton,
    IntercityLeg,
    LogisticsPlan,
    Recommendations,
    StayAllocation,
    TripBrief,
)
from tools import ToolRegistry


@dataclass(slots=True)
class LogisticsPlanningAgent:
    """Create stay allocation, movement legs, and day skeleton."""

    tool_registry: ToolRegistry

    def run_for_trip(
        self, trip_brief: TripBrief, recommendations: Recommendations
    ) -> LogisticsPlan:
        """Produce a typed LogisticsPlan for requested cities."""
        visited_cities = self._bounded_cities(
            trip_brief.cities,
            trip_brief.constraints.max_intercity_transfers,
        )
        visited_cities = self._fit_cities_to_available_days(
            visited_cities=visited_cities,
            total_days=trip_brief.duration_days,
        )
        stay_plan = self._allocate_stays(
            visited_cities=visited_cities,
            total_days=trip_brief.duration_days,
            recommendations=recommendations,
        )
        intercity_legs = self._build_intercity_legs(stay_plan)
        day_skeleton = self._build_day_skeleton(stay_plan, recommendations)
        return LogisticsPlan(
            stay_plan=stay_plan,
            intercity=intercity_legs,
            day_skeleton=day_skeleton,
        )

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Phase-compatible async wrapper used by orchestrator graph."""
        trip_brief = state["trip_brief"]
        recommendations = state["recommendations"]
        if not isinstance(trip_brief, TripBrief):
            trip_brief = TripBrief.model_validate(trip_brief)
        if not isinstance(recommendations, Recommendations):
            recommendations = Recommendations.model_validate(recommendations)
        plan = self.run_for_trip(trip_brief, recommendations)
        return {"logistics_plan": plan}

    def _bounded_cities(self, cities: list[str], max_transfers: int) -> list[str]:
        max_city_count = max(1, max_transfers + 1)
        return cities[:max_city_count] if len(cities) > max_city_count else cities

    def _fit_cities_to_available_days(
        self, *, visited_cities: list[str], total_days: int
    ) -> list[str]:
        # `StayAllocation.nights` requires at least one night per selected city.
        # If cities exceed available days, keep a deterministic prefix.
        if len(visited_cities) <= total_days:
            return visited_cities
        return visited_cities[:total_days]

    def _allocate_stays(
        self,
        *,
        visited_cities: list[str],
        total_days: int,
        recommendations: Recommendations,
    ) -> list[StayAllocation]:
        if not visited_cities:
            return []
        city_count = len(visited_cities)
        base_nights = total_days // city_count
        remainder = total_days % city_count
        stay_plan: list[StayAllocation] = []
        for idx, city in enumerate(visited_cities):
            nights = base_nights + (1 if idx < remainder else 0)
            area = self._preferred_area(city, recommendations.cities.get(city))
            stay_plan.append(StayAllocation(city=city, nights=nights, area=area))
        return stay_plan

    def _preferred_area(self, city: str, city_recs: CityRecommendations | None) -> str:
        if city_recs and city_recs.neighborhoods:
            return city_recs.neighborhoods[0].name
        hotels_response = self.tool_registry.call(
            "hotels_search",
            {"city": city, "nights": 1, "adults": 2, "max_results": 1, "currency": "USD"},
        )
        options = list(getattr(hotels_response, "options", []))
        if options:
            area = getattr(options[0], "neighborhood", None)
            if isinstance(area, str) and area.strip():
                return area
        return f"{city} Central"

    def _build_intercity_legs(self, stay_plan: list[StayAllocation]) -> list[IntercityLeg]:
        from itertools import pairwise

        legs: list[IntercityLeg] = []
        for from_stay, to_stay in pairwise(stay_plan):
            transit = self.tool_registry.call(
                "transit_search",
                {
                    "origin_city": from_stay.city,
                    "destination_city": to_stay.city,
                    "max_results": 1,
                    "currency": "USD",
                },
            )
            options = list(getattr(transit, "options", []))
            if options:
                primary = options[0]
                legs.append(
                    IntercityLeg(
                        **{
                            "from": from_stay.city,
                            "to": to_stay.city,
                            "mode": str(getattr(primary, "mode", "train")),
                            "duration_min": int(getattr(primary, "duration_minutes", 180)),
                        }
                    )
                )
                continue

            maps = self.tool_registry.call(
                "maps_distance",
                {"origin": from_stay.city, "destination": to_stay.city, "mode": "train"},
            )
            legs.append(
                IntercityLeg(
                    **{
                        "from": from_stay.city,
                        "to": to_stay.city,
                        "mode": "train",
                        "duration_min": int(getattr(maps, "duration_minutes", 180)),
                    }
                )
            )
        return legs

    def _build_day_skeleton(
        self,
        stay_plan: list[StayAllocation],
        recommendations: Recommendations,
    ) -> list[DaySkeleton]:
        skeleton: list[DaySkeleton] = []
        day_number = 1
        for stay in stay_plan:
            city_recs = recommendations.cities.get(stay.city)
            for night_idx in range(stay.nights):
                blocks = self._day_blocks(stay.city, city_recs, night_idx)
                skeleton.append(DaySkeleton(day=day_number, city=stay.city, blocks=blocks))
                day_number += 1
        return skeleton

    def _day_blocks(
        self,
        city: str,
        city_recs: CityRecommendations | None,
        day_index: int,
    ) -> list[DayBlock]:
        neighborhoods = city_recs.neighborhoods if city_recs else []
        experiences = city_recs.experiences if city_recs else []
        food = city_recs.food if city_recs else []
        morning = (
            neighborhoods[day_index % len(neighborhoods)].name if neighborhoods else f"{city} walk"
        )
        afternoon = (
            experiences[day_index % len(experiences)].name
            if experiences
            else f"{city} cultural highlight"
        )
        evening = food[day_index % len(food)].name if food else f"{city} food district"
        return [
            DayBlock(period="morning", activity=morning),
            DayBlock(period="afternoon", activity=afternoon),
            DayBlock(period="evening", activity=evening),
        ]


def build_logistics_agent(tool_registry: ToolRegistry | None = None) -> LogisticsPlanningAgent:
    """Factory helper used by orchestrator wiring."""
    return LogisticsPlanningAgent(tool_registry=tool_registry or ToolRegistry())
