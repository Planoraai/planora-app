"""Budget-agent output contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BudgetCategoryBreakdown(BaseModel):
    stay: float = Field(ge=0)
    transport: float = Field(ge=0)
    food: float = Field(ge=0)
    activities: float = Field(ge=0)
    buffer: float = Field(ge=0)


class BudgetFlag(BaseModel):
    issue: str = Field(min_length=2)
    suggestion: str = Field(min_length=2)


class BudgetReport(BaseModel):
    total_estimate_usd: float = Field(ge=0)
    by_category: BudgetCategoryBreakdown
    flags: list[BudgetFlag] = Field(default_factory=list)
    within_budget: bool
