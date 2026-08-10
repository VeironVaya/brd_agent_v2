"""Recursive CustomSection tree building — Python port of
frontend/src/utils/customSectionTree.js. The wire shape stays identical
to the mock's (parent_id -> nest_under only at top level, children
recursive), so the frontend's existing client-side code-computation
logic (topLevelCode/childCode) keeps working unchanged against this
response. Codes ARE computed here too, but only for server-side needs
(document export, flagged-item labels) — never sent on the wire.
"""

from dataclasses import dataclass

from app.models.section import Section
from app.services import template_service


@dataclass
class CustomNode:
    id: str
    title: str
    purpose: str | None
    has_children: bool
    nest_under: str | None  # only set on top-level nodes
    children: list["CustomNode"]


def _by_parent(sections: list[Section]) -> dict[str | None, list[Section]]:
    groups: dict[str | None, list[Section]] = {}
    for s in sections:
        groups.setdefault(s.parent_id, []).append(s)
    for siblings in groups.values():
        siblings.sort(key=lambda s: s.sort_order)
    return groups


def build_custom_tree(sections: list[Section]) -> list[dict]:
    """Returns the recursive custom_sections wire shape — top-level
    entries get `nest_under`, nested ones don't (matches api_contract.md)."""
    by_id = {s.section_id: s for s in sections}
    by_parent = _by_parent(sections)

    def build_children(parent_id: str) -> list[dict]:
        return [
            build_node(child, top_level=False)
            for child in by_parent.get(parent_id, [])
            if child.is_custom
        ]

    def build_node(section: Section, *, top_level: bool) -> dict:
        node = {
            "id": section.section_id,
            "title": section.title,
            "purpose": section.purpose,
            "has_children": not section.is_leaf,
            "children": build_children(section.section_id),
        }
        if top_level:
            parent = by_id.get(section.parent_id) if section.parent_id else None
            node["nest_under"] = parent.template_key if parent else None
        return node

    # A custom section is top-level iff its parent is missing (standalone)
    # or its parent is NOT itself a custom section.
    top_level_custom = [
        s
        for s in sections
        if s.is_custom and (s.parent_id is None or (s.parent_id in by_id and not by_id[s.parent_id].is_custom))
    ]
    top_level_custom.sort(key=lambda s: s.sort_order)
    return [build_node(s, top_level=True) for s in top_level_custom]


def compute_codes(sections: list[Section]) -> dict[str, str]:
    """section_id -> display code, for every section (template leaves use
    their template_key as-is; custom nodes get computed dotted codes,
    continuing after the template's own top-level/sibling count — same
    algorithm as customSectionTree.js's topLevelCode/childCode). Used
    server-side only (document export, flagged-item labels)."""
    by_id = {s.section_id: s for s in sections}
    by_parent = _by_parent(sections)
    codes: dict[str, str] = {}

    for s in sections:
        if not s.is_custom and s.template_key:
            codes[s.section_id] = s.template_key

    def template_child_count(parent_template_key: str | None) -> int:
        if parent_template_key is None:
            return len(template_service.SECTIONS)
        node = _find_template_node(parent_template_key)
        return len(node.children) if node else 0

    top_level_custom = [
        s
        for s in sections
        if s.is_custom and (s.parent_id is None or (s.parent_id in by_id and not by_id[s.parent_id].is_custom))
    ]
    top_level_custom.sort(key=lambda s: s.sort_order)

    # Group by their effective nest_under (template_key of parent, or None)
    counters: dict[str | None, int] = {}
    for s in top_level_custom:
        parent = by_id.get(s.parent_id) if s.parent_id else None
        nest_under = parent.template_key if parent else None
        base = template_child_count(nest_under)
        counters[nest_under] = counters.get(nest_under, base)
        counters[nest_under] += 1
        position = counters[nest_under]
        codes[s.section_id] = f"{nest_under}.{position}" if nest_under else f"{position}"

    def walk_children(parent_id: str, parent_code: str) -> None:
        children = [c for c in by_parent.get(parent_id, []) if c.is_custom]
        for i, child in enumerate(children):
            codes[child.section_id] = f"{parent_code}.{i + 1}"
            walk_children(child.section_id, codes[child.section_id])

    for s in top_level_custom:
        walk_children(s.section_id, codes[s.section_id])

    return codes


def _find_template_node(template_key: str) -> template_service.TemplateNode | None:
    def walk(nodes: tuple[template_service.TemplateNode, ...]) -> template_service.TemplateNode | None:
        for node in nodes:
            if node.id == template_key:
                return node
            if not node.is_leaf:
                found = walk(node.children)
                if found:
                    return found
        return None

    return walk(template_service.SECTIONS)
