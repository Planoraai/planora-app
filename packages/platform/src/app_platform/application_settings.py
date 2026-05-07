"""Typed application configuration loaded from environment / .env file.

Loads `.env` from the current working directory (run `uvicorn` from `apps/api/`
so `apps/api/.env` is picked up; see `packages/platform/.env.example` for names).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
VectorDB = Literal["chroma", "qdrant", "pinecone"]


class Settings(BaseSettings):
    """All runtime configuration, loaded once at startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: Environment = "development"
    app_name: str = "ai-travel-planner"
    app_version: str = "0.1.0"
    log_level: LogLevel = "INFO"
    log_json: bool = True
    mock_mode: bool = True

    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    google_api_key: SecretStr | None = None

    llm_reasoning_model: str = "gpt-4o"
    llm_cheap_model: str = "gpt-4o-mini"

    tavily_api_key: SecretStr | None = None
    serpapi_api_key: SecretStr | None = None
    google_maps_api_key: SecretStr | None = None
    amadeus_api_key: SecretStr | None = None
    amadeus_api_secret: SecretStr | None = None
    rapidapi_key: SecretStr | None = None
    exchangerate_api_key: SecretStr | None = None

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/travel_planner"

    vector_db: VectorDB = "chroma"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: SecretStr | None = None
    pinecone_api_key: SecretStr | None = None
    pinecone_env: str | None = None

    langsmith_api_key: SecretStr | None = None
    langsmith_project: str = "ai-travel-planner"
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    sentry_dsn: SecretStr | None = None
    sentry_traces_sample_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    sentry_profiles_sample_rate: float = Field(default=0.0, ge=0.0, le=1.0)

    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_cors_origins: str = "http://localhost:3000"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    @field_validator("api_cors_origins")
    @classmethod
    def _strip_cors(cls, v: str) -> str:
        return v.strip()

    @field_validator(
        "openai_api_key",
        "anthropic_api_key",
        "google_api_key",
        "tavily_api_key",
        "serpapi_api_key",
        "google_maps_api_key",
        "amadeus_api_key",
        "amadeus_api_secret",
        "rapidapi_key",
        "exchangerate_api_key",
        "qdrant_api_key",
        "pinecone_api_key",
        "langsmith_api_key",
        "langfuse_public_key",
        "langfuse_secret_key",
        "sentry_dsn",
        mode="before",
    )
    @classmethod
    def _empty_secret_to_none(cls, value: SecretStr | str | None) -> SecretStr | None:
        if value is None:
            return None
        if isinstance(value, SecretStr):
            raw = value.get_secret_value().strip()
            return None if raw == "" else SecretStr(raw)
        if isinstance(value, str):
            raw = value.strip()
            return None if raw == "" else SecretStr(raw)
        return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
