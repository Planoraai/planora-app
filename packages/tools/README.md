# `packages/tools/` — Typed tool layer

External-API wrappers exposed to agents through a uniform `BaseTool` contract.

## Reliability features (every tool gets these for free)

- Typed Pydantic request + response models — calls fail fast on bad payloads.
- Mock vs real mode — `MOCK_MODE=true` returns deterministic fixtures, `MOCK_MODE=false` raises `ToolConfigurationError` until a real integration is plugged in.
- Real timeout enforcement — runs the call in a `ThreadPoolExecutor` so a hanging upstream is interrupted, not just measured.
- Retries with backoff (configurable per tool).
- LRU cache on (request_hash) so repeated calls are free in mock mode and inside a run.
- Typed error classes (`ToolTimeoutError`, `ToolRateLimitError`, `ToolUpstreamError`, `ToolPayloadError`, `ToolConfigurationError`) — agents can catch by intent, not regex.

## Tools

| Module | Tool | Purpose |
|---|---|---|
| `web_search.py` | `WebSearchTool` | High-recall destination research |
| `vector_search.py` | `VectorSearchTool` | KB lookup (chroma/qdrant/pinecone selectable in settings) |
| `maps_distance.py` | `MapsDistanceTool` | Pairwise neighbourhood distances |
| `hotel_search.py` | `HotelsSearchTool` | Stay options per city |
| `intercity_transit_search.py` | `TransitSearchTool` | Train / flight / bus options between cities |
| `currency_conversion.py` | `FxConvertTool` | Multi-currency budget normalisation |
| `price_estimate.py` | `PriceEstimateTool` | Per-city per-day cost ranges |
| `registry.py` | `ToolRegistry` | Single entrypoint agents call (`registry.call("web_search", request)`) |
| `tool_runtime.py` | `BaseTool`, `ToolConfig`, `ToolMode`, error hierarchy | Reliability primitives every tool reuses |

## Verify

```bash
cd apps/api
pytest ../../packages/tools/tests -q
```

Originally lived as `phases/phase2/src/phase2/tools/`.
