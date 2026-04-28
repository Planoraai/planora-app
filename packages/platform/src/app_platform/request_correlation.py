"""Correlation-ID tracking for end-to-end traceability."""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_ID_HEADER = "X-Correlation-ID"

_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def set_correlation_id(value: str) -> None:
    _correlation_id.set(value)


def new_correlation_id() -> str:
    return uuid.uuid4().hex


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Inject and propagate a correlation ID for every HTTP request."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        cid = request.headers.get(CORRELATION_ID_HEADER) or new_correlation_id()
        token = _correlation_id.set(cid)
        try:
            response = await call_next(request)
        finally:
            _correlation_id.reset(token)
        response.headers[CORRELATION_ID_HEADER] = cid
        return response
