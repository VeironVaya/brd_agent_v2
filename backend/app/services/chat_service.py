"""postMessage — orchestrates the conversational drafting and reviewing flow:

1. Resolves room and validates user permission.
2. AGENT 1 generates/revises BRD section draft (official SYSTEM_PROMPT).
3. Persists Agent 1 draft content and completeness.
4. For canonical leaf sections:
   - Constructs confirmed project evidence (human inputs only, no generated drafts).
   - Runs Hard Validator (anti-hallucination fact check).
   - Retrieves same-field RAG references for benchmark context.
   - AGENT 2 evaluates the section (Stage A Grader + Stage B Critic).
   - Persists Agent 2 confidence, components, reason, and breakdown as the
     SINGLE SOURCE OF TRUTH.
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.bubble import Bubble
from app.models.section import Section
from app.repositories import answer_repository, bubble_repository, conversation_repository, section_repository
from app.ai.rag import CANONICAL_ANSWERABLE_FIELDS, ReferenceCitation, search_references
from app.ai.validator import validate_project_facts
from app.services import ai_integration, conversation_service, template_service
from app.ai import judge


def _derive_status(completeness: int | None, confidence: int | None, issues_count: int, previous_status: str | None) -> str:
    """completeness, confidence, and issues -> status is a backend rule."""
    if completeness is None:
        return previous_status or "ready"
    if completeness >= 100 and (confidence is None or confidence >= 70) and issues_count == 0:
        return "done"
    return "progress"


async def _resolve_room_section(session: AsyncSession, conversation_id: str, room_id: str) -> Section:
    sections = await section_repository.list_by_conversation(session, conversation_id)
    if room_id == template_service.GENERAL_ROOM_ID:
        match = next((s for s in sections if s.is_general), None)
    else:
        match = next(
            (s for s in sections if (s.template_key == room_id) or (s.is_custom and s.section_id == room_id)),
            None,
        )
    if match is None:
        raise NotFoundError(f"Room {room_id!r} not found.")
    return match


async def post_message(
    session: AsyncSession, *, conversation_id: str, user_id: str, room_id: str, text: str
) -> list[dict]:
    conversation, _role = await conversation_service.get_accessible(
        session, conversation_id, user_id, min_role="editor"
    )
    section = await _resolve_room_section(session, conversation_id, room_id)

    # Gather prior bubbles and existing answer before this turn
    history = await bubble_repository.list_by_section(session, section.section_id)
    existing_answer = await answer_repository.find_by_section_id(session, section.section_id)
    current_answer = (
        {
            "answer_text": existing_answer.answer_text,
            "completeness": existing_answer.completeness,
            "confidence": existing_answer.confidence,
            "missing_items": existing_answer.missing_items,
        }
        if existing_answer
        else None
    )

    # Canonical field ID (e.g. "1.1.1")
    field_id = (
        section.template_key
        if (section.is_leaf and not section.is_custom and not section.is_general)
        else None
    )

    # Map completed section answers for cross-section context / consistency checking
    all_sections = await section_repository.list_by_conversation(session, conversation_id)
    all_answers = await answer_repository.list_by_conversation(session, conversation_id)
    context_answers: dict[str, str] = {}
    for ans in all_answers:
        ans_sec = next((s for s in all_sections if s.section_id == ans.section_id), None)
        if ans_sec and ans.answer_text:
            ans_room_id = ans_sec.template_key or ans_sec.section_id
            context_answers[ans_room_id] = ans.answer_text

    # Record user message
    user_bubble = Bubble(
        section_id=section.section_id,
        role="user",
        text=text,
        created_at=datetime.now(timezone.utc),
    )
    await bubble_repository.insert(session, user_bubble)

    project_evidence = judge.build_project_evidence_text(
        conversation_context=conversation.context,
        requestor_directorate=conversation.requestor_directorate,
        impacted_stakeholders=conversation.impacted_stakeholders,
        history=history,
        latest_user_message=text,
    )

    # ------------------------------------------------------------------ #
    # 1. AGENT 1: Generate or revise section draft content               #
    # ------------------------------------------------------------------ #
    reply = await ai_integration.get_reply(
        room_id=section.template_key or section.section_id,
        room_title=section.title,
        room_purpose=section.purpose,
        message_text=text,
        history=[{"role": b.role, "text": b.text} for b in history],
        current_answer=current_answer,
        field_id=field_id,
        context_answers=context_answers,
        project_evidence=project_evidence,
    )

    agent2_result = None

    # ------------------------------------------------------------------ #
    # 2. AUTONOMOUS REFLECTION LOOP (Agent 2 Judge -> Agent 1 Fix)       #
    # ------------------------------------------------------------------ #
    if section.is_leaf:
        if field_id and field_id in CANONICAL_ANSWERABLE_FIELDS and reply.answer_text:
            try:
                # 2b. Hard Validator
                val_result = validate_project_facts(reply.answer_text, project_evidence)
                if not val_result.is_safe:
                    claims_str = ", ".join(val_result.unsupported_claims)
                    validator_findings = f"FLAGGED UNSUPPORTED CLAIMS: {claims_str}. {val_result.reason}"
                else:
                    validator_findings = "PASS: No unconfirmed numeric tokens, dates, or SLAs detected."

                # 2c. RAG Reference Retrieval
                try:
                    raw_results = await asyncio.to_thread(search_references, reply.answer_text, field_id, 3)
                    retrieved_refs = [
                        ReferenceCitation.from_search_result(f"R{i}", r)
                        for i, r in enumerate(raw_results, start=1)
                    ]
                except Exception as rag_err:
                    print(f"[RAG SEARCH NOTE] {rag_err}")
                    retrieved_refs = []

                # 2d. Initial Agent 2 Evaluation
                agent2_result = await judge.evaluate_section(
                    field_id=field_id,
                    section_title=section.title,
                    generated_content=reply.answer_text,
                    project_evidence=project_evidence,
                    context_answers=context_answers,
                    missing_items=reply.missing_items or [],
                    validator_findings=validator_findings,
                    retrieved_references=retrieved_refs,
                )

                if agent2_result:
                    print(f"📊 AGENT 2 INITIAL SCORE: {agent2_result['final_confidence']}/100")
                    if agent2_result["final_confidence"] < 100:
                        print(f"❌ Reason: {agent2_result['confidence_reason']}")
                    else:
                        print(f"✅ PERFECT SCORE. No reflection needed.")

                # REFLECTION CHECK REMOVED: 
                # Agent 2's evaluation is directly passed to the frontend sidebar. 
                # Agent 1's initial draft is retained without regeneration to save inference costs.
                if agent2_result and agent2_result["final_confidence"] < 100:
                    print("\n" + "="*65)
                    print(f"🧐 AGENT 2 (Judge) evaluated the draft: {agent2_result['final_confidence']}/100.")
                    print("🚀 Forwarding initial draft and Judge evaluation to User sidebar.")
                    print("="*65 + "\n")


            except Exception as judge_exc:
                print(f"[AGENT 2 ERROR] field={field_id} section={section.section_id}: {judge_exc}")

    # ------------------------------------------------------------------ #
    # 3. Persist Final Bubble and Answer                                 #
    # ------------------------------------------------------------------ #
    agent_bubble = Bubble(
        section_id=section.section_id,
        role="agent",
        text=reply.reply_text,
        created_at=datetime.now(timezone.utc),
    )
    await bubble_repository.insert(session, agent_bubble)

    if section.is_leaf:
        confidence = agent2_result["final_confidence"] if agent2_result else (existing_answer.confidence if existing_answer else None)
        
        breakdown = agent2_result["confidence_breakdown"] if agent2_result else (existing_answer.confidence_breakdown if existing_answer else None)
        issues_count = 0
        if breakdown and isinstance(breakdown, dict) and "critique_issues" in breakdown:
            issues = breakdown.get("critique_issues", [])
            valid_issues = [i for i in issues if not any(x in i.lower() for x in ['no critical issues', 'no issues', 'no significant issues', 'none'])]
            issues_count = len(valid_issues)
            
        status = _derive_status(reply.completeness, confidence, issues_count, existing_answer.status if existing_answer else None)
        
        upsert_kwargs = {
            "status": status,
            "completeness": reply.completeness,
            "answer_text": reply.answer_text,
            "missing_items": reply.missing_items,
        }
        
        if agent2_result:
            upsert_kwargs.update({
                "confidence": agent2_result["final_confidence"],
                "confidence_reason": agent2_result["confidence_reason"],
                "confidence_components": agent2_result["component_scores"],
                "confidence_breakdown": agent2_result["confidence_breakdown"],
            })
            
        await answer_repository.upsert(session, section.section_id, **upsert_kwargs)

    if not section.is_general:
        conversation.focused_section_id = section.section_id
    await conversation_repository.touch_updated_at(session, conversation)

    return [
        {"id": user_bubble.bubble_id, "role": user_bubble.role, "text": user_bubble.text},
        {"id": agent_bubble.bubble_id, "role": agent_bubble.role, "text": agent_bubble.text},
    ]


async def init_chat_room(
    session: AsyncSession, *, conversation_id: str, user_id: str, room_id: str
) -> dict:
    conversation, _role = await conversation_service.get_accessible(
        session, conversation_id, user_id, min_role="editor"
    )
    section = await _resolve_room_section(session, conversation_id, room_id)

    # Check if history exists; if so, we shouldn't init again
    history = await bubble_repository.list_by_section(session, section.section_id)
    if history:
        return {"id": history[-1].bubble_id, "role": history[-1].role, "text": history[-1].text}

    # Build context answers mapping for true context forwarding
    all_sections = await section_repository.list_by_conversation(session, conversation_id)
    all_answers = await answer_repository.list_by_conversation(session, conversation_id)
    context_answers = {}
    for ans in all_answers:
        ans_sec = next((s for s in all_sections if s.section_id == ans.section_id), None)
        if ans_sec and ans.answer_text:
            ans_room_id = ans_sec.template_key or ans_sec.section_id
            context_answers[ans_room_id] = ans.answer_text

    reply = await ai_integration.get_greeting(
        room_id=section.template_key or section.section_id,
        room_title=section.title,
        context_answers=context_answers,
    )

    agent_bubble = Bubble(
        section_id=section.section_id,
        role="agent",
        text=reply.reply_text,
        created_at=datetime.now(timezone.utc),
    )
    await bubble_repository.insert(session, agent_bubble)
    
    if section.is_leaf:
        existing_answer = await answer_repository.find_by_section_id(session, section.section_id)
        
        breakdown = reply.confidence_breakdown or (existing_answer.confidence_breakdown if existing_answer else None)
        issues_count = 0
        if breakdown and isinstance(breakdown, dict) and "critique_issues" in breakdown:
            issues = breakdown.get("critique_issues", [])
            valid_issues = [i for i in issues if not any(x in i.lower() for x in ['no critical issues', 'no issues', 'no significant issues', 'none'])]
            issues_count = len(valid_issues)
            
        status = _derive_status(reply.completeness, reply.confidence, issues_count, existing_answer.status if existing_answer else None)
        await answer_repository.upsert(
            session,
            section.section_id,
            status=status,
            completeness=reply.completeness,
            confidence=reply.confidence,
            answer_text=reply.answer_text,
            missing_items=reply.missing_items,
            confidence_breakdown=reply.confidence_breakdown,
        )
    
    if not section.is_general:
        conversation.focused_section_id = section.section_id
    await conversation_repository.touch_updated_at(session, conversation)

    return {"id": agent_bubble.bubble_id, "role": agent_bubble.role, "text": agent_bubble.text}


