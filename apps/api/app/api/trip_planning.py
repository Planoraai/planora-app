"""Trip planning API routes for Phase 8 frontend wiring."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from memory import MemoryAwarePlanner
from orchestrator.graph import run_orchestrator
from pydantic import BaseModel, Field
from reliability import HardenedPlannerService

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])
planner = MemoryAwarePlanner(runner=run_orchestrator)
hardening = HardenedPlannerService(planner_callable=planner.run, retry_attempts=2)


class TripPlanRequest(BaseModel):
    prompt: str = Field(min_length=10)
    user_id: str = Field(default="anonymous")
    opt_in_personalization: bool = True


class TripPlanResponse(BaseModel):
    approved: bool
    itinerary: dict[str, object]
    review: dict[str, object]
    run_id: str
    cache_hit: bool
    selected_model: str | None = None


@router.post("/plan", response_model=TripPlanResponse)
async def plan_trip(payload: TripPlanRequest) -> TripPlanResponse:
    result, safety = hardening.run(
        prompt=payload.prompt,
        planner_kwargs={
            "prompt": payload.prompt,
            "user_id": payload.user_id,
            "opt_in_personalization": payload.opt_in_personalization,
        },
    )
    if not safety["ok"]:
        raise HTTPException(
            status_code=503,
            detail={
                "error_type": safety["error_type"],
                "message": safety["message"],
            },
        )
    assert result is not None
    state, metadata = result
    itinerary_payload = state["itinerary"].model_dump(mode="json")
    review_payload = state["revision_request"].model_dump(mode="json")
    return TripPlanResponse(
        approved=bool(state["revision_request"].approved),
        itinerary=itinerary_payload,
        review=review_payload,
        run_id=str(metadata["run_id"]),
        cache_hit=bool(metadata["cache_hit"]),
        selected_model=safety.get("selected_model"),
    )
