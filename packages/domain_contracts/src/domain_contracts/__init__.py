"""Pydantic data contracts shared between agent stages."""

from __future__ import annotations

from domain_contracts.budget import BudgetCategoryBreakdown, BudgetFlag, BudgetReport
from domain_contracts.itinerary import Itinerary, ItineraryDay
from domain_contracts.logistics import (
    DayBlock,
    DaySkeleton,
    IntercityLeg,
    LogisticsPlan,
    StayAllocation,
)
from domain_contracts.recommendations import (
    CityRecommendations,
    RecommendationItem,
    Recommendations,
)
from domain_contracts.revision import RevisionRequest
from domain_contracts.trip_brief import TripBrief, TripConstraints

__all__ = [
    "BudgetCategoryBreakdown",
    "BudgetFlag",
    "BudgetReport",
    "CityRecommendations",
    "DayBlock",
    "DaySkeleton",
    "IntercityLeg",
    "Itinerary",
    "ItineraryDay",
    "LogisticsPlan",
    "RecommendationItem",
    "Recommendations",
    "RevisionRequest",
    "StayAllocation",
    "TripBrief",
    "TripConstraints",
]
