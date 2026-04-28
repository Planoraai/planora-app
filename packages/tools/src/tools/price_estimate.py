"""Heuristic price estimate tool for activities and food."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool

PriceCategory = Literal["food", "activity", "transport_local", "lodging_midrange"]


class PriceEstimateRequest(BaseModel):
    city: str = Field(min_length=2)
    category: PriceCategory
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PriceEstimateResponse(BaseModel):
    city: str
    category: PriceCategory
    min_cost: float = Field(ge=0)
    max_cost: float = Field(ge=0)
    confidence: Literal["low", "medium", "high"] = "medium"
    currency: str


class PriceEstimateTool(BaseTool[PriceEstimateRequest, PriceEstimateResponse]):
    name = "price_estimate"
    request_model = PriceEstimateRequest
    response_model = PriceEstimateResponse

    def _run_mock(self, request: PriceEstimateRequest) -> PriceEstimateResponse:
        bands: dict[PriceCategory, tuple[float, float]] = {
            "food": (12.0, 40.0),
            "activity": (10.0, 55.0),
            "transport_local": (3.0, 18.0),
            "lodging_midrange": (70.0, 180.0),
        }
        base_min, base_max = bands[request.category]
        city_adjust = (len(request.city) % 5) * 1.5
        return PriceEstimateResponse(
            city=request.city,
            category=request.category,
            min_cost=round(base_min + city_adjust, 2),
            max_cost=round(base_max + (city_adjust * 2), 2),
            confidence="medium",
            currency=request.currency.upper(),
        )
