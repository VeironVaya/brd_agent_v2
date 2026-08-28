"""Core application infrastructure: configuration, database, and exceptions."""

from app.core.config import Settings, settings
from app.core.db import Base, SessionLocal, async_sessionmaker, create_async_engine, engine, get_db
from app.core.exceptions import (
    AlreadySharedError,
    CannotShareWithSelfError,
    DomainError,
    EmailTakenError,
    ForbiddenError,
    GenerationFailedError,
    InvalidChoiceDataError,
    InvalidCredentialsError,
    InvalidRegistrationError,
    InvalidRoleError,
    NotFoundError,
    TitleRequiredError,
)

__all__ = [
    "AlreadySharedError",
    "Base",
    "CannotShareWithSelfError",
    "DomainError",
    "EmailTakenError",
    "ForbiddenError",
    "GenerationFailedError",
    "InvalidChoiceDataError",
    "InvalidCredentialsError",
    "InvalidRegistrationError",
    "InvalidRoleError",
    "NotFoundError",
    "SessionLocal",
    "Settings",
    "TitleRequiredError",
    "async_sessionmaker",
    "create_async_engine",
    "engine",
    "get_db",
    "settings",
]

