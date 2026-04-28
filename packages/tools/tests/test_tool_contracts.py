"""Phase 2 tool contract tests for mode behavior and typed outputs."""

from __future__ import annotations

import pytest
from tools import ToolConfig, ToolMode, ToolRegistry
from tools.tool_runtime import ToolConfigurationError


@pytest.mark.parametrize(
    ("tool_name", "payload"),
    [
        ("web_search", {"query": "kyoto temples", "limit": 2}),
        (
            "vector_search",
            {"query": "quiet neighborhoods in tokyo", "top_k": 3, "namespace": "travel"},
        ),
        (
            "maps_distance",
            {"origin": "Tokyo Station", "destination": "Senso-ji", "mode": "transit"},
        ),
        (
            "hotels_search",
            {"city": "Kyoto", "nights": 2, "adults": 2, "max_results": 2, "currency": "USD"},
        ),
        (
            "transit_search",
            {
                "origin_city": "Tokyo",
                "destination_city": "Kyoto",
                "max_results": 2,
                "currency": "USD",
            },
        ),
        ("fx_convert", {"amount": 100.0, "from_currency": "USD", "to_currency": "JPY"}),
        ("price_estimate", {"city": "Osaka", "category": "food", "currency": "USD"}),
    ],
)
def test_mock_mode_returns_response_model_for_each_registered_tool(
    tool_name: str,
    payload: dict[str, object],
) -> None:
    registry = ToolRegistry(mode=ToolMode.MOCK)
    tool = registry.get(tool_name)  # type: ignore[arg-type]
    response = registry.call(tool_name, payload)  # type: ignore[arg-type]
    # Tool execute() should always return an instance of the declared response model.
    assert isinstance(response, tool.response_model)


@pytest.mark.parametrize(
    ("tool_name", "payload"),
    [
        ("web_search", {"query": "kyoto temples", "limit": 2}),
        (
            "vector_search",
            {"query": "quiet neighborhoods in tokyo", "top_k": 3, "namespace": "travel"},
        ),
        (
            "maps_distance",
            {"origin": "Tokyo Station", "destination": "Senso-ji", "mode": "transit"},
        ),
        (
            "hotels_search",
            {"city": "Kyoto", "nights": 2, "adults": 2, "max_results": 2, "currency": "USD"},
        ),
        (
            "transit_search",
            {
                "origin_city": "Tokyo",
                "destination_city": "Kyoto",
                "max_results": 2,
                "currency": "USD",
            },
        ),
        ("fx_convert", {"amount": 100.0, "from_currency": "USD", "to_currency": "JPY"}),
        ("price_estimate", {"city": "Osaka", "category": "food", "currency": "USD"}),
    ],
)
def test_real_mode_without_integration_fails_explicitly(
    tool_name: str,
    payload: dict[str, object],
) -> None:
    registry = ToolRegistry(base_config=ToolConfig(mode=ToolMode.REAL, max_retries=0))
    with pytest.raises(ToolConfigurationError):
        registry.call(tool_name, payload)  # type: ignore[arg-type]
