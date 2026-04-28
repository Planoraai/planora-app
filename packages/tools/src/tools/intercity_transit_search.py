"""Transit search and rough pricing tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool

TransitOptionMode = Literal["train", "bus", "flight"]


class TransitSearchRequest(BaseModel):
    origin_city: str = Field(min_length=2)
    destination_city: str = Field(min_length=2)
    date_hint: str | None = None
    max_results: int = Field(default=3, ge=1, le=8)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class TransitOption(BaseModel):
    mode: TransitOptionMode
    provider: str
    duration_minutes: int = Field(ge=1)
    estimated_price: float = Field(ge=0)
    currency: str


class TransitSearchResponse(BaseModel):
    origin_city: str
    destination_city: str
    options: list[TransitOption] = Field(default_factory=list)


class TransitSearchTool(BaseTool[TransitSearchRequest, TransitSearchResponse]):
    name = "transit_search"
    request_model = TransitSearchRequest
    response_model = TransitSearchResponse

    def _run_mock(self, request: TransitSearchRequest) -> TransitSearchResponse:
        trip_length = len(request.origin_city) + len(request.destination_city)
        seed_price = 20 + (trip_length * 6)
        seed_duration = 80 + (trip_length * 10)
        modes: list[TransitOptionMode] = ["train", "bus", "flight"]
        options = [
            TransitOption(
                mode=modes[(idx - 1) % len(modes)],
                provider=f"Provider {idx}",
                duration_minutes=seed_duration + (idx * 25),
                estimated_price=round(seed_price + (idx * 18), 2),
                currency=request.currency.upper(),
            )
            for idx in range(1, request.max_results + 1)
        ]
        return TransitSearchResponse(
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            options=options,
        )
