from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HalalFit Global"
    app_env: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    # Replace these with the pooled/direct connection strings from Neon.
    database_url: str = "sqlite+aiosqlite:///./halalfit.db"
    migration_database_url: str = "sqlite:///./halalfit.db"

    jwt_secret: str = "change-this-before-production-use-at-least-64-random-characters"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    frontend_urls: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "capacitor://localhost", "https://localhost"]
    )
    open_food_facts_url: str = "https://world.openfoodfacts.org"
    open_food_facts_user_agent: str = "HalalFit/1.0 (contact@example.com)"
    max_upload_mb: int = 8
    auto_create_tables: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
