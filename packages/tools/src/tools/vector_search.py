"""Vector/KB search tool."""

from __future__ import annotations

from pydantic import BaseModel, Field

from tools.tool_runtime import BaseTool


class VectorSearchRequest(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    namespace: str = Field(default="travel", min_length=2)


class VectorMatch(BaseModel):
    doc_id: str
    text: str
    score: float = Field(ge=0, le=1)


class VectorSearchResponse(BaseModel):
    query: str
    namespace: str
    matches: list[VectorMatch] = Field(default_factory=list)


class VectorSearchTool(BaseTool[VectorSearchRequest, VectorSearchResponse]):
    name = "vector_search"
    request_model = VectorSearchRequest
    response_model = VectorSearchResponse

    def _run_mock(self, request: VectorSearchRequest) -> VectorSearchResponse:
        matches: list[VectorMatch] = []
        for idx in range(request.top_k):
            rank = idx + 1
            score = round(max(0.05, 1 - (idx * 0.12)), 2)
            matches.append(
                VectorMatch(
                    doc_id=f"{request.namespace}-{rank}",
                    text=f"Mock KB note {rank} related to {request.query}.",
                    score=score,
                )
            )
        return VectorSearchResponse(
            query=request.query,
            namespace=request.namespace,
            matches=matches,
        )
