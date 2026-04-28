"""Tool registry for Phase 2."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from tools.currency_conversion import FxConvertTool
from tools.hotel_search import HotelsSearchTool
from tools.intercity_transit_search import TransitSearchTool
from tools.maps_distance import MapsDistanceTool
from tools.price_estimate import PriceEstimateTool
from tools.tool_runtime import BaseTool, ToolConfig, ToolMode
from tools.vector_search import VectorSearchTool
from tools.web_search import WebSearchTool

ToolName = Literal[
    "web_search",
    "vector_search",
    "maps_distance",
    "hotels_search",
    "transit_search",
    "fx_convert",
    "price_estimate",
]


class ToolRegistry:
    """Lookup and invoke typed tools via a uniform API."""

    def __init__(
        self,
        *,
        mode: ToolMode = ToolMode.MOCK,
        base_config: ToolConfig | None = None,
    ) -> None:
        config = base_config or ToolConfig(mode=mode)
        self._tools: dict[str, BaseTool[BaseModel, BaseModel]] = {}
        for tool in (
            WebSearchTool(config),
            VectorSearchTool(config),
            MapsDistanceTool(config),
            HotelsSearchTool(config),
            TransitSearchTool(config),
            FxConvertTool(config),
            PriceEstimateTool(config),
        ):
            self.register(tool)

    def register(self, tool: BaseTool[BaseModel, BaseModel]) -> None:
        self._tools[tool.name] = tool

    def get(self, name: ToolName) -> BaseTool[BaseModel, BaseModel]:
        try:
            return self._tools[name]
        except KeyError as exc:
            available = ", ".join(sorted(self._tools))
            raise KeyError(f"Unknown tool '{name}'. Available tools: {available}") from exc

    def call(self, name: ToolName, payload: dict[str, object]) -> BaseModel:
        tool = self.get(name)
        return tool.execute(payload)

    def list_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))
