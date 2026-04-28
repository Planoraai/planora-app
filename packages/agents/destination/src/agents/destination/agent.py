"""Destination research agent implementation for Phase 3."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from domain_contracts import CityRecommendations, RecommendationItem, Recommendations, TripBrief
from tools import ToolRegistry

_FOOD_KEYWORDS = ("food", "eat", "restaurant", "street food", "sushi", "ramen")
_NEIGHBORHOOD_KEYWORDS = ("district", "neighborhood", "area", "quarter", "ward")
_CROWD_HIGH_KEYWORDS = ("crowded", "busy", "popular")
_CROWD_LOW_KEYWORDS = ("quiet", "calm", "less touristy", "hidden")


@dataclass(slots=True)
class DestinationResearchAgent:
    """Build city-level recommendations from tool lookups."""

    tool_registry: ToolRegistry

    def build_sub_queries(self, trip_brief: TripBrief, city: str) -> list[str]:
        """Generate focused retrieval prompts for one city."""
        preferences = (
            ", ".join(trip_brief.preferences) if trip_brief.preferences else "local highlights"
        )
        avoidances = ", ".join(trip_brief.avoidances) if trip_brief.avoidances else "none"
        return [
            f"{city} best neighborhoods for {preferences}",
            f"{city} food and cultural experiences {preferences}",
            f"{city} quiet alternatives avoid {avoidances}",
        ]

    def run_for_trip(self, trip_brief: TripBrief) -> Recommendations:
        """Produce a typed Recommendations payload for all requested cities."""
        city_map: dict[str, CityRecommendations] = {}
        for city in trip_brief.cities:
            city_map[city] = self._recommend_for_city(trip_brief, city)
        return Recommendations(cities=city_map)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Phase-compatible async wrapper used by graph nodes."""
        trip_brief = state["trip_brief"]
        if not isinstance(trip_brief, TripBrief):
            trip_brief = TripBrief.model_validate(trip_brief)
        return {"recommendations": self.run_for_trip(trip_brief)}

    def _recommend_for_city(self, trip_brief: TripBrief, city: str) -> CityRecommendations:
        items_by_category: dict[str, list[RecommendationItem]] = {
            "neighborhoods": [],
            "experiences": [],
            "food": [],
        }
        seen_names: set[str] = set()

        for query in self.build_sub_queries(trip_brief, city):
            web_response = self.tool_registry.call("web_search", {"query": query, "limit": 4})
            vector_response = self.tool_registry.call(
                "vector_search",
                {"query": query, "top_k": 4, "namespace": "travel"},
            )

            web_results = list(getattr(web_response, "results", []))
            vector_matches = list(getattr(vector_response, "matches", []))
            for candidate in [*web_results, *vector_matches]:
                item = self._to_recommendation_item(candidate, city, trip_brief)
                normalized = item.name.strip().lower()
                if normalized in seen_names:
                    continue
                seen_names.add(normalized)
                category = self._category_for_item(item)
                items_by_category[category].append(item)

        self._ensure_non_empty_categories(
            items_by_category,
            city,
            trip_brief.preferences,
            trip_brief.avoidances,
        )
        return CityRecommendations(
            neighborhoods=items_by_category["neighborhoods"][:5],
            experiences=items_by_category["experiences"][:7],
            food=items_by_category["food"][:7],
        )

    def _to_recommendation_item(
        self,
        raw: object,
        city: str,
        trip_brief: TripBrief,
    ) -> RecommendationItem:
        if not isinstance(raw, SimpleNamespace):
            raw = SimpleNamespace(**getattr(raw, "__dict__", {}))

        name = getattr(raw, "title", None) or getattr(raw, "doc_id", None) or f"{city} highlight"
        why = (
            getattr(raw, "snippet", None)
            or getattr(raw, "text", None)
            or f"Popular choice in {city}."
        )
        combined = f"{name} {why}".lower()

        tags = sorted({tag for tag in trip_brief.preferences if tag in combined})
        crowd_level = self._infer_crowd_level(combined, trip_brief.avoidances)
        priority = "must_do" if tags else "nice_to_have"
        return RecommendationItem(
            name=str(name),
            why=str(why),
            tags=tags,
            crowd_level=crowd_level,
            priority=priority,
        )

    def _category_for_item(self, item: RecommendationItem) -> str:
        text = f"{item.name} {item.why}".lower()
        if any(keyword in text for keyword in _FOOD_KEYWORDS):
            return "food"
        if any(keyword in text for keyword in _NEIGHBORHOOD_KEYWORDS):
            return "neighborhoods"
        return "experiences"

    def _infer_crowd_level(self, text: str, avoidances: list[str]) -> str:
        if any(word in text for word in _CROWD_HIGH_KEYWORDS):
            return "high"
        avoiding_crowds = any("crowd" in tag for tag in avoidances)
        if avoiding_crowds or any(word in text for word in _CROWD_LOW_KEYWORDS):
            return "low"
        return "medium"

    def _ensure_non_empty_categories(
        self,
        items_by_category: dict[str, list[RecommendationItem]],
        city: str,
        preferences: list[str],
        avoidances: list[str],
    ) -> None:
        defaults = {
            "neighborhoods": RecommendationItem(
                name=f"{city} Central District Walk",
                why=f"Good orientation area to understand {city} layout.",
                tags=[],
                crowd_level="medium",
                priority="nice_to_have",
            ),
            "experiences": RecommendationItem(
                name=f"{city} Signature Cultural Experience",
                why=f"Baseline cultural activity aligned with {'/'.join(preferences) or 'general interests'}.",
                tags=preferences[:2],
                crowd_level="medium",
                priority="must_do" if preferences else "nice_to_have",
            ),
            "food": RecommendationItem(
                name=f"{city} Local Food Crawl",
                why=f"Structured food stop to sample regional dishes in {city}.",
                tags=["food"] if "food" in preferences else [],
                crowd_level="low" if any("crowd" in item for item in avoidances) else "medium",
                priority="must_do" if "food" in preferences else "nice_to_have",
            ),
        }
        for category, default_item in defaults.items():
            if not items_by_category[category]:
                items_by_category[category].append(default_item)


def build_destination_agent(tool_registry: ToolRegistry | None = None) -> DestinationResearchAgent:
    """Factory helper used by orchestrator wiring."""
    return DestinationResearchAgent(tool_registry=tool_registry or ToolRegistry())
