"""Liveness (`/healthz`) and readiness (`/readyz`) HTTP routes mounted on every API process."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app_platform import __version__
from app_platform.application_settings import settings

router = APIRouter()


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": __version__,
        "env": settings.app_env,
    }


@router.get("/readyz", status_code=status.HTTP_200_OK)
async def readyz() -> dict[str, Any]:
    checks = _run_readiness_checks()
    if any(value != "ok" for value in checks.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not_ready", "checks": checks},
        )
    return {
        "status": "ready",
        "checks": checks,
    }


def _run_readiness_checks() -> dict[str, str]:
    checks: dict[str, str] = {"config": "ok", "orchestrator": "ok", "tool_registry": "ok"}
    try:
        from orchestrator.graph import run_orchestrator

        _ = run_orchestrator
    except Exception:
        checks["orchestrator"] = "error"

    try:
        from tools import ToolRegistry

        _ = ToolRegistry().list_tools()
    except Exception:
        checks["tool_registry"] = "error"
    return checks
