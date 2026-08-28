"""Backward-compatibility re-export for app.ai.validator."""

from app.ai.validator import (
    WORD_NUMBERS,
    ValidationResult,
    extract_numeric_tokens,
    validate_project_facts,
)

__all__ = [
    "WORD_NUMBERS",
    "ValidationResult",
    "extract_numeric_tokens",
    "validate_project_facts",
]
