"""Phase 10 hardening primitives for resilience and cost control."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class PlannerCallable(Protocol):
    """Protocol for planner invocation."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


@dataclass(slots=True)
class ModelTierPolicy:
    """Simple model tiering policy for cost control."""

    reasoning_model: str = "gpt-4o"
    cheap_model: str = "gpt-4o-mini"

    def choose_model(self, *, prompt: str, cache_hit: bool) -> str:
        if cache_hit:
            return self.cheap_model
        if len(prompt) > 220 or "budget" in prompt.lower() or "constraints" in prompt.lower():
            return self.reasoning_model
        return self.cheap_model


@dataclass(slots=True)
class CircuitBreaker:
    """Fail-fast guard around unstable dependencies."""

    failure_threshold: int = 3
    recovery_window_seconds: float = 30.0
    failure_count: int = 0
    opened_at: float | None = None

    def allow_request(self) -> bool:
        if self.opened_at is None:
            return True
        if monotonic() - self.opened_at >= self.recovery_window_seconds:
            self.failure_count = 0
            self.opened_at = None
            return True
        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = monotonic()

    @property
    def is_open(self) -> bool:
        return self.opened_at is not None and not self.allow_request()


def with_retry(func: Callable[[], T], *, attempts: int = 2) -> T:
    """Retry helper with bounded attempts."""
    last_exc: Exception | None = None
    for _ in range(max(1, attempts)):
        try:
            return func()
        except Exception as exc:  # pragma: no cover - exercised in tests
            last_exc = exc
    assert last_exc is not None
    raise last_exc


@dataclass(slots=True)
class HardenedPlannerService:
    """Planner wrapper adding circuit-breaker, retries, and response metadata."""

    planner_callable: PlannerCallable
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    model_policy: ModelTierPolicy = field(default_factory=ModelTierPolicy)
    retry_attempts: int = 2
    max_latency_seconds: float | None = 12.0

    def run(
        self, *, prompt: str, planner_kwargs: dict[str, Any]
    ) -> tuple[Any | None, dict[str, Any]]:
        if not self.circuit_breaker.allow_request():
            return None, {
                "ok": False,
                "error_type": "circuit_open",
                "message": "Planner temporarily unavailable due to repeated failures.",
            }

        selected_model = self.model_policy.choose_model(
            prompt=prompt,
            cache_hit=False,
        )

        started = monotonic()
        try:
            result = with_retry(
                lambda: self.planner_callable(**planner_kwargs),
                attempts=self.retry_attempts,
            )
            elapsed = monotonic() - started
            if self.max_latency_seconds is not None and elapsed > self.max_latency_seconds:
                self.circuit_breaker.record_failure()
                return None, {
                    "ok": False,
                    "error_type": "latency_budget_exceeded",
                    "message": (
                        f"Planner exceeded latency budget: {elapsed:.2f}s "
                        f"> {self.max_latency_seconds:.2f}s"
                    ),
                    "selected_model": selected_model,
                }
            validation_error = self._validate_result_shape(result)
            if validation_error is not None:
                self.circuit_breaker.record_failure()
                return None, {
                    "ok": False,
                    "error_type": "invalid_planner_result",
                    "message": validation_error,
                    "selected_model": selected_model,
                }
            self.circuit_breaker.record_success()
            return result, {"ok": True, "selected_model": selected_model}
        except Exception as exc:
            self.circuit_breaker.record_failure()
            return None, {
                "ok": False,
                "error_type": "planner_failure",
                "message": str(exc),
                "selected_model": selected_model,
            }

    def _validate_result_shape(self, result: Any) -> str | None:
        if not isinstance(result, tuple) or len(result) != 2:
            return "Planner must return a tuple of (state, metadata)."
        state, metadata = result
        if not isinstance(state, dict):
            return "Planner state payload must be a dictionary."
        if "revision_request" not in state:
            return "Planner state missing required 'revision_request'."
        if "itinerary" not in state:
            return "Planner state missing required 'itinerary'."
        if not isinstance(metadata, dict):
            return "Planner metadata payload must be a dictionary."
        return None
