import os
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from utils import get_project_root

ENV_DIR = get_project_root() / "env"
ENVIRONMENTS = ["development", "staging", "production"]
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ENV_FILE = ENV_DIR / f".env.{ENVIRONMENT}"


class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"  # type: ignore[assignment]
    SERVICE_NAME: str = "pw-admin-backend"
    REDIS_URL: str = "redis://localhost:6379/0"
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318"
    OTEL_EXPORTER_OTLP_HEADERS: str = ""

    model_config = SettingsConfigDict(
        env_file=(ENV_DIR / ".env", ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        validate_default=True,
    )


@lru_cache
def get_settings() -> Settings:
    if ENVIRONMENT not in ENVIRONMENTS:
        raise ValueError(
            f"Invalid ENVIRONMENT={ENVIRONMENT!r}. Expected one of: {', '.join(ENVIRONMENTS)}."
        )
    if not ENV_FILE.is_file():
        raise FileNotFoundError(f"Environment file not found: {ENV_FILE}")
    return Settings()
