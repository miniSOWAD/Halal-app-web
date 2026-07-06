from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import models  # noqa: F401  # Register SQLAlchemy models before create_all.
from app.bootstrap import seed_database, upgrade_existing_schema
from app.config import settings
from app.database import DATABASE_URL, Base, engine
from app.routes import router


def validate_production_settings() -> None:
    if not settings.is_production:
        return
    if DATABASE_URL.startswith("sqlite"):
        raise RuntimeError(
            "Production cannot use SQLite. Add DATABASE_URL in FastAPI Cloud "
            "or connect the Neon integration, then redeploy."
        )
    if settings.jwt_secret == "development-only-change-me" or len(settings.jwt_secret) < 32:
        raise RuntimeError("Set a strong JWT_SECRET secret in FastAPI Cloud before running in production.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    validate_production_settings()

    if settings.auto_create_tables:
        async with engine.begin() as connection:
            if connection.dialect.name == "postgresql":
                # Avoid concurrent first-start schema creation across cloud instances.
                await connection.execute(
                    text("SELECT pg_advisory_xact_lock(:lock_key)"),
                    {"lock_key": 485019770},
                )
            await upgrade_existing_schema(connection)
            await connection.run_sync(Base.metadata.create_all)

    if settings.auto_seed_data:
        await seed_database()

    yield
    await engine.dispose()


app = FastAPI(
    title=f"{settings.app_name} API",
    description="Ingredient, barcode, QR, food-label, halal, and nutrition analysis API.",
    version="1.3.0",
    lifespan=lifespan,
)

if settings.cors_allow_all:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_urls,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "api": settings.api_prefix,
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/database")
async def database_health() -> dict[str, str | bool]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            dialect = connection.dialect.name
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database connection failed.") from exc
    return {
        "status": "ok",
        "database": "connected",
        "dialect": dialect,
        "persistent": dialect == "postgresql",
    }


@app.get("/health/config")
async def configuration_health() -> dict[str, str | bool]:
    # Safe diagnostics only. No credentials or secrets are returned.
    return {
        "environment": settings.app_env,
        "api_prefix": settings.api_prefix,
        "cors_allow_all": settings.cors_allow_all,
        "database_dialect": engine.dialect.name,
        "auto_create_tables": settings.auto_create_tables,
        "auto_seed_data": settings.auto_seed_data,
        "seed_demo_products": settings.seed_demo_products,
        "email_configured": bool(settings.smtp_username and settings.smtp_password),
    }
