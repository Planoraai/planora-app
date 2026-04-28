"""Web search tool."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool


class WebSearchRequest(BaseModel):
    query: str = Field(min_length=3)
    limit: int = Field(default=5, ge=1, le=10)


class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str = "web"


class WebSearchResponse(BaseModel):
    query: str
    results: list[WebSearchResult] = Field(default_factory=list)


class WebSearchTool(BaseTool[WebSearchRequest, WebSearchResponse]):
    name = "web_search"
    request_model = WebSearchRequest
    response_model = WebSearchResponse

    def _run_mock(self, request: WebSearchRequest) -> WebSearchResponse:
        base_slug = request.query.lower().replace(" ", "-")
        results = [
            WebSearchResult(
                title=f"{request.query.title()} guide #{idx}",
                url=f"https://example.com/{base_slug}/{idx}",
                snippet=f"Mock web snippet {idx} for {request.query}.",
            )
            for idx in range(1, request.limit + 1)
        ]
        return WebSearchResponse(query=request.query, results=results)
