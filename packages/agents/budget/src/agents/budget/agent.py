"""Budget agent implementation for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from domain_contracts import (
    BudgetCategoryBreakdown,
    BudgetFlag,
    BudgetReport,
    LogisticsPlan,
    Recommendations,
    TripBrief,
)
from tools import ToolRegistry


@dataclass(slots=True)
class BudgetPlanningAgent:
    """Estimate category spend and produce actionable budget flags."""

    tool_registry: ToolRegistry

    def run_for_trip(
        self,
        trip_brief: TripBrief,
        recommendations: Recommendations,
        logistics_plan: LogisticsPlan,
    ) -> BudgetReport:
        del recommendations
        stay_cost = self._estimate_stay_cost(logistics_plan)
        transport_cost = self._estimate_transport_cost(logistics_plan)
        food_cost = self._estimate_daily_category_cost(trip_brief, category="food")
        activity_cost = self._estimate_daily_category_cost(trip_brief, category="activity")

        subtotal = stay_cost + transport_cost + food_cost + activity_cost
        buffer_cost = round(subtotal * 0.08, 2)
        total = round(subtotal + buffer_cost, 2)
        within_budget = total <= trip_brief.budget_usd
        budget_flags = self._build_budget_overflow_flags(
            trip_brief.budget_usd,
            total,
            stay_cost,
            transport_cost,
            food_cost,
        )
        sanity_flags = self._build_sanity_flags(
            trip_brief=trip_brief,
            stay_cost=stay_cost,
            transport_cost=transport_cost,
            food_cost=food_cost,
            activity_cost=activity_cost,
            buffer_cost=buffer_cost,
            total=total,
        )
        flags = [*budget_flags, *sanity_flags]
        return BudgetReport(
            total_estimate_usd=total,
            by_category=BudgetCategoryBreakdown(
                stay=stay_cost,
                transport=transport_cost,
                food=food_cost,
                activities=activity_cost,
                buffer=buffer_cost,
            ),
            flags=flags,
            within_budget=within_budget,
        )

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Phase-compatible async wrapper used by orchestrator graph."""
        trip_brief = state["trip_brief"]
        recommendations = state["recommendations"]
        logistics_plan = state["logistics_plan"]
        if not isinstance(trip_brief, TripBrief):
            trip_brief = TripBrief.model_validate(trip_brief)
        if not isinstance(recommendations, Recommendations):
            recommendations = Recommendations.model_validate(recommendations)
        if not isinstance(logistics_plan, LogisticsPlan):
            logistics_plan = LogisticsPlan.model_validate(logistics_plan)
        return {
            "budget_report": self.run_for_trip(
                trip_brief=trip_brief,
                recommendations=recommendations,
                logistics_plan=logistics_plan,
            )
        }

    def _estimate_stay_cost(self, logistics_plan: LogisticsPlan) -> float:
        total = 0.0
        for stay in logistics_plan.stay_plan:
            result = self.tool_registry.call(
                "hotels_search",
                {
                    "city": stay.city,
                    "nights": stay.nights,
                    "adults": 2,
                    "max_results": 1,
                    "currency": "USD",
                },
            )
            options = list(getattr(result, "options", []))
            if options:
                total += float(getattr(options[0], "total_estimate", 0.0))
        return round(total, 2)

    def _estimate_transport_cost(self, logistics_plan: LogisticsPlan) -> float:
        total = 0.0
        for leg in logistics_plan.intercity:
            result = self.tool_registry.call(
                "transit_search",
                {
                    "origin_city": leg.from_city,
                    "destination_city": leg.to_city,
                    "max_results": 1,
                    "currency": "USD",
                },
            )
            options = list(getattr(result, "options", []))
            if options:
                total += float(getattr(options[0], "estimated_price", 0.0))
        return round(total, 2)

    def _estimate_daily_category_cost(self, trip_brief: TripBrief, *, category: str) -> float:
        per_day_total = 0.0
        for city in trip_brief.cities:
            estimate = self.tool_registry.call(
                "price_estimate",
                {"city": city, "category": category, "currency": "USD"},
            )
            min_cost = float(getattr(estimate, "min_cost", 0.0))
            max_cost = float(getattr(estimate, "max_cost", 0.0))
            per_day_total += (min_cost + max_cost) / 2
        if trip_brief.cities:
            per_day_total /= len(trip_brief.cities)
        return round(per_day_total * trip_brief.duration_days * trip_brief.travelers, 2)

    def _build_budget_overflow_flags(
        self,
        budget_limit: float,
        total_estimate: float,
        stay_cost: float,
        transport_cost: float,
        food_cost: float,
    ) -> list[BudgetFlag]:
        if total_estimate <= budget_limit:
            return []
        overflow = round(total_estimate - budget_limit, 2)
        return [
            BudgetFlag(
                issue=f"Estimated total exceeds budget by ${overflow}.",
                suggestion="Reduce stay cost by switching to cheaper neighborhoods or shorter stays.",
            ),
            BudgetFlag(
                issue=f"Top categories: stay=${stay_cost:.2f}, transport=${transport_cost:.2f}, food=${food_cost:.2f}.",
                suggestion="Prefer train/bus over flights and replace one premium food stop per day.",
            ),
        ]

    def _build_sanity_flags(
        self,
        *,
        trip_brief: TripBrief,
        stay_cost: float,
        transport_cost: float,
        food_cost: float,
        activity_cost: float,
        buffer_cost: float,
        total: float,
    ) -> list[BudgetFlag]:
        flags: list[BudgetFlag] = []
        subtotal = stay_cost + transport_cost + food_cost + activity_cost

        if subtotal == 0 and total == 0:
            flags.append(
                BudgetFlag(
                    issue="Sanity: all estimated category costs are $0.00.",
                    suggestion="Re-run budget estimation with fallback price baselines before approval.",
                )
            )
            return flags

        if total > 0:
            if buffer_cost / total > 0.5:
                flags.append(
                    BudgetFlag(
                        issue="Sanity: contingency buffer dominates total estimated spend.",
                        suggestion="Inspect category estimates and rebalance buffer vs core categories.",
                    )
                )

            category_totals = {
                "stay": stay_cost,
                "transport": transport_cost,
                "food": food_cost,
                "activities": activity_cost,
            }
            top_category, top_value = max(category_totals.items(), key=lambda item: item[1])
            if subtotal > 0 and top_value / subtotal >= 0.85 and top_value >= 250:
                flags.append(
                    BudgetFlag(
                        issue=f"Sanity: {top_category} is an outlier at ${top_value:.2f} "
                        f"({(top_value / subtotal) * 100:.0f}% of core spend).",
                        suggestion="Cross-check this category with alternate suppliers or capped assumptions.",
                    )
                )

            people_days = max(1, trip_brief.duration_days * trip_brief.travelers)
            per_person_per_day = total / people_days
            if per_person_per_day < 20:
                flags.append(
                    BudgetFlag(
                        issue=f"Sanity: per-person daily spend (${per_person_per_day:.2f}) is unusually low.",
                        suggestion="Validate unit prices and currency assumptions for each category.",
                    )
                )
            if per_person_per_day > 1500:
                flags.append(
                    BudgetFlag(
                        issue=f"Sanity: per-person daily spend (${per_person_per_day:.2f}) is unusually high.",
                        suggestion="Re-evaluate premium selections and cap high-cost categories.",
                    )
                )
        return flags


def build_budget_agent(tool_registry: ToolRegistry | None = None) -> BudgetPlanningAgent:
    """Factory helper used by orchestrator wiring."""
    return BudgetPlanningAgent(tool_registry=tool_registry or ToolRegistry())
