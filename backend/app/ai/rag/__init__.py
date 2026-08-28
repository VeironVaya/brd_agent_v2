"""app/ai/rag
==========
Internal RAG & Knowledge Base Subsystem for BRD Generation & Retrieval.
"""

from app.ai.rag.models import (
    ConfidenceAssessment,
    ConfidenceComponents,
    GeneratedDocument,
    GeneratedSection,
    LoadedBlock,
    LoadedDocument,
    ParsedDocument,
    ParsedField,
    ReferenceCitation,
    ReferenceChunk,
    SearchResult,
    ValidationResult,
)
from app.ai.rag.embeddings import EmbeddingGenerator
from app.ai.rag.retrieval import (
    PostgresSemanticStore,
    search_references,
)
from app.ai.rag.generator import (
    CANONICAL_ANSWERABLE_FIELDS,
    CANONICAL_FIELD_ORDER,
    CANONICAL_FIELDS_META,
    STRUCTURAL_SECTION_IDS,
    UnsafeGenerationError,
)
from app.ai.validator import (
    extract_numeric_tokens,
    validate_project_facts,
)

__all__ = [
    "CANONICAL_ANSWERABLE_FIELDS",
    "CANONICAL_FIELD_ORDER",
    "CANONICAL_FIELDS_META",
    "ConfidenceAssessment",
    "ConfidenceComponents",
    "EmbeddingGenerator",
    "GeneratedDocument",
    "GeneratedSection",
    "LoadedBlock",
    "LoadedDocument",
    "ParsedDocument",
    "ParsedField",
    "PostgresSemanticStore",
    "ReferenceCitation",
    "ReferenceChunk",
    "SearchResult",
    "STRUCTURAL_SECTION_IDS",
    "UnsafeGenerationError",
    "ValidationResult",
    "extract_numeric_tokens",
    "search_references",
    "validate_project_facts",
]

