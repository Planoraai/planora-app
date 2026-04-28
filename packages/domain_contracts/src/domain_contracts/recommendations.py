"""Destination-research output contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Priority = Literal["must_do", "nice_to_have"]
CrowdLevel = Literal["low", "medium", "high"]


class RecommendationItem(BaseModel):
    """One recommended spot/experience/food item."""

    name: str = Field(min_length=2)
    why: str = Field(min_length=2)
    tags: list[str] = Field(default_factory=list)
    crowd_level: CrowdLevel = "medium"
    priority: Priority = "nice_to_have"


class CityRecommendations(BaseModel):
    """Recommendations grouped by city and category."""

    neighborhoods: list[RecommendationItem] = Field(default_factory=list)
    experiences: list[RecommendationItem] = Field(default_factory=list)
    food: list[RecommendationItem] = Field(default_factory=list)


class Recommendations(BaseModel):
    """Top-level map: city name -> recommendation bundle."""

    cities: dict[str, CityRecommendations] = Field(default_factory=dict)
