"""
tests/test_ingest.py
====================
Consolidated unit and integration tests for Ingestion Submodule.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from app.ai.rag.models import LoadedBlock, LoadedDocument, ParsedDocument, ParsedField
from app.ai.rag.ingest.loader import load_document
from app.ai.rag.ingest.parser import parse_document, match_heading, FIELD_TITLE_MAP
from app.ai.rag.ingest.chunker import create_chunks
from app.ai.rag.ingest.validator import validate_ingest
from app.ai.rag.ingest.repository import ReferenceRepository
from app.ai.rag.cli import load_corpus, find_source_file


def test_canonical_field_contract_loaded():
    assert len(FIELD_TITLE_MAP) == 26
    assert "1.1.1" in FIELD_TITLE_MAP
    assert "3.2" in FIELD_TITLE_MAP
    assert "5.1" in FIELD_TITLE_MAP


def test_heading_matching():
    fid, title = match_heading("1.1.1 Background")
    assert fid == "1.1.1"
    assert title == "Background"

    fid2, title2 = match_heading("3.3.3 Security Requirements")
    assert fid2 == "3.3.3"
    assert title2 is not None
    assert "Security" in title2

    fid3, title3 = match_heading("Table of Contents")
    assert fid3 is None


def test_parser_maps_blocks_to_canonical_fields():
    doc = LoadedDocument(
        path=Path("mock.docx"),
        filename="mock.docx",
        checksum="abc123mock",
        blocks=(
            LoadedBlock(kind="paragraph", text="1.1.1 Background", style="Heading 1"),
            LoadedBlock(kind="paragraph", text="This is background context for project.", style="Normal"),
            LoadedBlock(kind="paragraph", text="1.2 Business Objective", style="Heading 1"),
            LoadedBlock(kind="paragraph", text="Goal is to scale revenue.", style="Normal"),
        )
    )

    parsed = parse_document(doc)
    assert "1.1.1" in parsed.fields
    assert "1.2" in parsed.fields
    assert len(parsed.fields["1.1.1"].blocks) == 1
    assert "background context" in parsed.fields["1.1.1"].blocks[0].text


def test_chunker_respects_single_field_boundary():
    parsed = ParsedDocument(
        fields={
            "1.1.1": ParsedField(
                field_id="1.1.1",
                field_title="Background",
                blocks=(
                    LoadedBlock(kind="paragraph", text="Short background content."),
                )
            ),
            "1.2": ParsedField(
                field_id="1.2",
                field_title="Business Objective",
                blocks=(
                    LoadedBlock(kind="paragraph", text="Short objective content."),
                )
            )
        }
    )

    chunks = create_chunks("doc_test", parsed)
    assert len(chunks) == 2
    assert chunks[0].field_id == "1.1.1"
    assert chunks[1].field_id == "1.2"


def test_validator_detects_empty_chunks():
    from app.ai.rag.models import ReferenceChunk
    parsed = ParsedDocument()
    bad_chunks = [
        ReferenceChunk(
            document_key="doc1",
            field_id="1.1.1",
            field_title="Background",
            chunk_index=0,
            content="",
            char_count=0,
        )
    ]
    report = validate_ingest({"document_key": "doc1"}, parsed, bad_chunks)
    assert not report.is_valid
    assert any("Empty chunk content" in e for e in report.errors)
