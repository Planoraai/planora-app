"""Final synthesized itinerary contract."""

from __future__ import annotations

from pydantic import BaseModel, Field

from domain_contracts.budget import BudgetReport
from domain_contracts.logistics import LogisticsPlan
from domain_contracts.recommendations import Recommendations
from domain_contracts.trip_brief import TripBrief


class ItineraryDay(BaseModel):
    day: int = Field(ge=1)
    city: str = Field(min_length=2)
    summary: str = Field(min_length=2)
    highlights: list[str] = Field(default_factory=list)


class Itinerary(BaseModel):
    title: str = Field(min_length=2)
    trip_brief: TripBrief
    recommendations: Recommendations
    logistics_plan: LogisticsPlan
    budget_report: BudgetReport
    day_by_day: list[ItineraryDay] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
