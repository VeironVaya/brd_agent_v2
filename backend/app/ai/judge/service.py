"""Agent 2 — Senior Business Analyst Reviewer / Judge.

Orchestrates the two-stage evaluation of a single BRD section immediately
after Agent 1 generates or revises it.

Public API:
    await judge.evaluate_section(...) -> dict

Agent 2 is the SINGLE SOURCE OF TRUTH for:
- final_confidence (0-100)
- confidence_level ("HIGH" | "MEDIUM" | "LOW")
- confidence_reason (summary explanation)
- component_scores (5-dimension scores)
- confidence_breakdown (full breakdown payload for frontend)
"""

from __future__ import annotations

import json
import os
import asyncio
from datetime import datetime, timezone
from typing import Any, Sequence
import litellm

from app.models.bubble import Bubble

from app.ai.rag import (
    CANONICAL_ANSWERABLE_FIELDS,
    CANONICAL_FIELDS_META,
    ReferenceCitation,
    search_references,
)
from app.services.brd_rules import DEPENDENCY_RULES
from app.ai.judge.scoring import (
    calculate_component_score,
    calculate_final_confidence,
    determine_confidence_level,
    _calculate_component_scores,
)
from app.ai.judge.schema import (
    JudgmentLabel,
    JudgeStageAOutput,
    JudgeStageBOutput,
)
from app.services.brd_rules import (
    GLOBAL_CLARITY_CRITERIA,
    GLOBAL_CONSISTENCY_CRITERIA,
    GLOBAL_GROUNDING_CRITERIA,
    GLOBAL_REFERENCE_CRITERIA,
    get_field_rubric,
)
from app.ai.judge.prompt import build_stage_a_context, build_stage_b_context
from app.config import settings


# ---------------------------------------------------------------------------
# LLM model selection for Agent 2
# ---------------------------------------------------------------------------

_JUDGE_MODEL = "gemini/gemini-2.5-flash"
_JUDGE_FALLBACKS = [
    "gemini/gemini-flash-latest",
    "gemini/gemini-1.5-flash",
    "gemini/gemini-1.5-pro",
    "groq/llama-3.3-70b-versatile",
]

# Aliases for direct function calls and tests
_component_score = calculate_component_score
_calculate_final_confidence = calculate_final_confidence


# ---------------------------------------------------------------------------
# Deterministic Score Calculation
# ---------------------------------------------------------------------------

def _calculate_component_scores(stage_a: JudgeStageAOutput) -> dict[str, int | None]:
    """Map Stage A judgment lists to integer component scores (0-100 or None)."""
    return {
        "grounding": calculate_component_score(stage_a.grounding_judgments),
        "reference_context": calculate_component_score(stage_a.reference_judgments),
        "section_compliance": calculate_component_score(stage_a.section_compliance_judgments),
        "testability": calculate_component_score(stage_a.clarity_judgments),
        "consistency": calculate_component_score(stage_a.consistency_judgments),
    }


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def _classify_user_input(text: str) -> str:
    """Classifies a user message to distinguish confirmed facts/requirements from exploratory questions and hypotheses.

    Rules:
    - User questions (ending with '?' or starting with question words) are labeled UNCONFIRMED.
    - Brainstorming/hypothetical expressions ('mungkin', 'maybe', 'what if', etc.) are labeled UNCONFIRMED.
    - Definitive statements, numbers, constraints, and business rules are labeled CONFIRMED.
    """
    stripped = text.strip()
    lower = stripped.lower()

    # Question patterns
    question_starters = (
        # "apakah", "bagaimana", "kenapa", "mengapa", "bisakah", "kapan", "siapa", "dimana", "mana",
        "can we", "could we", "what if", "should we", "is it possible", "how about", "why", "when", "who", "where", "how"
    )
    if stripped.endswith("?") or any(lower.startswith(q) for q in question_starters):
        return f"[User Question / Inquiry — UNCONFIRMED]: {stripped}"

    # Brainstorming / Hypothesis patterns
    speculative_starters = (
        # "mungkin", "kayaknya", "sepertinya", "bisa jadi", "kira-kira", "usul", "ide", "bagus kalau", "gimana kalau",
        "maybe", "perhaps", "suppose", "consider", "brainstorming", "suggest", "i think", "tentative", "what about"
    )
    if any(lower.startswith(s) for s in speculative_starters):
        return f"[User Hypothesis / Brainstorming — UNCONFIRMED]: {stripped}"

    return f"[Confirmed User Requirement / Fact]: {stripped}"


