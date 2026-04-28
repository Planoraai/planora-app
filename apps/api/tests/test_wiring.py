"""Ensure the integration shell exposes the Phase 0 ASGI app."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_app_is_fastapi_with_health_routes() -> None:
    assert app.title == "ai-travel-planner"
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/healthz" in paths
    assert "/readyz" in paths
    assert "/api/v1/trips/plan" in paths


def test_trip_plan_endpoint_returns_itinerary_payload() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/trips/plan",
            json={
                "prompt": "Plan a 5-day trip to Japan. Tokyo + Kyoto. $3000 budget. Love food and temples.",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert "itinerary" in body
    assert "review" in body
    assert "approved" in body
    assert "selected_model" in body
