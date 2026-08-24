"""
app/rag/generator.py
====================
Core Orchestration and Taxonomy Schema Engine.
Loads canonical 26-field schema and validates canonical field identities.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable, Sequence

from .confidence import assess_confidence
from .embeddings import EmbeddingGenerator
from .llm_client import LLMClient
from .models import GeneratedDocument, GeneratedSection, ReferenceCitation, SearchResult
from .prompts import build_section_generation_prompt, extract_canonical_gaps, extract_confirmed_evidence
from .semantic import search_references
from .validator import extract_numeric_tokens, validate_project_facts

BRD_FIELDS_PATH = Path(__file__).resolve().parent / "config" / "brd_fields.json"


class UnsafeGenerationError(ValueError):
    """Raised when generated LLM output violates strict reference-isolation or evidence contracts."""
    pass


def _load_canonical_schema() -> tuple[dict[str, dict[str, str]], list[str], set[str]]:
    """
    Loads canonical BRD fields schema from config/brd_fields.json.
    Returns:
    - fields_meta: mapping of field_id -> {title, big_question, information_needed}
    - canonical_order: list of field_ids in exact canonical document sequence
    - structural_ids: set of non-answerable structural section IDs
    """
    if not BRD_FIELDS_PATH.exists():
        raise FileNotFoundError(f"BRD fields configuration not found at {BRD_FIELDS_PATH}")

    data = json.loads(BRD_FIELDS_PATH.read_text(encoding="utf-8"))

    structural_ids = {s["section_id"] for s in data.get("structural_sections", [])}
    fields_meta = {}
    canonical_order = []

    for f in data.get("fields", []):
        fid = f["field_id"]
        fields_meta[fid] = {
            "title": f.get("title", ""),
            "big_question": f.get("big_question", ""),
            "information_needed": f.get("information_needed", ""),
        }
        canonical_order.append(fid)

    return fields_meta, canonical_order, structural_ids


CANONICAL_FIELDS_META, CANONICAL_FIELD_ORDER, STRUCTURAL_SECTION_IDS = _load_canonical_schema()
CANONICAL_ANSWERABLE_FIELDS = set(CANONICAL_FIELDS_META.keys())


def _parse_structured_llm_json(raw_output: str) -> dict:
    text = raw_output.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UnsafeGenerationError(f"LLM output could not be parsed as valid JSON: {exc}\nRaw output: {raw_output[:200]}") from exc

    if not isinstance(data, dict):
        raise UnsafeGenerationError("LLM JSON output must be a JSON object (dict).")
    return data


def generate_section(
    field_id: str,
    confirmed_information: str,
    conversation_context: str | None = None,
    search_fn: Callable[[str, str | None, int], list[SearchResult]] | None = None,
    llm_client: LLMClient | None = None,
    top_k: int = 3,
    embedder: EmbeddingGenerator | None = None,
) -> GeneratedSection:
    """Generates content for a single canonical answerable BRD section."""
    if field_id is None:
        raise ValueError("field_id is required for section generation. field_id=None is not permitted.")

    if field_id not in CANONICAL_ANSWERABLE_FIELDS:
        if field_id in STRUCTURAL_SECTION_IDS:
            raise ValueError(
                f"Section generation rejected: field_id '{field_id}' is a structural header section, not an answerable leaf section."
            )
        raise ValueError(
            f"Invalid or non-answerable field_id: '{field_id}'. Section generation requires one of the 26 canonical answerable fields."
        )

    meta = CANONICAL_FIELDS_META[field_id]
    field_title = meta["title"]

    if not confirmed_information or not confirmed_information.strip():
        return GeneratedSection(
            field_id=field_id,
            field_title=field_title,
            content="[Content unresolved - No confirmed information provided for this section]",
            retrieved_references=(),
            cited_references=(),
            is_unresolved=True,
            confidence=None,
        )

    confirmed_evidence_map = extract_confirmed_evidence(confirmed_information)
    canonical_gaps = extract_canonical_gaps(meta["information_needed"])

    query_text = confirmed_information.strip()
    if conversation_context and conversation_context.strip():
        query_text += "\n" + conversation_context.strip()

    search_executor = search_fn or search_references
    raw_results = search_executor(query_text, field_id, top_k)

    retrieved_refs: list[ReferenceCitation] = []
    valid_citation_map: dict[str, ReferenceCitation] = {}
    for idx, res in enumerate(raw_results, start=1):
        cid = f"R{idx}"
        citation = ReferenceCitation.from_search_result(citation_id=cid, result=res)
        retrieved_refs.append(citation)
        valid_citation_map[cid] = citation

    retrieved_tuple = tuple(retrieved_refs)

    system_instruction, user_prompt = build_section_generation_prompt(
        field_id=field_id,
        field_title=field_title,
        big_question=meta["big_question"],
        information_needed=meta["information_needed"],
        confirmed_information=confirmed_evidence_map,
        conversation_context=conversation_context,
        references=retrieved_tuple,
        canonical_gaps=canonical_gaps,
    )

    if llm_client is None:
        raise ValueError("llm_client must be provided for generation")

    raw_output = llm_client.generate(prompt=user_prompt, system_instruction=system_instruction)
    data = _parse_structured_llm_json(raw_output)

    if "requirements" not in data or not isinstance(data["requirements"], list):
        raise UnsafeGenerationError("Structured JSON output must contain a 'requirements' list.")

    unresolved_gap_ids = data.get("unresolved_gap_ids", [])
    validated_gap_ids: list[str] = []
    for gid in unresolved_gap_ids:
        if gid in canonical_gaps and gid not in validated_gap_ids:
            validated_gap_ids.append(gid)

    req_list = data["requirements"]
    validated_reqs: list[dict] = []
    cited_r_ids: set[str] = set()

    for idx, req in enumerate(req_list):
        if not isinstance(req, dict):
            continue
        req_text = req.get("text", "").strip()
        if not req_text:
            continue

        evidence_ids = req.get("evidence_ids", [])
        cited_evidence_parts = [confirmed_evidence_map[eid] for eid in evidence_ids if eid in confirmed_evidence_map]
        combined_evidence_text = "\n".join(cited_evidence_parts)

        # Anti-hallucination check
        val_res = validate_project_facts(req_text, combined_evidence_text)
        if not val_res.is_safe:
            raise UnsafeGenerationError(val_res.reason)

        grounding_refs = req.get("grounding_reference_ids", [])
        for rid in grounding_refs:
            if rid in valid_citation_map:
                cited_r_ids.add(rid)

        validated_reqs.append({
            "text": req_text,
            "evidence_ids": evidence_ids,
            "grounding_reference_ids": grounding_refs,
        })

    content_lines: list[str] = []
    if validated_reqs:
        for r in validated_reqs:
            t = r["text"]
            content_lines.append(f"- {t}" if len(validated_reqs) > 1 else t)
    else:
        content_lines.append("[No confirmed requirements generated for this section]")

    final_content = "\n".join(content_lines)
    cited_refs_tuple = tuple(valid_citation_map[rid] for rid in sorted(cited_r_ids))
    unresolved_descriptions = [canonical_gaps[gid] for gid in validated_gap_ids if gid in canonical_gaps]

    confidence_assessment = assess_confidence(
        field_id=field_id,
        generated_content=final_content.strip(),
        retrieved_references=retrieved_tuple,
        total_canonical_gaps=len(canonical_gaps),
        unresolved_gap_descriptions=unresolved_descriptions,
        embedder=embedder,
        llm_client=llm_client,
    )

    return GeneratedSection(
        field_id=field_id,
        field_title=field_title,
        content=final_content.strip(),
        retrieved_references=retrieved_tuple,
        cited_references=cited_refs_tuple,
        is_unresolved=False,
        confidence=confidence_assessment,
    )


def generate_final_document(
    confirmed_sections: dict[str, str] | None = None,
    conversation_contexts: dict[str, str] | None = None,
    search_fn: Callable[[str, str | None, int], list[SearchResult]] | None = None,
    llm_client: LLMClient | None = None,
    top_k: int = 3,
    embedder: EmbeddingGenerator | None = None,
) -> GeneratedDocument:
    """Assembles a complete GeneratedDocument by generating sections in canonical BRD field order."""
    confirmed_map = confirmed_sections or {}
    contexts_map = conversation_contexts or {}

    sections: list[GeneratedSection] = []
    for fid in CANONICAL_FIELD_ORDER:
        confirmed_info = confirmed_map.get(fid, "")
        conv_context = contexts_map.get(fid, None)

        sec = generate_section(
            field_id=fid,
            confirmed_information=confirmed_info,
            conversation_context=conv_context,
            search_fn=search_fn,
            llm_client=llm_client,
            top_k=top_k,
            embedder=embedder,
        )
        sections.append(sec)

    return GeneratedDocument(sections=tuple(sections))
