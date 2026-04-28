"""Typed tool layer: `BaseTool`, `ToolRegistry`, and every concrete tool wrapper.

Each tool exposes typed Pydantic request/response models, runs in mock or real mode,
applies retries with backoff, caches successful responses, and enforces a real
ThreadPoolExecutor-based timeout (not just elapsed-time measurement).
"""

from __future__ import annotations

from tools.currency_conversion import FxConvertRequest, FxConvertResponse, FxConvertTool
from tools.hotel_search import (
    HotelOption,
    HotelsSearchRequest,
    HotelsSearchResponse,
    HotelsSearchTool,
)
from tools.intercity_transit_search import (
    TransitSearchRequest,
    TransitSearchResponse,
    TransitSearchTool,
)
from tools.maps_distance import MapsDistanceRequest, MapsDistanceResponse, MapsDistanceTool
from tools.price_estimate import (
    PriceEstimateRequest,
    PriceEstimateResponse,
    PriceEstimateTool,
)
from tools.registry import ToolRegistry
from tools.tool_runtime import BaseTool, ToolConfig, ToolError, ToolMode
from tools.vector_search import VectorSearchRequest, VectorSearchResponse, VectorSearchTool
from tools.web_search import WebSearchRequest, WebSearchResponse, WebSearchTool

__all__ = [
    "BaseTool",
    "FxConvertRequest",
    "FxConvertResponse",
    "FxConvertTool",
    "HotelOption",
    "HotelsSearchRequest",
    "HotelsSearchResponse",
    "HotelsSearchTool",
    "MapsDistanceRequest",
    "MapsDistanceResponse",
    "MapsDistanceTool",
    "PriceEstimateRequest",
    "PriceEstimateResponse",
    "PriceEstimateTool",
    "ToolConfig",
    "ToolError",
    "ToolMode",
    "ToolRegistry",
    "TransitSearchRequest",
    "TransitSearchResponse",
    "TransitSearchTool",
    "VectorSearchRequest",
    "VectorSearchResponse",
    "VectorSearchTool",
    "WebSearchRequest",
    "WebSearchResponse",
    "WebSearchTool",
]
