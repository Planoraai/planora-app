"""Pytest defaults for the platform package tests (formerly phase0)."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest


def pytest_configure(config: object) -> None:
    os.environ.setdefault("MOCK_MODE", "true")
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("LOG_JSON", "false")
    os.environ.setdefault("LOG_LEVEL", "WARNING")


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> Iterator[None]:
    from app_platform.application_settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
