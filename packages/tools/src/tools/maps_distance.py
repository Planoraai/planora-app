"""Maps distance/time estimate tool."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool

TransitMode = Literal["walk", "transit", "train", "taxi"]


class MapsDistanceRequest(BaseModel):
    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    mode: TransitMode = "transit"


class MapsDistanceResponse(BaseModel):
    origin: str
    destination: str
    mode: TransitMode
    distance_km: float = Field(ge=0)
    duration_minutes: int = Field(ge=1)


class MapsDistanceTool(BaseTool[MapsDistanceRequest, MapsDistanceResponse]):
    name = "maps_distance"
    request_model = MapsDistanceRequest
    response_model = MapsDistanceResponse

    def _run_mock(self, request: MapsDistanceRequest) -> MapsDistanceResponse:
        seed = len(request.origin) * 7 + len(request.destination) * 11
        mode_factor = {"walk": 12, "transit": 4, "train": 3, "taxi": 3.5}[request.mode]
        distance_km = round((seed % 70) + 5.0, 1)
        duration_minutes = max(10, int((distance_km * mode_factor) + (seed % 15)))
        return MapsDistanceResponse(
            origin=request.origin,
            destination=request.destination,
            mode=request.mode,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
        )
