"""Structured logging using structlog."""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from app_platform.application_settings import settings
from app_platform.request_correlation import get_correlation_id

_configured = False


def _add_correlation_id(_logger: logging.Logger, _method: str, event_dict: EventDict) -> EventDict:
    cid = get_correlation_id()
    if cid is not None:
        event_dict.setdefault("correlation_id", cid)
    return event_dict


def _add_app_metadata(_logger: logging.Logger, _method: str, event_dict: EventDict) -> EventDict:
    event_dict.setdefault("service", settings.app_name)
    event_dict.setdefault("env", settings.app_env)
    return event_dict


def configure_logging() -> None:
    """Configure stdlib logging + structlog. Idempotent."""
    global _configured
    if _configured:
        return

    log_level = getattr(logging, settings.log_level, logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        _add_correlation_id,
        _add_app_metadata,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_json:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    for noisy in ("httpx", "httpcore", "urllib3", "openai", "anthropic"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str | None = None, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    if not _configured:
        configure_logging()
    logger = structlog.get_logger(name)
    if initial_values:
        logger = logger.bind(**initial_values)
    return logger
