"""ASGI entrypoint: composes the platform shell with domain routers."""

from __future__ import annotations

from app_platform.application_factory import create_app

from app.api import trip_planning_router

app = create_app()
app.include_router(trip_planning_router)
