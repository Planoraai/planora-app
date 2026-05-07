"""FastAPI application factory: builds the ASGI app with logging, correlation IDs, CORS, health routes."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app_platform import __version__
from app_platform.application_settings import settings
from app_platform.health_routes import router as health_router
from app_platform.request_correlation import CorrelationIdMiddleware
from app_platform.structured_logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    log = get_logger(__name__)
    log.info(
        "app.startup",
        version=__version__,
        env=settings.app_env,
        mock_mode=settings.mock_mode,
    )
    yield
    log.info("app.shutdown")


def create_app() -> FastAPI:
    configure_logging()
    _configure_sentry()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "AI Travel Planner - multi-agent system that turns a short travel "
            "request into a complete day-by-day itinerary."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Correlation-ID"],
    )

    app.include_router(health_router, tags=["health"])

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, Any]:
        return {
            "service": settings.app_name,
            "version": __version__,
            "env": settings.app_env,
            "docs": "/docs",
        }

    return app


def _configure_sentry() -> None:
    if not settings.sentry_dsn:
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn.get_secret_value(),
        environment=settings.app_env,
        release=settings.app_version,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
    )
