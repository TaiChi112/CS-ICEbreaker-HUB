from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CS-Icebreaker Hub"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cs_icebreaker_hub"

    ws_ping_interval_seconds: int = 20
    ws_ping_timeout_seconds: int = 60
    max_room_players: int = 200

    llm_provider: str = "openai"
    llm_fallback_enabled: bool = True
    llm_default_batch_size: int = 8

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-latest"

    log_level: str = "INFO"
    enable_structured_logs: bool = True

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
