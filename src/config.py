"""
Application configuration loaded from environment variables and .env file.

Uses pydantic-settings for type-safe config with validation and defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Zomato AI Recommendation System."""

    # --- Groq LLM ---
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.3

    # --- Recommendation tuning ---
    max_candidates: int = 20
    top_k: int = 5

    # --- Dataset ---
    dataset_cache_path: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Module-level singleton — import `settings` wherever needed.
settings = Settings()
