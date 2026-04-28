"""Tests for app_platform.structured_logging and app_platform.request_correlation."""

from __future__ import annotations

from app_platform.request_correlation import (
    get_correlation_id,
    new_correlation_id,
    set_correlation_id,
)
from app_platform.structured_logging import configure_logging, get_logger


def test_configure_logging_is_idempotent() -> None:
    configure_logging()
    configure_logging()
    log = get_logger("test")
    log.info("platform.smoke")


def test_correlation_id_roundtrip() -> None:
    cid = new_correlation_id()
    set_correlation_id(cid)
    assert get_correlation_id() == cid


def test_new_correlation_ids_are_unique() -> None:
    a = new_correlation_id()
    b = new_correlation_id()
    assert a != b
    assert len(a) == 32
