"""Hotel search and pricing tool."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool


class HotelsSearchRequest(BaseModel):
    city: str = Field(min_length=2)
    nights: int = Field(default=1, ge=1, le=30)
    adults: int = Field(default=2, ge=1, le=8)
    max_results: int = Field(default=3, ge=1, le=8)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class HotelOption(BaseModel):
    name: str
    neighborhood: str
    nightly_rate: float = Field(ge=0)
    total_estimate: float = Field(ge=0)
    currency: str


class HotelsSearchResponse(BaseModel):
    city: str
    options: list[HotelOption] = Field(default_factory=list)


class HotelsSearchTool(BaseTool[HotelsSearchRequest, HotelsSearchResponse]):
    name = "hotels_search"
    request_model = HotelsSearchRequest
    response_model = HotelsSearchResponse

    def _run_mock(self, request: HotelsSearchRequest) -> HotelsSearchResponse:
        base = 60 + (len(request.city) * 4) + (request.adults * 8)
        options = [
            HotelOption(
                name=f"{request.city} Stay {idx}",
                neighborhood=f"Area {idx}",
                nightly_rate=round(base + (idx * 18), 2),
                total_estimate=round((base + (idx * 18)) * request.nights, 2),
                currency=request.currency.upper(),
            )
            for idx in range(1, request.max_results + 1)
        ]
        return HotelsSearchResponse(city=request.city, options=options)
