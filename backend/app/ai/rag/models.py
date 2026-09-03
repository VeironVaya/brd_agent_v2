"""
app/rag/models.py
=================
Unified Data Models for BRD Reference Retrieval, Grounding & Confidence Assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


# ---------------------------------------------------------------------------
# Ingestion & Corpus Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LoadedBlock:
    kind: Literal["paragraph", "table"]
    text: str
    style: str | None = None


@dataclass(frozen=True)
class LoadedDocument:
    path: Path
    filename: str
    checksum: str
    blocks: tuple[LoadedBlock, ...]


@dataclass(frozen=True)
class ParsedField:
    field_id: str
    field_title: str
    blocks: tuple[LoadedBlock, ...]


@dataclass
class ParsedDocument:
    """Result of parse_document(). Consumed by chunker and validator."""
    fields: dict[str, ParsedField] = field(default_factory=dict)
    empty_fields: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    unknown_headings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReferenceChunk:
    document_key: str
    field_id: str
    field_title: str
    chunk_index: int
    content: str
    char_count: int


# ---------------------------------------------------------------------------
# Retrieval Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SearchResult:
    document_key: str
    document_title: str
    field_id: str
    field_title: str
    chunk_index: int
    content: str
    similarity_score: float


@dataclass(frozen=True)
class LexicalDocumentChunk:
    document_key: str
    document_title: str
    field_id: str
    field_title: str
    chunk_index: int
    content: str


# ---------------------------------------------------------------------------
# Generation & Grounding Data Models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReferenceCitation:
    """A retrieved Reference BRD chunk with provenance metadata."""
    citation_id: str  # e.g., "R1", "R2"
    document_key: str
    document_title: str
    field_id: str
    field_title: str
    chunk_index: int
    content: str
    similarity_score: float

    @classmethod
    def from_search_result(cls, citation_id: str, result: SearchResult) -> ReferenceCitation:
        return cls(
            citation_id=citation_id,
            document_key=result.document_key,
            document_title=result.document_title,
            field_id=result.field_id,
            field_title=result.field_title,
            chunk_index=result.chunk_index,
            content=result.content,
            similarity_score=result.similarity_score,
        )


@dataclass(frozen=True)
class ConfidenceComponents:
    """Detailed technical score components contributing to the confidence score."""
    reference_similarity: float
    field_alignment: float
    canonical_coverage: float

    def to_dict(self) -> dict[str, float]:
        return {
            "reference_similarity": self.reference_similarity,
            "field_alignment": self.field_alignment,
            "canonical_coverage": self.canonical_coverage,
        }


@dataclass(frozen=True)
class ConfidenceAssessment:
    """
    Confidence assessment evaluated post-generation against Reference BRD knowledge,
    canonical field purpose, and canonical gap coverage.
    """
    confidence_score: float
    confidence_percentage: int
    confidence_level: str  # "high", "medium", "low"
    components: ConfidenceComponents
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence_score": self.confidence_score,
            "confidence_percentage": self.confidence_percentage,
            "confidence_level": self.confidence_level,
            "components": self.components.to_dict(),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Result of anti-hallucination validation on generated BRD content against project evidence."""
    is_safe: bool
    unsupported_claims: tuple[str, ...] = ()
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "is_safe": self.is_safe,
            "unsupported_claims": list(self.unsupported_claims),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class GeneratedSection:
    """Generated content and reference provenance for a single canonical BRD section."""
    field_id: str
    field_title: str
    content: str
    retrieved_references: tuple[ReferenceCitation, ...] = ()
    cited_references: tuple[ReferenceCitation, ...] = ()
    is_unresolved: bool = False
    confidence: ConfidenceAssessment | None = None


@dataclass(frozen=True)
class GeneratedDocument:
    """Assembled BRD document consisting of canonical field-aligned GeneratedSections."""
    sections: tuple[GeneratedSection, ...] = ()