def build_project_evidence_text(
    conversation_context: str | None,
    requestor_directorate: str | None,
    impacted_stakeholders: list[str] | None,
    history: Sequence[Bubble | dict[str, Any]],
    latest_user_message: str,
) -> str:
    """Build confirmed project/user evidence strictly from human/user inputs.

    CRITICAL: Generated draft answers (Agent 1 outputs) must NEVER be included here.
    Only user messages, user-provided project context, and confirmed stakeholder inputs
    are valid project evidence.
    Distinguishes confirmed facts/requirements from brainstorming and exploratory inquiries.
    """
    parts: list[str] = []
    if conversation_context and conversation_context.strip():
        parts.append(f"[Confirmed Project Context]: {conversation_context.strip()}")
    if requestor_directorate and requestor_directorate.strip():
        parts.append(f"[Confirmed Requestor Directorate]: {requestor_directorate.strip()}")
    if impacted_stakeholders:
        parts.append(f"[Confirmed Impacted Stakeholders]: {', '.join(impacted_stakeholders)}")

    for msg in history:
        # Support both Bubble objects and dicts
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else None)
        text = getattr(msg, "text", None) or (msg.get("text") if isinstance(msg, dict) else None)
        if role == "user" and text and text.strip():
            parts.append(_classify_user_input(text))

    if latest_user_message and latest_user_message.strip():
        parts.append(f"{_classify_user_input(latest_user_message)} (Current Message)")

    return "\n\n".join(parts) if parts else "(No explicit user evidence provided yet)"


def _build_context_sections_str(
    field_id: str,
    context_answers: dict[str, str],
) -> str:
    """Format completed sections (excluding the current field) for injection."""
    lines: list[str] = []
    dep_entry = DEPENDENCY_RULES.get(field_id, {})
    deps: list[dict[str, Any]] = [d for d in dep_entry.get("dependencies", []) if isinstance(d, dict)]
    dep_ids = {d.get("to_id") for d in deps}

    for fid, text in context_answers.items():
        if fid == field_id:
            continue
        marker = " [DEPENDENCY]" if fid in dep_ids else ""
        meta = CANONICAL_FIELDS_META.get(fid, {})
        title = meta.get("title", fid)
        lines.append(f"[{fid} — {title}]{marker}\n{text[:500]}{'...' if len(text) > 500 else ''}")

    return "\n\n".join(lines) if lines else ""


def _build_dependencies_str(field_id: str) -> str:
    """Describe canonical dependencies for the given field."""
    dep_entry = DEPENDENCY_RULES.get(field_id, {})
    deps_raw = dep_entry.get("dependencies", [])
    if not isinstance(deps_raw, list) or not deps_raw:
        return ""

    lines: list[str] = []
    for d in deps_raw:
        if not isinstance(d, dict):
            continue
        dep_type = d.get("type", "")
        strength = "STRONG BLOCKER" if dep_type == "S" else ("STRONG FORWARD-REF" if dep_type == "S!" else "CONTEXT")
        lines.append(
            f"- [{strength}] {field_id} depends on {d.get('to_id', '?')}: {d.get('reason', '')}"
        )
    return "\n".join(lines)


def _build_reference_excerpts_str(references: list[ReferenceCitation]) -> str:
    """Format retrieved reference BRD excerpts for Stage A context."""
    if not references:
        return ""
    lines: list[str] = []
    for r in references:
        lines.append(
            f"[Ref {r.citation_id} — {r.document_title} / {r.field_title}]\n"
            f"{r.content[:400]}{'...' if len(r.content) > 400 else ''}"
        )
    return "\n\n".join(lines)


def _build_criteria_str(criteria: list[str]) -> str:
    return "\n".join(f"- {c}" for c in criteria)


def _build_stage_a_summary(stage_a: JudgeStageAOutput) -> str:
    """Summarize Stage A judgments for Stage B prompt injection."""
    sections: list[str] = []

    def fmt(name: str, judgments: list) -> str:
        if not judgments:
            return f"{name}: (no criteria)"
        items = "\n".join(
            f"  [{j.label}] {j.criterion}: {j.rationale}"
            for j in judgments
        )
        return f"{name}:\n{items}"

    sections.append(fmt("Grounding", stage_a.grounding_judgments))
    sections.append(fmt("Reference Alignment", stage_a.reference_judgments))
    sections.append(fmt("Section Compliance", stage_a.section_compliance_judgments))
    sections.append(fmt("Clarity/Testability", stage_a.clarity_judgments))
    sections.append(fmt("Consistency/Dependency", stage_a.consistency_judgments))

    if stage_a.critical_flags:
        flags = "\n".join(
            f"  [{f.type}] {f.reason}" for f in stage_a.critical_flags
        )
        sections.append(f"Critical Flags:\n{flags}")

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# LLM call helper
# ---------------------------------------------------------------------------

