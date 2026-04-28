"""Smoke tests for the platform HTTP surface (root, /healthz, /readyz, correlation IDs)."""

from __future__ import annotations

from app_platform.application_factory import create_app
from fastapi.testclient import TestClient


def test_root_returns_service_metadata() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "ai-travel-planner"
    assert body["env"] == "test"
    assert "version" in body


def test_healthz_returns_ok() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz_returns_ready() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["orchestrator"] == "ok"
    assert response.json()["checks"]["tool_registry"] == "ok"


def test_correlation_id_is_echoed_back() -> None:
    app = create_app()
    cid = "deadbeefcafebabe"
    with TestClient(app) as client:
        response = client.get("/healthz", headers={"X-Correlation-ID": cid})
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == cid


def test_correlation_id_is_generated_when_missing() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    cid = response.headers.get("X-Correlation-ID")
    assert cid is not None
    assert len(cid) >= 16
