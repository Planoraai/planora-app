"""Defaults for API integration tests (complements packages/platform/tests)."""

from __future__ import annotations

import os


def pytest_configure(config: object) -> None:
    os.environ.setdefault("MOCK_MODE", "true")
    os.environ.setdefault("APP_ENV", "test")
    os.environ.setdefault("LOG_JSON", "false")
    os.environ.setdefault("LOG_LEVEL", "WARNING")
