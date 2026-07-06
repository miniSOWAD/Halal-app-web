from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import models  # noqa: F401  # Register SQLAlchemy models before create_all.
from app.bootstrap import seed_database
from app.config import settings
from app.database import DATABASE_URL, Base, engine
from app.routes import router


def validate_production_settings() -> None:
    if not settings.is_production:
        return
    if DATABASE_URL.startswith("sqlite"):
        raise RuntimeError(
            "Production cannot use the temporary SQLite fallback. Connect Neon in FastAPI Cloud "
            "or set the DATABASE_URL secret."
        )
    if settings.jwt_secret == "development-only-change-me" or len(settings.jwt_secret) < 32:
        raise RuntimeError("Set a strong JWT_SECRET secret before running in production.")


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
            await connection.run_sync(Base.metadata.create_all)

    if settings.auto_seed_data:
        await seed_database()

    yield
    await engine.dispose()


app = FastAPI(
    title=f"{settings.app_name} API",
    description="Ingredient, barcode, QR, food-label, halal, and nutrition analysis API.",
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_urls,
    allow_credentials=True,
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
async def database_health() -> dict[str, str]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database connection failed.") from exc
    return {"status": "ok", "database": "connected"}
