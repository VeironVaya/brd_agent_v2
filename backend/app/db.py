"""Backward-compatibility re-export for app.core.db."""

from app.core.db import (
    Base,
    SessionLocal,
    async_sessionmaker,
    create_async_engine,
    engine,
    get_db,
)

__all__ = [
    "Base",
    "SessionLocal",
    "async_sessionmaker",
    "create_async_engine",
    "engine",
    "get_db",
]
