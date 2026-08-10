"""Builds the Markdown BRD from the section tree + answers — Python port
of frontend/src/utils/documentMarkdown.js. Deterministic, no AI call
(same as the mock: this is what a real backend hands back, per
CLAUDE.md NFR-1 — the frontend converts markdown -> PDF client-side,
never talks to a model directly)."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import answer_repository, conversation_repository, section_repository
from app.services import conversation_service, section_tree_service, template_service

DOCUMENT_VERSION = "Version 1.0"


def _append_leaf(lines: list[str], template_key: str, title: str, answer_text: str | None) -> None:
    lines.append(f"**{template_key} {title}**")
    lines.append("")
    lines.append(answer_text or "_Not yet answered._")
    lines.append("")


def _append_custom_node(lines: list[str], node: dict, code: str, codes: dict[str, str], answers_by_section: dict) -> None:
    lines.append(f"**{code} {node['title']}**")
    lines.append("")
    if node["has_children"]:
        for i, child in enumerate(node["children"]):
            child_code = codes.get(child["id"], f"{code}.{i + 1}")
            _append_custom_node(lines, child, child_code, codes, answers_by_section)
    else:
        answer = answers_by_section.get(node["id"])
        lines.append((answer.answer_text if answer else None) or "_Not yet answered._")
        lines.append("")


async def build_markdown(session: AsyncSession, *, conversation_id: str, user_id: str) -> str:
    conversation, _role = await conversation_service.get_accessible(
        session, conversation_id, user_id, min_role="viewer"
    )
    sections = await section_repository.list_by_conversation(session, conversation_id)
    answers = await answer_repository.list_by_conversation(session, conversation_id)
    answers_by_section = {a.section_id: a for a in answers}

    by_template_key = {s.template_key: s for s in sections if s.template_key}
    custom_tree = section_tree_service.build_custom_tree(sections)
    codes = section_tree_service.compute_codes(sections)

    # Index custom top-level nodes by their nest_under (template_key), for
    # inline interleaving — mirrors customChildrenFor() in the frontend.
    custom_by_nest_under: dict[str | None, list[dict]] = {}
    for node in custom_tree:
        custom_by_nest_under.setdefault(node.get("nest_under"), []).append(node)

    lines: list[str] = []
    now = datetime.now(timezone.utc)
    generated_on = f"{now.strftime('%B')} {now.day}, {now.year}"  # avoids %-d, not portable to Windows strftime
    lines.append(f"# {conversation.title}")
    lines.append("")
    lines.append(f"*Business Requirement Document — {DOCUMENT_VERSION} · Generated {generated_on}*")
    lines.append("")

    for top in template_service.SECTIONS:
        lines.append(f"## {top.id}. {top.title}")
        lines.append("")
        for node in top.children:
            if node.is_leaf:
                section = by_template_key.get(node.id)
                answer = answers_by_section.get(section.section_id) if section else None
                _append_leaf(lines, node.id, node.title, answer.answer_text if answer else None)
            else:
                lines.append(f"### {node.id} {node.title}")
                lines.append("")
                for leaf in node.children:
                    section = by_template_key.get(leaf.id)
                    answer = answers_by_section.get(section.section_id) if section else None
                    _append_leaf(lines, leaf.id, leaf.title, answer.answer_text if answer else None)
                for custom_node in custom_by_nest_under.get(node.id, []):
                    _append_custom_node(lines, custom_node, codes.get(custom_node["id"], ""), codes, answers_by_section)
        for custom_node in custom_by_nest_under.get(top.id, []):
            _append_custom_node(lines, custom_node, codes.get(custom_node["id"], ""), codes, answers_by_section)

    lines.append(f"## {template_service.BOILERPLATE_SECTION['title']}")
    lines.append("")
    lines.append(template_service.BOILERPLATE_SECTION["description"])
    lines.append("")

    standalone = custom_by_nest_under.get(None, [])
    if standalone:
        lines.append("## Custom Sections")
        lines.append("")
        for custom_node in standalone:
            _append_custom_node(lines, custom_node, codes.get(custom_node["id"], ""), codes, answers_by_section)

    return "\n".join(lines)


async def generate(session: AsyncSession, *, conversation_id: str, user_id: str, format: str) -> dict:
    conversation, _role = await conversation_service.get_accessible(
        session, conversation_id, user_id, min_role="viewer"
    )
    markdown = await build_markdown(session, conversation_id=conversation_id, user_id=user_id)
    await conversation_repository.update_generation_metadata(session, conversation, DOCUMENT_VERSION)

    ext = "md" if format == "markdown" else "pdf"
    return {"filename": f"{conversation.title}.{ext}", "markdown": markdown}
