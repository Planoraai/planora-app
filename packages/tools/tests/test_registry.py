"""Phase 2 registry and tool happy-path tests."""

from __future__ import annotations

from tools import ToolRegistry
from tools.currency_conversion import FxConvertResponse
from tools.hotel_search import HotelsSearchResponse
from tools.intercity_transit_search import TransitSearchResponse
from tools.maps_distance import MapsDistanceResponse
from tools.price_estimate import PriceEstimateResponse
from tools.vector_search import VectorSearchResponse
from tools.web_search import WebSearchResponse


def test_registry_lists_expected_tools() -> None:
    registry = ToolRegistry()
    assert registry.list_tools() == (
        "fx_convert",
        "hotels_search",
        "maps_distance",
        "price_estimate",
        "transit_search",
        "vector_search",
        "web_search",
    )


def test_registry_runs_all_tools_with_typed_outputs() -> None:
    registry = ToolRegistry()

    web_result = registry.call("web_search", {"query": "kyoto temples", "limit": 2})
    assert isinstance(web_result, WebSearchResponse)
    assert len(web_result.results) == 2

    vector_result = registry.call(
        "vector_search",
        {"query": "quiet neighborhoods in tokyo", "top_k": 3, "namespace": "travel"},
    )
    assert isinstance(vector_result, VectorSearchResponse)
    assert len(vector_result.matches) == 3

    maps_result = registry.call(
        "maps_distance",
        {"origin": "Tokyo Station", "destination": "Senso-ji", "mode": "transit"},
    )
    assert isinstance(maps_result, MapsDistanceResponse)
    assert maps_result.duration_minutes > 0

    hotels_result = registry.call(
        "hotels_search",
        {"city": "Kyoto", "nights": 2, "adults": 2, "max_results": 2, "currency": "USD"},
    )
    assert isinstance(hotels_result, HotelsSearchResponse)
    assert len(hotels_result.options) == 2

    transit_result = registry.call(
        "transit_search",
        {
            "origin_city": "Tokyo",
            "destination_city": "Kyoto",
            "max_results": 2,
            "currency": "USD",
        },
    )
    assert isinstance(transit_result, TransitSearchResponse)
    assert len(transit_result.options) == 2

    fx_result = registry.call(
        "fx_convert",
        {"amount": 100.0, "from_currency": "USD", "to_currency": "JPY"},
    )
    assert isinstance(fx_result, FxConvertResponse)
    assert fx_result.converted_amount > 100.0

    estimate_result = registry.call(
        "price_estimate",
        {"city": "Osaka", "category": "food", "currency": "USD"},
    )
    assert isinstance(estimate_result, PriceEstimateResponse)
    assert estimate_result.max_cost >= estimate_result.min_cost


def test_registry_unknown_tool_raises_helpful_error() -> None:
    registry = ToolRegistry()
    try:
        registry.call("web_seach", {"query": "x"})  # type: ignore[arg-type]
    except KeyError as exc:
        assert "Unknown tool" in str(exc)
        assert "web_search" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected KeyError for unknown tool name")