async def _call_llm_json(prompt: str, temperature: float = 0.1) -> dict[str, Any]:
    """Call LiteLLM with Gemini for Agent 2 Judge and return parsed JSON dict."""
    if not settings.groq_api_key and not settings.gemini_api_key:
        raise RuntimeError("No API key configured for LiteLLM.")

    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    if settings.groq_api_key:
        os.environ["GROQ_API_KEY"] = settings.groq_api_key

    max_attempts = 4
    for attempt in range(max_attempts):
        try:
            completion: Any = await litellm.acompletion(
                model=_JUDGE_MODEL,
                fallbacks=_JUDGE_FALLBACKS,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=temperature,
            )
            print(f"[AGENT 2 JUDGE MODEL]: {getattr(completion, 'model', _JUDGE_MODEL)}")
            raw = completion.choices[0].message.content or "{}"
            return json.loads(raw)
        except Exception as exc:
            err_str = str(exc).lower()
            if ("rate" in err_str or "quota" in err_str or "429" in err_str or "exhausted" in err_str) and attempt < max_attempts - 1:
                wait_sec = 8.0 * (attempt + 1)
                print(f"[LLM RETRY] Hit rate limit, waiting {wait_sec}s before attempt {attempt+2}...")
                await asyncio.sleep(wait_sec)
                continue
            raise
    raise RuntimeError("Failed to obtain LLM response after retries.")


# ---------------------------------------------------------------------------
# Main public interface
# ---------------------------------------------------------------------------

