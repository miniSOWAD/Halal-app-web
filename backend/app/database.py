from __future__ import annotations

from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


def sqlalchemy_database_url(raw_url: str) -> str:
    """Convert Neon/FastAPI Cloud PostgreSQL URLs to SQLAlchemy asyncpg URLs.

    Neon commonly provides a standard ``postgresql://`` URL with
    ``sslmode=require`` and ``channel_binding=require``. asyncpg expects
    ``ssl=require`` and does not accept ``channel_binding`` in the URL.
    """
    value = raw_url.strip()

    if value.startswith("sqlite+aiosqlite://"):
        return value

    if value.startswith("postgres://"):
        value = value.replace("postgres://", "postgresql://", 1)

    if value.startswith("postgresql+psycopg://"):
        value = value.replace("postgresql+psycopg://", "postgresql://", 1)
    elif value.startswith("postgresql+asyncpg://"):
        value = value.replace("postgresql+asyncpg://", "postgresql://", 1)

    if not value.startswith("postgresql://"):
        return value

    parsed = urlsplit(value)
    query_items = []
    for key, item_value in parse_qsl(parsed.query, keep_blank_values=True):
        if key == "channel_binding":
            continue
        if key == "sslmode":
            key = "ssl"
        query_items.append((key, item_value))

    normalized_query = urlencode(query_items)
    normalized = urlunsplit(
        (
            "postgresql+asyncpg",
            parsed.netloc,
            parsed.path,
            normalized_query,
            parsed.fragment,
        )
    )
    return normalized


def migration_database_url() -> str:
    raw_url = settings.migration_database_url or settings.database_url
    return sqlalchemy_database_url(raw_url)


DATABASE_URL = sqlalchemy_database_url(settings.database_url)

engine_options: dict[str, object] = {
    "echo": settings.debug,
    "pool_pre_ping": True,
}

if DATABASE_URL.startswith("postgresql+asyncpg://"):
    # Keep each cloud instance's local pool small. Neon may already provide a
    # pooled endpoint, so a large local pool is unnecessary.
    engine_options.update(
        pool_size=3,
        max_overflow=2,
        pool_recycle=300,
    )

engine = create_async_engine(DATABASE_URL, **engine_options)

SessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_database() -> AsyncGenerator[AsyncSession]:
    async with SessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
