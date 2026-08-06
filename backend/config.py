"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized settings for the Parista backend.

    Values come from environment variables (or a local ``.env`` file).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM (Google AI Studio)
    gemini_api_key: str = ""

    # Supabase (Postgres + pgvector)
    supabase_url: str = ""
    supabase_key: str = ""

    # Telegram
    telegram_bot_token: str = ""

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000


settings = Settings()