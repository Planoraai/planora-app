"""Trip request canonical model produced by the parser."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class TripConstraints(BaseModel):
    """Hard constraints used by planner and validator."""

    max_intercity_transfers: int = Field(default=1, ge=0)


class TripBrief(BaseModel):
    """Structured representation of the user travel request."""

    destination_country: str = Field(min_length=2)
    cities: list[str] = Field(default_factory=list, min_length=1)
    duration_days: int = Field(ge=1)
    budget_usd: float = Field(gt=0)
    preferences: list[str] = Field(default_factory=list)
    avoidances: list[str] = Field(default_factory=list)
    travelers: int = Field(default=1, ge=1)
    start_date: date | None = None
    constraints: TripConstraints = Field(default_factory=TripConstraints)

    @field_validator("destination_country")
    @classmethod
    def _normalize_country(cls, value: str) -> str:
        return value.strip().title()

    @field_validator("cities")
    @classmethod
    def _normalize_cities(cls, value: list[str]) -> list[str]:
        cleaned = [city.strip().title() for city in value if city.strip()]
        if not cleaned:
            raise ValueError("cities must contain at least one value")
        return cleaned

    @field_validator("preferences", "avoidances")
    @classmethod
    def _normalize_tags(cls, value: list[str]) -> list[str]:
        return [tag.strip().lower() for tag in value if tag.strip()]

    @field_validator("start_date")
    @classmethod
    def _validate_start_date_not_past(cls, value: date | None) -> date | None:
        if value is None:
            return None
        if value < date.today():
            raise ValueError("start_date cannot be in the past")
        return value
