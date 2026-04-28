"""HTTP routers mounted by phase packages (Phase 0 health routes live in `phase0`)."""

from __future__ import annotations

from app.api.trip_planning import router as trip_planning_router

__all__ = ["trip_planning_router"]
