"""Phase 10 hardening tests."""

from __future__ import annotations

import time

import pytest
from reliability import CircuitBreaker, HardenedPlannerService, ModelTierPolicy, with_retry


def test_model_tier_policy_prefers_cheap_for_short_prompt() -> None:
    policy = ModelTierPolicy(reasoning_model="r", cheap_model="c")
    assert policy.choose_model(prompt="short prompt", cache_hit=False) == "c"
    assert policy.choose_model(prompt="anything", cache_hit=True) == "c"
    assert (
        policy.choose_model(prompt="long constraints and budget planning details", cache_hit=False)
        == "r"
    )


def test_circuit_breaker_opens_after_failures() -> None:
    breaker = CircuitBreaker(failure_threshold=2, recovery_window_seconds=100)
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.allow_request() is True
    breaker.record_failure()
    assert breaker.allow_request() is False


def test_with_retry_retries_and_succeeds() -> None:
    calls = {"count": 0}

    def flaky() -> str:
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("temporary")
        return "ok"

    assert with_retry(flaky, attempts=2) == "ok"
    assert calls["count"] == 2


def test_hardened_planner_returns_graceful_error_on_failure() -> None:
    def broken(**_kwargs):
        raise RuntimeError("boom")

    service = HardenedPlannerService(planner_callable=broken, retry_attempts=1)
    result, metadata = service.run(prompt="test", planner_kwargs={"prompt": "x"})
    assert result is None
    assert metadata["ok"] is False
    assert metadata["error_type"] == "planner_failure"


def test_hardened_planner_success_path_returns_selected_model() -> None:
    def ok_runner(**_kwargs):
        return (
            {"itinerary": {"trip": "ok"}, "revision_request": {"approved": True}},
            {"run_id": "run-1", "cache_hit": False},
        )

    service = HardenedPlannerService(planner_callable=ok_runner, retry_attempts=1)
    result, metadata = service.run(prompt="small prompt", planner_kwargs={"prompt": "x"})
    assert result is not None
    assert metadata["ok"] is True
    assert metadata["selected_model"] is not None


def test_with_retry_raises_after_exhaustion() -> None:
    with pytest.raises(ValueError):
        with_retry(lambda: (_ for _ in ()).throw(ValueError("x")), attempts=2)


def test_hardened_planner_rejects_invalid_partial_result() -> None:
    def partial_runner(**_kwargs):
        return ({"trip": "ok"}, {"run_id": "run-1"})

    service = HardenedPlannerService(planner_callable=partial_runner, retry_attempts=1)
    result, metadata = service.run(prompt="small prompt", planner_kwargs={"prompt": "x"})
    assert result is None
    assert metadata["ok"] is False
    assert metadata["error_type"] == "invalid_planner_result"


def test_hardened_planner_enforces_latency_budget() -> None:
    def slow_runner(**_kwargs):
        time.sleep(0.03)
        return (
            {"itinerary": {"ok": True}, "revision_request": {"approved": True}},
            {"run_id": "run-2", "cache_hit": False},
        )

    service = HardenedPlannerService(
        planner_callable=slow_runner,
        retry_attempts=1,
        max_latency_seconds=0.01,
    )
    result, metadata = service.run(prompt="small prompt", planner_kwargs={"prompt": "x"})
    assert result is None
    assert metadata["ok"] is False
    assert metadata["error_type"] == "latency_budget_exceeded"