async def evaluate_section(
    *,
    field_id: str,
    section_title: str,
    generated_content: str,
    project_evidence: str,
    context_answers: dict[str, str],
    missing_items: list[str],
    validator_findings: str | None = None,
    retrieved_references: list[ReferenceCitation] | None = None,
) -> dict[str, Any]:
    """Run Agent 2 Stage A + B and return the full evaluation result.

    Agent 2 is the single source of truth for confidence.

    Returns a dict with:
    - final_confidence: int (0-100)
    - confidence_level: str ("HIGH" | "MEDIUM" | "LOW")
    - confidence_reason: str
    - component_scores: dict
    - review_status: str ("PASS" | "REVIEW_REQUIRED")
    - dependency_status: str
    - critical_flags: list[dict]
    - confidence_breakdown: dict (payload for frontend ConfidenceBreakdown component)
    """
    if field_id not in CANONICAL_ANSWERABLE_FIELDS:
        return {}

    # Inject API keys for LiteLLM
    import os
    if settings.groq_api_key:
        os.environ["GROQ_API_KEY"] = settings.groq_api_key
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    # Retrieve same-field references if not provided (benchmark context only)
    if retrieved_references is None:
        try:
            raw_results = await asyncio.to_thread(
                search_references, generated_content, field_id, 3
            )
            retrieved_references = [
                ReferenceCitation.from_search_result(f"R{i}", r)
                for i, r in enumerate(raw_results, start=1)
            ]
        except Exception as rag_exc:
            print(f"[AGENT 2] RAG reference retrieval note: {rag_exc}")
            retrieved_references = []

    # Build criteria strings
    field_rubric = get_field_rubric(field_id)
    field_specific_criteria_str = (
        _build_criteria_str(field_rubric)
        if field_rubric
        else "(No field-specific criteria; mark section_compliance as N_A)"
    )
    context_sections_str = _build_context_sections_str(field_id, context_answers)
    dependencies_str = _build_dependencies_str(field_id)
    reference_excerpts_str = _build_reference_excerpts_str(retrieved_references)
    validator_str = validator_findings or "(No hard validator findings)"

    # Stage A: Verifier + Grader
    stage_a_prompt = build_stage_a_context(
        field_id=field_id,
        section_title=section_title,
        generated_content=generated_content,
        project_evidence=project_evidence,
        context_sections=context_sections_str,
        canonical_dependencies=dependencies_str,
        reference_excerpts=reference_excerpts_str,
        validator_findings=validator_str,
        grounding_criteria=_build_criteria_str(GLOBAL_GROUNDING_CRITERIA),
        reference_criteria=_build_criteria_str(GLOBAL_REFERENCE_CRITERIA),
        field_specific_criteria=field_specific_criteria_str,
        clarity_criteria=_build_criteria_str(GLOBAL_CLARITY_CRITERIA),
        consistency_criteria=_build_criteria_str(GLOBAL_CONSISTENCY_CRITERIA),
    )

    try:
        stage_a_raw = await _call_llm_json(stage_a_prompt, temperature=0.1)
        stage_a = JudgeStageAOutput.model_validate(stage_a_raw)
    except RuntimeError as rerr:
        if "No API key configured" in str(rerr):
            dim: dict[str, Any] = {"score": 75, "reason": "Evaluated in stub mode."}
            stub_bd: dict[str, Any] = {
                "final_confidence": 75,
                "confidence_level": "MEDIUM",
                "grounding": dim,
                "reference_context": dim,
                "section_compliance": dim,
                "testability": dim,
                "consistency": dim,
                "review_status": "PASS",
                "dependency_status": "NOT_YET_VERIFIABLE",
                "critical_flags": [],
                "critique_strengths": ["Draft recorded in stub mode."],
                "critique_issues": [],
                "critique_suggestions": ["Configure API keys in .env to enable live LLM evaluation."],
                "critique_summary": "Evaluated in stub mode.",
                "judge_model": "stub",
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
            }
            stub_res: dict[str, Any] = {
                "final_confidence": 75,
                "confidence_level": "MEDIUM",
                "confidence_reason": "Evaluated in stub mode.",
                "component_scores": {
                    "grounding": 75,
                    "reference_context": 75,
                    "section_compliance": 75,
                    "testability": 75,
                    "consistency": 75,
                },
                "review_status": "PASS",
                "dependency_status": "NOT_YET_VERIFIABLE",
                "critical_flags": [],
                "confidence_breakdown": stub_bd,
            }
            stub_res.update(stub_bd)
            return stub_res
        raise

    # Deterministic backend score calculation (pure Python, no LLM)
    component_scores = _calculate_component_scores(stage_a)
    final_confidence = calculate_final_confidence(component_scores)
    confidence_level = determine_confidence_level(final_confidence)
    review_status = "REVIEW_REQUIRED" if stage_a.critical_flags else "PASS"

    # Stage B: Critic
    stage_a_summary = _build_stage_a_summary(stage_a)
    stage_b_prompt = build_stage_b_context(
        field_id=field_id,
        section_title=section_title,
        generated_content=generated_content,
        stage_a_summary=stage_a_summary,
        grounding_score=component_scores.get("grounding"),
        reference_score=component_scores.get("reference_context"),
        compliance_score=component_scores.get("section_compliance"),
        clarity_score=component_scores.get("testability"),
        consistency_score=component_scores.get("consistency"),
        final_confidence=final_confidence,
        confidence_level=confidence_level,
        critical_flags_count=len(stage_a.critical_flags),
        review_status=review_status,
    )

    stage_b_raw = await _call_llm_json(stage_b_prompt, temperature=0.3)
    stage_b = JudgeStageBOutput.model_validate(stage_b_raw)

    summary_reason = stage_b.summary_reason.strip() if stage_b.summary_reason else ""
    if not summary_reason:
        summary_reason = f"Section evaluated with {confidence_level} confidence ({final_confidence}%)."

    # Build breakdown dictionary (persisted into JSONB and consumed by ConfidenceBreakdown.jsx)
    def _score_entry(score: int | None, judgments: list) -> dict[str, Any]:
        rationales = [
            j.rationale.strip()
            for j in judgments
            if j.label != JudgmentLabel.N_A and j.rationale and j.rationale.strip()
        ]
        if not rationales:
            return {"score": score, "reason": "No applicable criteria."}
        cleaned = []
        for r in rationales[:3]:
            r_str = r.rstrip(".; ")
            cleaned.append(f"{r_str}.")
        reason = " ".join(cleaned)
        return {"score": score, "reason": reason}

    critical_flags_list = [
        {"type": f.type, "reason": f.reason, "excerpt": f.excerpt}
        for f in stage_a.critical_flags
    ]

    breakdown: dict[str, Any] = {
        "final_confidence": final_confidence,
        "confidence_level": confidence_level,
        "grounding": _score_entry(component_scores["grounding"], stage_a.grounding_judgments),
        "reference_context": _score_entry(component_scores["reference_context"], stage_a.reference_judgments),
        "section_compliance": _score_entry(component_scores["section_compliance"], stage_a.section_compliance_judgments),
        "testability": _score_entry(component_scores["testability"], stage_a.clarity_judgments),
        "consistency": _score_entry(component_scores["consistency"], stage_a.consistency_judgments),
        "review_status": review_status,
        "dependency_status": stage_a.dependency_status,
        "critical_flags": critical_flags_list,
        "critique_strengths": stage_b.strengths,
        "critique_issues": stage_b.issues,
        "critique_suggestions": stage_b.suggestions,
        "critique_summary": summary_reason,
        "judge_model": _JUDGE_MODEL,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Return cohesive result dict with top-level attributes AND breakdown dict
    result: dict[str, Any] = {
        "final_confidence": final_confidence,
        "confidence_level": confidence_level,
        "confidence_reason": summary_reason,
        "component_scores": component_scores,
        "review_status": review_status,
        "dependency_status": stage_a.dependency_status,
        "critical_flags": critical_flags_list,
        "confidence_breakdown": breakdown,
    }
    # Also expose breakdown keys directly on result for seamless backward compatibility
    result.update(breakdown)
    return result
