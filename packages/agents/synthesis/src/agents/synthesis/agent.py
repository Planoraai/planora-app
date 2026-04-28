"""Itinerary synthesis implementation for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain_contracts import (
    BudgetReport,
    Itinerary,
    ItineraryDay,
    LogisticsPlan,
    Recommendations,
    TripBrief,
)


@dataclass(slots=True)
class ItinerarySynthesisAgent:
    """Merge destination, logistics, and budget outputs into final itinerary."""

    def run_for_trip(
        self,
        trip_brief: TripBrief,
        recommendations: Recommendations,
        logistics_plan: LogisticsPlan,
        budget_report: BudgetReport,
    ) -> Itinerary:
        itinerary_days: list[ItineraryDay] = []
        for day in logistics_plan.day_skeleton:
            highlights = [block.activity for block in day.blocks]
            summary = (
                f"{day.city} day plan with {len(highlights)} slots; "
                f"focus on {', '.join(trip_brief.preferences or ['local culture'])}."
            )
            itinerary_days.append(
                ItineraryDay(
                    day=day.day,
                    city=day.city,
                    summary=summary,
                    highlights=highlights,
                )
            )

        notes = [
            "Merged from Destination + Logistics + Budget specialist outputs.",
            "Day blocks are linked to recommendation themes by category/name alignment.",
        ]
        if not budget_report.within_budget:
            notes.append("Budget exceeds target; review BudgetReport flags before user delivery.")

        return Itinerary(
            title=f"{trip_brief.duration_days}-day {trip_brief.destination_country} itinerary",
            trip_brief=trip_brief,
            recommendations=recommendations,
            logistics_plan=logistics_plan,
            budget_report=budget_report,
            day_by_day=itinerary_days,
            notes=notes,
        )

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Phase-compatible async wrapper used by orchestrator graph."""
        trip_brief = state["trip_brief"]
        recommendations = state["recommendations"]
        logistics_plan = state["logistics_plan"]
        budget_report = state["budget_report"]
        if not isinstance(trip_brief, TripBrief):
            trip_brief = TripBrief.model_validate(trip_brief)
        if not isinstance(recommendations, Recommendations):
            recommendations = Recommendations.model_validate(recommendations)
        if not isinstance(logistics_plan, LogisticsPlan):
            logistics_plan = LogisticsPlan.model_validate(logistics_plan)
        if not isinstance(budget_report, BudgetReport):
            budget_report = BudgetReport.model_validate(budget_report)
        itinerary = self.run_for_trip(
            trip_brief=trip_brief,
            recommendations=recommendations,
            logistics_plan=logistics_plan,
            budget_report=budget_report,
        )
        return {"itinerary": itinerary}


def build_synthesis_agent() -> ItinerarySynthesisAgent:
    """Factory helper used by orchestrator wiring."""
    return ItinerarySynthesisAgent()
