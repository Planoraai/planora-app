"""Logistics-agent output contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class StayAllocation(BaseModel):
    city: str = Field(min_length=2)
    nights: int = Field(ge=1)
    area: str = Field(min_length=2)


class IntercityLeg(BaseModel):
    from_city: str = Field(alias="from", min_length=2)
    to_city: str = Field(alias="to", min_length=2)
    mode: str = Field(min_length=2)
    duration_min: int = Field(ge=1)

    model_config = {"populate_by_name": True}


class DayBlock(BaseModel):
    period: str = Field(min_length=2)
    activity: str = Field(min_length=2)


class DaySkeleton(BaseModel):
    day: int = Field(ge=1)
    city: str = Field(min_length=2)
    blocks: list[DayBlock] = Field(default_factory=list)


class LogisticsPlan(BaseModel):
    stay_plan: list[StayAllocation] = Field(default_factory=list)
    intercity: list[IntercityLeg] = Field(default_factory=list)
    day_skeleton: list[DaySkeleton] = Field(default_factory=list)
