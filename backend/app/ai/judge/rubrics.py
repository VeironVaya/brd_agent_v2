"""Rubric definitions for Agent 2 (Senior BA Reviewer/Judge).

Two layers:
  GLOBAL_*_CRITERIA  — used for the 4 global components (grounding, reference
                        alignment, clarity/testability, consistency/dependency)
                        applied identically across all 26 fields.

  FIELD_SPECIFIC_RUBRICS — keyed by field_id (e.g. '1.1.1'), used ONLY for
                            Section-Specific Compliance (Component 3).
                            Must have exactly 26 entries matching
                            CANONICAL_ANSWERABLE_FIELDS.

Anti-double-counting ownership:
  Unsupported project fact          → grounding
  Misuse of reference               → reference alignment
  Wrong section / scope             → section_compliance
  Vague / non-testable              → clarity/testability
  Cross-section contradiction       → consistency/dependency
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Global rubric criteria (4 components, same for all fields)
# ---------------------------------------------------------------------------

GLOBAL_GROUNDING_CRITERIA: list[str] = [
    "Claims about facts, numbers, dates, SLA, roles, or vendors are traceable to confirmed user/project evidence",
    "No values are invented or inferred where project evidence is absent",
    "Key assertions are supported by user-stated context, not assumed from general knowledge",
]

GLOBAL_REFERENCE_CRITERIA: list[str] = [
    "The section makes business sense compared with similar projects (reference BRDs used as benchmark only)",
    "No specific number, SLA, role, rule, or vendor from a reference BRD is copied verbatim without project evidence",
    "The business approach is reasonable compared to similar enterprise or digital projects",
]

GLOBAL_CLARITY_CRITERIA: list[str] = [
    "Requirements or descriptions are clearly and unambiguously stated",
    "Content is verifiable or testable where the section type naturally warrants it (do not require numbers for sections where numbers are not natural)",
    "Requirements or statements are actionable — someone can take action based on them",
    "No unnecessary jargon or vacuous claims that add no verifiable meaning",
]

GLOBAL_CONSISTENCY_CRITERIA: list[str] = [
    "The section is internally consistent with no self-contradictions",
    "The section is logically consistent with other completed BRD sections",
    "Dependencies are properly reflected and no conflict exists with prerequisite section content",
]

# ---------------------------------------------------------------------------
# Field-specific rubrics — Section-Specific Compliance only
# ---------------------------------------------------------------------------

FIELD_SPECIFIC_RUBRICS: dict[str, list[str]] = {
    "1.1.1": [
        "The current state of the affected domain or system is described",
        "A clear problem or business opportunity is articulated",
        "The affected context (process, users, system, or market) is identified",
        "Business relevance is explained — why this matters to the organization",
        "Cause vs symptom distinction is maintained (root cause is presented, not just observable symptom)",
        "The section is solution-neutral — it does not prescribe a specific technical solution",
    ],
    "1.1.2": [
        "A clear business driver for the project is identified",
        "Market, customer, or competitive context is described where relevant",
        "Project relevance to the business driver is explained",
        "External claims (market share, competitor data, industry trends) are traced to user evidence or flagged as assumptions",
        "Business implications of the analysis are stated",
        "No fabricated market statistics or competitor facts are presented as truth",
    ],
    "1.1.3": [
        "Relevant historical data supporting the business case is referenced",
        "The meaning or significance of each metric or data point is explained",
        "A relevant timeframe or period is identified for the historical data",
        "A baseline is provided where applicable and evidence supports it",
        "No historical values are fabricated — all figures are traceable to user evidence",
        "A logical link is drawn between the historical data and the identified business need",
    ],
    "1.2": [
        "Objectives are outcome-oriented, not activity-oriented",
        "Each objective is linked to the identified problem or opportunity",
        "Business value of achieving the objective is stated or implied",
        "Objectives are measurable when evidence for measurement exists",
        "Objectives are technology-neutral",
        "Objectives are within the stated project scope",
    ],
    "1.3": [
        "The purpose of this specific BRD document is clearly stated",
        "The purpose is aligned with the business objectives from section 1.2",
        "A scope boundary is defined — what is in scope and what is out",
        "The content does not duplicate section 1.1 Background",
        "No implementation planning or solution design is included",
        "No unsupported new goals are introduced that were not established in prior sections",
    ],
    "1.4": [
        "The program type or project classification is clearly stated",
        "The classification is supported by evidence from user inputs",
        "The program type aligns with the stated purpose and scope",
        "No invented or fabricated program category is used",
        "The classification does not substitute for architecture or technical design decisions",
    ],
    "1.5": [
        "At least one risk event is described",
        "The cause or trigger of each risk is identified where known",
        "The business impact of each risk is described",
        "Proceeding vs not-proceeding risk distinction is made where relevant",
        "Severity or likelihood assessments are only included when supported by project evidence",
        "Risk is distinguished from issue — risks are potential, issues are current",
        "No invented mitigation strategies are stated as if confirmed",
    ],
    "2.1": [
        "At least one clear benefit is described",
        "The beneficiary is identified where relevant",
        "Each benefit is linked to a business objective from section 1.2",
        "Benefits are expressed as business outcomes or value, not as features",
        "Measurable benefits are provided only when project evidence supports the figures",
        "No fabricated ROI, cost savings, or revenue projections are presented as fact",
        "No overclaiming of benefit magnitude beyond what evidence supports",
    ],
    "2.2": [
        "All relevant calculation inputs are clearly identified",
        "The formula or calculation logic is explicitly stated",
        "Units of measurement are specified for all values",
        "The relevant time period for the calculation is stated",
        "Facts are distinguished from assumptions used in the calculation",
        "All inputs are traceable to project evidence or clearly flagged as assumptions",
        "The calculation is mathematically correct and internally consistent",
        "Precision is appropriate to the evidence available — no false precision",
    ],
    "3.1": [
        "A clear business capability is described",
        "The relevant actor, role, or entity is identified where applicable",
        "The requirement is within the stated project scope",
        "The requirement is stated at appropriate abstraction — not a design solution",
        "Requirements are non-redundant with other sections",
        "Only confirmed business rules are stated as requirements",
        "No vague aspirations are stated without a concrete, verifiable behavior",
    ],
    "3.2": [
        "The product or service capability is clearly described",
        "Boundaries of the product or service are defined",
        "Expected behavior, constraints, or performance characteristics are stated",
        "The specification is aligned with the general requirement in section 3.1",
        "No premature design or technology decisions are embedded",
        "No invented attributes or capabilities are presented as confirmed",
        "Expected behavior in normal and edge cases is addressed where evidence supports it",
    ],
    "3.3.1": [
        "The affected business process is identified",
        "The affected roles or organizational units are identified",
        "The nature of change to the process is described (e.g., replaced, automated, enhanced)",
        "The current-to-future state impact is described",
        "Adjacent process or downstream impacts are noted where evidence exists",
        "The impact is not merely a repetition of product features",
        "No invented organizational impact is presented without project evidence",
    ],
    "3.3.2": [
        "A clear process trigger or initiating event is described",
        "All relevant participants or roles are identified",
        "A logical sequence of process steps is described",
        "Decision points or branches are included where applicable and evidence supports them",
        "The process outcome or end state is described",
        "No invented exceptions or edge cases are stated as confirmed",
        "The process description is aligned with requirements and specification sections",
    ],
    "3.3.3": [
        "The protected concern, data type, or asset is identified",
        "Access boundaries or authorization requirements are described",
        "Required security controls are stated",
        "Security requirements are related to a confirmed business or regulatory need",
        "No invented compliance standards or regulations are cited without project evidence",
        "No specific vendor or architecture solution is prescribed",
        "Security requirements are consistent with the overall process design",
    ],
    "3.3.4": [
        "The affected organizational unit or team is identified",
        "Role or responsibility changes are described",
        "Relevant policy impacts are addressed",
        "Ownership of the change is supported by project evidence",
        "No invented roles or policies are stated as confirmed",
        "Organizational changes are aligned with the process description",
        "Governance responsibilities are identified where evidence supports them",
    ],
    "3.3.5": [
        "Relevant service delivery or readiness activities are described",
        "A logical sequence or prerequisites for delivery activities are stated",
        "Responsible parties are only named where evidence confirms ownership",
        "Operational handover or readiness criteria are addressed",
        "Timing or milestone references are only included where evidence supports them",
        "Service delivery is distinguished from commercial product launch",
    ],
    "3.4": [
        "The type or trigger of complaint being addressed is described",
        "The complaint channel is identified where evidence confirms it",
        "An owner or responsible party for complaint handling is identified where confirmed",
        "A resolution or escalation path is described",
        "SLA targets are only included where confirmed by project evidence",
        "Complaint handling is aligned with the overall service or process design",
        "No invented support workflow or ticketing tool is stated as confirmed",
    ],
    "3.5": [
        "The subject or type of report is clearly identified",
        "The content or key data elements of the report are described",
        "The recipient or consumer of the report is identified",
        "The purpose of the report is stated",
        "Frequency or timing is stated only where evidence confirms it",
        "Reporting requirements are aligned with business process needs",
        "No invented metrics or report fields are stated as confirmed",
    ],
    "3.6": [
        "The subject of monitoring is clearly identified",
        "The business purpose of monitoring is stated",
        "Indicators or metrics are identified where evidence confirms them",
        "Threshold values or alert levels are only stated where project evidence supports them",
        "The trigger action or response to a monitoring alert is described where available",
        "Monitoring is distinguished from reporting — monitoring is operational, reporting is informational",
        "Requirements remain at business level — no specific tooling is mandated without evidence",
    ],
    "3.7": [
        "The settlement scope or subject is clearly identified",
        "The relevant parties to the settlement are identified",
        "The settlement or reconciliation process is described",
        "Calculation logic is internally consistent with section 2.2 if applicable",
        "Timing or SLA for settlement is stated only where project evidence confirms it",
        "Exception or dispute handling is addressed only where relevant and evidence-based",
        "No invented financial rules or settlement obligations are stated as confirmed",
    ],
    "3.8": [
        "Assumptions are explicitly labeled as assumptions, not stated as facts",
        "Assumptions are distinguished from dependencies",
        "No assumption has been promoted to a confirmed project fact",
        "Each dependency has a clear target section, system, or decision",
        "The impact if a dependency is not met is described where available",
        "No circular dependencies are present",
        "No speculative or invented dependencies are stated as confirmed",
        "Assumption and dependency content is consistent with other completed sections",
    ],
    "4.1": [
        "A readiness target date or milestone is stated where evidence supports it",
        "Readiness criteria or definition of ready are described where confirmed",
        "Logical prerequisites for readiness are identified",
        "No invented dates or milestone targets are stated without project evidence",
        "Service delivery readiness is aligned with section 3.3.5",
        "Dependency readiness is addressed — what must be true before go-live",
        "Technical completion is distinguished from business readiness",
    ],
    "4.2": [
        "The scope of the commercial launch is described",
        "The target audience or customer segment is identified where relevant",
        "Timing is only stated where project evidence supports it",
        "Commercial launch is aligned with the Ready for Service milestone in section 4.1",
        "Commercial conditions or prerequisites are only stated where evidence confirms them",
        "Commercial launch is distinguished from operational rollout",
        "No invented go/no-go criteria are stated as confirmed",
    ],
    "4.3": [
        "The internal audience for socialization is identified",
        "Communication or training needs are described",
        "Relevant content for socialization is identified",
        "An owner for socialization activities is only named where evidence confirms it",
        "Timing is only stated where evidence supports it",
        "Socialization plan is aligned with the organizational changes in section 3.3.4",
        "No invented training obligations or mandatory programs are stated as confirmed",
    ],
    "4.4": [
        "A rollout strategy or approach is described where defined",
        "Logical phases or stages of rollout are identified where applicable",
        "Target segments, regions, or user groups are identified",
        "Timing references are only included where project evidence supports them",
        "Rollout approach is aligned with the commercial launch plan in section 4.2",
        "Entry and exit conditions for phases are only stated where evidence exists",
        "No invented pilot programs or phasing constructs are stated as confirmed",
        "Rollout risks or controls are proportionate to the evidence available",
    ],
    "5.1": [
        "A retirement trigger or event is identified where evidence supports it",
        "Affected users, services, or systems are identified",
        "Transition or migration requirements are described",
        "Data or transaction closure requirements are addressed where applicable",
        "Communication requirements are based on project evidence, not assumed",
        "No invented ownership, dates, or timelines are stated as confirmed",
        "The retirement plan is consistent with the overall product or service lifecycle",
        "No invented replacement product or successor system is stated as confirmed",
    ],
}


def get_field_rubric(field_id: str) -> list[str]:
    """Return the section-compliance rubric for a given field_id.

    Returns an empty list if the field has no specific rubric (e.g. structural
    sections like '1.1' or '3.3'), which will result in N_A judgment for
    Section-Specific Compliance.
    """
    return FIELD_SPECIFIC_RUBRICS.get(field_id, [])
