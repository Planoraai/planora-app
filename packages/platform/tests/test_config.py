"""Tests for app_platform.application_settings."""

from __future__ import annotations

import pytest
from app_platform.application_settings import Settings, get_settings


def test_defaults_are_safe_for_tests() -> None:
    s = get_settings()
    assert s.app_env == "test"
    assert s.mock_mode is True
    assert s.is_test is True
    assert s.is_production is False


def test_cors_origins_list_splits_comma_separated() -> None:
    s = Settings(api_cors_origins="http://a.com, http://b.com ,http://c.com")
    assert s.cors_origins_list == ["http://a.com", "http://b.com", "http://c.com"]


def test_invalid_port_is_rejected() -> None:
    with pytest.raises(ValueError):
        Settings(api_port=70000)


def test_secret_keys_default_to_none() -> None:
    s = get_settings()
    assert s.openai_api_key is None
    assert s.anthropic_api_key is None
