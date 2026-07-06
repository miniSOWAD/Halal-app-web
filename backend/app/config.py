from __future__ import annotations

import json
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HalalFit Global"
    app_env: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    # FastAPI Cloud's Neon integration injects a normal postgresql:// URL.
    # app.database converts it to SQLAlchemy's asyncpg dialect automatically.
    database_url: str = "sqlite+aiosqlite:///./halalfit.db"
    migration_database_url: str | None = None

    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    frontend_urls: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "capacitor://localhost",
            "https://localhost",
        ]
    )

    open_food_facts_url: str = "https://world.openfoodfacts.org"
    open_food_facts_user_agent: str = "HalalFit/1.0 (contact@example.com)"

    max_upload_mb: int = 8
    auto_create_tables: bool = True
    auto_seed_data: bool = True
    seed_demo_products: bool = False
    seed_admin_email: str | None = None
    seed_admin_password: str | None = None

    # OCR options:
    # - ocr_space: works on FastAPI Cloud after OCR_API_KEY is configured
    # - tesseract: local/container fallback that needs the Tesseract system binary
    # - disabled: image endpoint returns a configuration message
    ocr_provider: str = "disabled"
    ocr_api_url: str = "https://api.ocr.space/parse/image"
    ocr_api_key: str | None = None
    ocr_language: str = "eng"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("frontend_urls", mode="before")
    @classmethod
    def parse_frontend_urls(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            return json.loads(stripped)
        return [item.strip() for item in stripped.split(",") if item.strip()]

    @field_validator("ocr_provider")
    @classmethod
    def validate_ocr_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"disabled", "ocr_space", "tesseract"}
        if normalized not in allowed:
            raise ValueError(f"OCR_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
