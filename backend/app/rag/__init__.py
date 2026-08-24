"""
app/rag
=======
Internal RAG & Knowledge Base Subsystem for BRD Generation & Post-Generation Validation.
"""

from .models import (
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

from .embeddings import EmbeddingGenerator

from .semantic import (
    PostgresSemanticStore,
    search_references,
)

from .confidence import (
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    assess_confidence,
    calculate_canonical_coverage,
    calculate_field_alignment,
    calculate_reference_similarity,
    determine_confidence_level,
    generate_confidence_explanation,
)


from .validator import (
    extract_numeric_tokens,
    validate_project_facts,
)

from .generator import (
    CANONICAL_ANSWERABLE_FIELDS,
    CANONICAL_FIELD_ORDER,
    CANONICAL_FIELDS_META,
    STRUCTURAL_SECTION_IDS,
    generate_final_document,
    generate_section,
)

from .llm_client import (
    FakeLLMClient,
    LLMClient,
    get_default_llm_client,
)

from .prompts import (
    build_section_generation_prompt,
    extract_canonical_gaps,
    extract_confirmed_evidence,
)

__all__ = [
    "ConfidenceAssessment",
    "ConfidenceComponents",
    "GeneratedDocument",
    "GeneratedSection",
    "LoadedBlock",
    "LoadedDocument",
    "ParsedDocument",
    "ParsedField",
    "ReferenceCitation",
    "ReferenceChunk",
    "SearchResult",
    "ValidationResult",
    "EmbeddingGenerator",
    "PostgresSemanticStore",
    "search_references",
    "assess_confidence",
    "calculate_canonical_coverage",
    "calculate_field_alignment",
    "calculate_reference_similarity",
    "determine_confidence_level",
    "generate_confidence_explanation",
    "extract_numeric_tokens",
    "validate_project_facts",
    "CANONICAL_ANSWERABLE_FIELDS",
    "CANONICAL_FIELD_ORDER",
    "CANONICAL_FIELDS_META",
    "STRUCTURAL_SECTION_IDS",
    "generate_final_document",
    "generate_section",
    "build_section_generation_prompt",
    "extract_canonical_gaps",
    "extract_confirmed_evidence",
    "LLMClient",
    "FakeLLMClient",
    "get_default_llm_client",
]
