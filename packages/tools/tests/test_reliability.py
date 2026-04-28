"""Phase 2 reliability tests for retries and cache behavior."""

from __future__ import annotations

import time

from pydantic import BaseModel
from tools.tool_runtime import (
    BaseTool,
    ToolConfig,
    ToolConfigurationError,
    ToolError,
    ToolPayloadError,
    ToolTimeoutError,
)


class _RetryRequest(BaseModel):
    value: int


class _RetryResponse(BaseModel):
    value: int
    source: str


class _FlakyTool(BaseTool[_RetryRequest, _RetryResponse]):
    name = "flaky_tool"
    request_model = _RetryRequest
    response_model = _RetryResponse

    def __init__(self, failures_before_success: int, config: ToolConfig) -> None:
        super().__init__(config)
        self._remaining_failures = failures_before_success

    def _run_mock(self, request: _RetryRequest) -> _RetryResponse:
        if self._remaining_failures > 0:
            self._remaining_failures -= 1
            raise RuntimeError("temporary failure")
        return _RetryResponse(value=request.value, source="mock")


def test_retry_eventually_succeeds_within_retry_budget() -> None:
    tool = _FlakyTool(
        failures_before_success=1,
        config=ToolConfig(max_retries=2, retry_backoff_seconds=0, cache_ttl_seconds=120),
    )

    result = tool.execute({"value": 7})

    assert result.value == 7
    assert tool.stats.attempts == 2


def test_retry_exhaustion_raises_tool_error() -> None:
    tool = _FlakyTool(
        failures_before_success=3,
        config=ToolConfig(max_retries=1, retry_backoff_seconds=0, cache_ttl_seconds=120),
    )

    try:
        tool.execute({"value": 7})
    except ToolError as exc:
        assert "failed after 2 attempts" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ToolError when retries are exhausted")


class _CachedTool(BaseTool[_RetryRequest, _RetryResponse]):
    name = "cached_tool"
    request_model = _RetryRequest
    response_model = _RetryResponse

    def __init__(self, config: ToolConfig) -> None:
        super().__init__(config)
        self.execution_count = 0

    def _run_mock(self, request: _RetryRequest) -> _RetryResponse:
        self.execution_count += 1
        return _RetryResponse(value=request.value, source="mock")


def test_cache_hit_avoids_second_backend_execution() -> None:
    tool = _CachedTool(ToolConfig(cache_ttl_seconds=300, retry_backoff_seconds=0))

    first = tool.execute({"value": 5})
    second = tool.execute({"value": 5})

    assert first == second
    assert tool.execution_count == 1
    assert tool.stats.cache_hits == 1


class _BadPayloadTool(BaseTool[_RetryRequest, _RetryResponse]):
    name = "bad_payload_tool"
    request_model = _RetryRequest
    response_model = _RetryResponse

    def _run_mock(self, request: _RetryRequest) -> dict[str, object]:
        del request
        return {"unexpected": "shape"}


class _SlowTool(BaseTool[_RetryRequest, _RetryResponse]):
    name = "slow_tool"
    request_model = _RetryRequest
    response_model = _RetryResponse

    def _run_mock(self, request: _RetryRequest) -> _RetryResponse:
        del request
        return _RetryResponse(value=1, source="mock")

    def _call_backend(self, request: _RetryRequest) -> _RetryResponse:
        del request
        raise TimeoutError("simulated timeout")


def test_payload_validation_errors_raise_typed_tool_payload_error() -> None:
    tool = _BadPayloadTool(ToolConfig(max_retries=0, retry_backoff_seconds=0))
    try:
        tool.execute({"value": 10})
    except ToolPayloadError as exc:
        assert "invalid payload" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ToolPayloadError for invalid payload")


def test_timeout_maps_to_typed_timeout_error() -> None:
    tool = _SlowTool(ToolConfig(max_retries=0, retry_backoff_seconds=0))
    try:
        tool.execute({"value": 10})
    except ToolTimeoutError as exc:
        assert "exceeded timeout" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ToolTimeoutError for simulated timeout")


class _SleepyTool(BaseTool[_RetryRequest, _RetryResponse]):
    name = "sleepy_tool"
    request_model = _RetryRequest
    response_model = _RetryResponse

    def _run_mock(self, request: _RetryRequest) -> _RetryResponse:
        time.sleep(0.05)
        return _RetryResponse(value=request.value, source="mock")


def test_timeout_interrupts_slow_backend_execution() -> None:
    tool = _SleepyTool(
        ToolConfig(timeout_seconds=0.01, max_retries=0, retry_backoff_seconds=0),
    )
    started = time.monotonic()
    try:
        tool.execute({"value": 11})
    except ToolTimeoutError as exc:
        elapsed = time.monotonic() - started
        assert "exceeded timeout" in str(exc)
        assert elapsed < 0.06
    else:  # pragma: no cover
        raise AssertionError("Expected ToolTimeoutError for slow backend execution")


def test_real_mode_without_real_backend_raises_configuration_error() -> None:
    tool = _CachedTool(ToolConfig(mode="real", max_retries=0, retry_backoff_seconds=0))
    try:
        tool.execute({"value": 1})
    except ToolConfigurationError as exc:
        assert "does not support real mode yet" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected ToolConfigurationError in real mode without backend")
