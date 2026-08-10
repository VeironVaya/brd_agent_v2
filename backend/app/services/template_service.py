"""Static app config: the 26-leaf BRD template tree, its dependsOn graph,
and template_key values. Python port of frontend/src/utils/draftFields.js's
SECTIONS — keep the two in sync if either changes; this is the source of
truth `SectionRepository.seed_template_tree` seeds a new Conversation from.

The dependsOn graph is resolved from the real business rules in
brainstorming/brd_dependency_matrix_v1.xlsx ("Dependency Matrix" sheet),
not hand-invented — replacing what used to be a small placeholder sample.
Resolution rules (agreed 2026-08-10, see integration_1.md for the fuller
writeup):
  1. Strong (S) and Weak (W) marks are both treated as real dependencies —
     no strength distinction exists in this schema.
  2. A dependency listed on a non-leaf header row (e.g. "3.3 Business
     Process") is propagated to every leaf under that header — headers
     have no Answer/status of their own to gate on.
  3. Same propagation applied when a header is the *target* of a
     dependency, except: if the header is the dependent leaf's own
     ancestor, that edge is dropped entirely rather than expanded — it
     would otherwise turn into the leaf depending on its own later
     siblings, a forward-reference the spreadsheet's own convention
     (unused here) would flag as a conflict.
  4. The matrix's single "5" row/column (no separate "5.1" row exists)
     maps directly onto our actual leaf, 5.1.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TemplateNode:
    id: str
    title: str
    depends_on: tuple[str, ...] = ()
    children: tuple["TemplateNode", ...] = ()

    @property
    def is_leaf(self) -> bool:
        return not self.children


SECTIONS: tuple[TemplateNode, ...] = (
    TemplateNode(
        id="1",
        title="Introduction",
        children=(
            TemplateNode(
                id="1.1",
                title="Overview",
                children=(
                    TemplateNode(id="1.1.1", title="Background"),
                    TemplateNode(id="1.1.2", title="Business and Market Analysis", depends_on=("1.1.1",)),
                    TemplateNode(id="1.1.3", title="Relevant Historical Data", depends_on=("1.1.1",)),
                ),
            ),
            TemplateNode(id="1.2", title="Business Objective", depends_on=("1.1.1", "1.1.2", "1.1.3")),
            TemplateNode(id="1.3", title="Purpose of this Business Requirement", depends_on=("1.2",)),
            TemplateNode(id="1.4", title="Program Type", depends_on=("1.1.1", "1.2")),
            TemplateNode(id="1.5", title="Business Risk", depends_on=("1.2", "1.3", "1.4")),
        ),
    ),
    TemplateNode(
        id="2",
        title="Benefit Analysis",
        children=(
            TemplateNode(id="2.1", title="Summary", depends_on=("1.1.3", "1.2", "1.3")),
            TemplateNode(id="2.2", title="Assumption and Calculation", depends_on=("1.1.3", "2.1")),
        ),
    ),
    TemplateNode(
        id="3",
        title="Service Description",
        children=(
            TemplateNode(id="3.1", title="General Requirement", depends_on=("1.2", "1.4", "2.1")),
            TemplateNode(id="3.2", title="Product / Service Specification", depends_on=("3.1",)),
            TemplateNode(
                id="3.3",
                title="Business Process",
                children=(
                    TemplateNode(id="3.3.1", title="Business process impact", depends_on=("1.1.1", "3.1", "3.2")),
                    TemplateNode(id="3.3.2", title="Description", depends_on=("3.1", "3.2")),
                    TemplateNode(id="3.3.3", title="Security", depends_on=("3.1", "3.2", "3.3.2")),
                    TemplateNode(id="3.3.4", title="Organization and policy", depends_on=("1.4", "3.1", "3.2", "3.3.2")),
                    TemplateNode(
                        id="3.3.5",
                        title="Service Delivery Plan",
                        depends_on=("1.4", "3.1", "3.2", "3.3.2", "3.3.4"),
                    ),
                ),
            ),
            TemplateNode(id="3.4", title="Complain Handling", depends_on=("3.2", "3.3.2")),
            TemplateNode(id="3.5", title="Reporting", depends_on=("2.2", "3.3.2")),
            TemplateNode(id="3.6", title="Monitoring", depends_on=("1.5", "3.5")),
            TemplateNode(id="3.7", title="Settlement Plan", depends_on=("2.2", "3.2")),
            TemplateNode(
                id="3.8",
                title="Assumptions and Dependencies",
                depends_on=("2.2", "3.3.1", "3.3.2", "3.3.3", "3.3.4", "3.3.5", "3.7"),
            ),
        ),
    ),
    TemplateNode(
        id="4",
        title="Release Plan",
        children=(
            TemplateNode(id="4.1", title="Target Ready for Service", depends_on=("3.1", "3.3.5", "3.8")),
            TemplateNode(id="4.2", title="Commercial Launch", depends_on=("2.1", "4.1")),
            TemplateNode(id="4.3", title="Internal Socialization Plan", depends_on=("3.3.4", "4.1")),
            TemplateNode(id="4.4", title="Rollout Scenario", depends_on=("1.4", "4.1", "4.2")),
        ),
    ),
    TemplateNode(
        id="5",
        title="Product/Service Retirement Plan",
        children=(TemplateNode(id="5.1", title="Retirement Plan", depends_on=("1.5", "3.2", "4.4")),),
    ),
)

# Document Signoff — deliberately NOT a Section row (see erd.md's Decisions:
# static app config, identical across every conversation, no chat/answer).
# document_service.py appends this directly from here.
BOILERPLATE_SECTION = {
    "title": "Document Signoff",
    "description": "Name / Role / Date placeholders for approvers — included automatically, not gathered through chat.",
}


@dataclass(frozen=True)
class Leaf:
    id: str
    title: str
    depends_on: tuple[str, ...]
    top_section_id: str


def flatten_leaves() -> list[Leaf]:
    leaves: list[Leaf] = []

    def walk(nodes: tuple[TemplateNode, ...], top_section_id: str) -> None:
        for node in nodes:
            if node.is_leaf:
                leaves.append(Leaf(id=node.id, title=node.title, depends_on=node.depends_on, top_section_id=top_section_id))
            else:
                walk(node.children, top_section_id)

    for top in SECTIONS:
        walk(top.children, top.id)
    return leaves


FIELD_ORDER: list[str] = [leaf.id for leaf in flatten_leaves()]
FIELD_META: dict[str, Leaf] = {leaf.id: leaf for leaf in flatten_leaves()}

GENERAL_ROOM_ID = "general"
