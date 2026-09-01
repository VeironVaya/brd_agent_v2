"""BRD Dependency Rules Engine."""

DEPENDENCY_RULES = {
    "1.1": {
        "title": "Overview",
        "dependencies": [
        ]
    },
    "1.1.1": {
        "title": "Background",
        "specific_rules": """Must state the actual trigger (the event, problem, or decision behind it), not a restated objective.""",
        "dependencies": [
            {
                "to_id": "1.1",
                "type": "S",
                "reason": """Background elaborates the problem framed in the Overview and must stay consistent with it.""",
                "big_question": """What is the current situation that led to this initiative?""",
                "info_needed": """What exists today? What pain points or gaps triggered this? Have there been prior attempts or related projects?"""
            },
        ]
    },
    "1.1.2": {
        "title": "Business and Market Analysis",
        "specific_rules": """Must cite something concrete (a named benchmark, a competitor behavior), not a general claim of importance.""",
        "dependencies": [
            {
                "to_id": "1.1",
                "type": "W",
                "reason": """Market analysis should align with the general topic introduced in the Overview.""",
                "big_question": """How do market and industry conditions justify this initiative?""",
                "info_needed": """What are competitors doing? What customer or market trends are relevant? How does this compare to industry benchmarks?"""
            },
            {
                "to_id": "1.1.1",
                "type": "S",
                "reason": """Market analysis explains the competitive/industry context behind the background problem already described.""",
                "big_question": """How do market and industry conditions justify this initiative?""",
                "info_needed": """What are competitors doing? What customer or market trends are relevant? How does this compare to industry benchmarks?"""
            },
        ]
    },
    "1.1.3": {
        "title": "Relevant Historical Data",
        "specific_rules": """Must reference specific data, incidents, or metrics grounding the need. If none exist, say so explicitly and flag it as an assumption.""",
        "dependencies": [
            {
                "to_id": "1.1.1",
                "type": "S",
                "reason": """Historical data should quantify and support the background narrative already established.""",
                "big_question": """What historical evidence supports the need for this initiative?""",
                "info_needed": """What are the relevant past metrics, volumes, costs, or incidents? Is there trend data over time?"""
            },
        ]
    },
    "1.2": {
        "title": "Business Objective",
        "specific_rules": """The underlying business problem and why it matters now. Not a feature name — the actual goal.""",
        "dependencies": [
            {
                "to_id": "1.1",
                "type": "W",
                "reason": """Objectives should align with the overview's stated purpose.""",
                "big_question": """What does the business want to achieve with this initiative?""",
                "info_needed": """What measurable outcomes are expected? What does success look like? What's the target timeframe?"""
            },
            {
                "to_id": "1.1.1",
                "type": "S",
                "reason": """Objectives respond directly to the problem or gap described in Background.""",
                "big_question": """What does the business want to achieve with this initiative?""",
                "info_needed": """What measurable outcomes are expected? What does success look like? What's the target timeframe?"""
            },
            {
                "to_id": "1.1.2",
                "type": "S",
                "reason": """Objectives should reflect the market pressures identified in the market analysis.""",
                "big_question": """What does the business want to achieve with this initiative?""",
                "info_needed": """What measurable outcomes are expected? What does success look like? What's the target timeframe?"""
            },
            {
                "to_id": "1.1.3",
                "type": "S",
                "reason": """Objectives should be grounded in and justified by the historical trend data.""",
                "big_question": """What does the business want to achieve with this initiative?""",
                "info_needed": """What measurable outcomes are expected? What does success look like? What's the target timeframe?"""
            },
        ]
    },
    "1.3": {
        "title": "Purpose of this Business Requirement",
        "specific_rules": """What this specific document is meant to achieve or authorize.""",
        "dependencies": [
            {
                "to_id": "1.2",
                "type": "S",
                "reason": """The purpose statement should reference the business objective it supports.""",
                "big_question": """Why does this BRD exist and what decision does it support?""",
                "info_needed": """What approval or decision is this document driving? What's in scope and out of scope? Who is the audience for this BRD?"""
            },
        ]
    },
    "1.4": {
        "title": "Program Type",
        "specific_rules": """A specific category: new product/service, enhancement, regulatory compliance, migration, retirement, etc. Not "a project." """,
        "dependencies": [
            {
                "to_id": "1.1.1",
                "type": "W",
                "reason": """Classification is partly driven by the nature of the problem in Background.""",
                "big_question": """What kind of initiative is this?""",
                "info_needed": """Is this a new build, enhancement, compliance mandate, migration, or process improvement? What's driving the classification?"""
            },
            {
                "to_id": "1.2",
                "type": "S",
                "reason": """The type of program should match the nature of the stated objective.""",
                "big_question": """What kind of initiative is this?""",
                "info_needed": """Is this a new build, enhancement, compliance mandate, migration, or process improvement? What's driving the classification?"""
            },
            {
                "to_id": "1.3",
                "type": "S",
                "reason": """The program type classification should align with the stated purpose of this business requirement.""",
                "big_question": """What kind of initiative is this?""",
                "info_needed": """Is this a new build, enhancement, compliance mandate, migration, or process improvement? What's driving the classification?"""
            },
        ]
    },
    "1.5": {
        "title": "Business Risk",
        "specific_rules": """Concrete risks of doing this *and* of not doing it. Each risk names a specific cause and consequence.""",
        "dependencies": [
            {
                "to_id": "1.2",
                "type": "W",
                "reason": """Risks should be framed against what the objective is trying to achieve.""",
                "big_question": """What could go wrong and how significant is the exposure?""",
                "info_needed": """What operational, financial, compliance, technical, or reputational risks exist? What's the likelihood and impact of each?"""
            },
            {
                "to_id": "1.3",
                "type": "W",
                "reason": """Risks may relate to whether the purpose/decision this BRD supports is actually achieved.""",
                "big_question": """What could go wrong and how significant is the exposure?""",
                "info_needed": """What operational, financial, compliance, technical, or reputational risks exist? What's the likelihood and impact of each?"""
            },
            {
                "to_id": "1.4",
                "type": "S",
                "reason": """Program type strongly shapes the risk category, e.g. compliance program versus new build.""",
                "big_question": """What could go wrong and how significant is the exposure?""",
                "info_needed": """What operational, financial, compliance, technical, or reputational risks exist? What's the likelihood and impact of each?"""
            },
        ]
    },
    "2.1": {
        "title": "Summary (Benefit Analysis)",
        "specific_rules": """What improves, for whom, and by how much. A real figure is required. Never state units with no number and no explanation of why. If pending, state "pending baseline confirmation".""",
        "dependencies": [
            {
                "to_id": "1.2",
                "type": "S",
                "reason": """Benefit summary should map directly back to the stated business objective.""",
                "big_question": """What business value or benefit will this initiative deliver?""",
                "info_needed": """What are the expected financial and non-financial benefits? Over what timeframe? Who validated these estimates?"""
            },
            {
                "to_id": "1.3",
                "type": "W",
                "reason": """Should stay consistent with the stated purpose and scope of the BRD.""",
                "big_question": """What business value or benefit will this initiative deliver?""",
                "info_needed": """What are the expected financial and non-financial benefits? Over what timeframe? Who validated these estimates?"""
            },
            {
                "to_id": "1.1.3",
                "type": "S",
                "reason": """Benefit estimates need a historical baseline to compare against.""",
                "big_question": """What business value or benefit will this initiative deliver?""",
                "info_needed": """What are the expected financial and non-financial benefits? Over what timeframe? Who validated these estimates?"""
            },
        ]
    },
    "2.2": {
        "title": "Assumption and Calculation",
        "specific_rules": """The numbers and assumptions behind any benefit claim, with every assumption used in the calculation stated explicitly, not implied.""",
        "dependencies": [
            {
                "to_id": "2.1",
                "type": "S",
                "reason": """Calculations must use the assumptions and figures already declared in the Summary.""",
                "big_question": """How were the benefit figures derived?""",
                "info_needed": """What assumptions underlie the numbers, such as volumes, costs, or rates? What calculation methodology was used? What are the sensitivities?"""
            },
            {
                "to_id": "1.1.3",
                "type": "S",
                "reason": """Calculation inputs such as baseline volumes and costs come from the historical data already established.""",
                "big_question": """How were the benefit figures derived?""",
                "info_needed": """What assumptions underlie the numbers, such as volumes, costs, or rates? What calculation methodology was used? What are the sensitivities?"""
            },
        ]
    },
    "3.1": {
        "title": "General Requirement",
        "specific_rules": """A numbered list. Each item is a concrete, testable "the system shall ..." behavior.""",
        "dependencies": [
            {
                "to_id": "1.2",
                "type": "S",
                "reason": """Requirements must trace back to the business objective they are meant to satisfy.""",
                "big_question": """What must the solution do at a high level?""",
                "info_needed": """What are the must-have capabilities? What constraints exist, such as regulatory, technical, or budget? What's explicitly out of scope?"""
            },
            {
                "to_id": "1.4",
                "type": "S",
                "reason": """The nature and scope of requirements depends on what type of program this is.""",
                "big_question": """What must the solution do at a high level?""",
                "info_needed": """What are the must-have capabilities? What constraints exist, such as regulatory, technical, or budget? What's explicitly out of scope?"""
            },
            {
                "to_id": "2.1",
                "type": "W",
                "reason": """Requirements should be consistent with the benefit case that justified the investment.""",
                "big_question": """What must the solution do at a high level?""",
                "info_needed": """What are the must-have capabilities? What constraints exist, such as regulatory, technical, or budget? What's explicitly out of scope?"""
            },
        ]
    },
    "3.2": {
        "title": "Product / Service Specification",
        "specific_rules": """The actual specification of what's being built or changed, not a summary of the objective.""",
        "dependencies": [
            {
                "to_id": "3.1",
                "type": "S",
                "reason": """Specification is a direct elaboration of the general requirement.""",
                "big_question": """What exactly is being built or offered?""",
                "info_needed": """What are the detailed features or functions? What are the technical or product specifications? What variations or tiers exist?"""
            },
        ]
    },
    "3.3": {
        "title": "Business Process",
        "dependencies": [
            {
                "to_id": "3.1",
                "type": "W",
                "reason": """Process design should support the stated requirement.""",
                "big_question": """How will this operate from end to end?""",
                "info_needed": """What is the process flow from initiation to completion? Who are the actors involved at each step?"""
            },
            {
                "to_id": "3.2",
                "type": "S",
                "reason": """Process needs to reflect exactly what was specified for the product or service.""",
                "big_question": """How will this operate from end to end?""",
                "info_needed": """What is the process flow from initiation to completion? Who are the actors involved at each step?"""
            },
        ]
    },
    "3.3.1": {
        "title": "Business process impact",
        "specific_rules": """What existing processes change, and how.""",
        "dependencies": [
            {
                "to_id": "3.3",
                "type": "S",
                "reason": """Impact assessment is a direct extension of the process description.""",
                "big_question": """How does this change existing operations?""",
                "info_needed": """What processes are being replaced, modified, or newly introduced? Who is affected operationally?"""
            },
            {
                "to_id": "1.1.1",
                "type": "S",
                "reason": """Impact is measured relative to the current state already described in Background.""",
                "big_question": """How does this change existing operations?""",
                "info_needed": """What processes are being replaced, modified, or newly introduced? Who is affected operationally?"""
            },
        ]
    },
    "3.3.2": {
        "title": "Description",
        "specific_rules": """Description of the new or changed process itself.""",
        "dependencies": [
            {
                "to_id": "3.3",
                "type": "S",
                "reason": """Description elaborates the process outlined at the parent level.""",
                "big_question": """What are the step-by-step mechanics of the process?""",
                "info_needed": """What are the detailed steps, inputs, outputs, and handoffs in the process?"""
            },
            {
                "to_id": "3.2",
                "type": "S",
                "reason": """Description must stay consistent with the product/service specification.""",
                "big_question": """What are the step-by-step mechanics of the process?""",
                "info_needed": """What are the detailed steps, inputs, outputs, and handoffs in the process?"""
            },
        ]
    },
    "3.3.3": {
        "title": "Security",
        "specific_rules": """Concrete controls/requirements, not "it will be secure." """,
        "dependencies": [
            {
                "to_id": "3.3.2",
                "type": "S",
                "reason": """Security controls are defined against the process just described.""",
                "big_question": """How is the process and its data protected?""",
                "info_needed": """What data is sensitive? What access controls, authentication, or encryption are required? What compliance standards apply?"""
            },
            {
                "to_id": "3.2",
                "type": "W",
                "reason": """Security requirements may be shaped by the nature of the product or service itself.""",
                "big_question": """How is the process and its data protected?""",
                "info_needed": """What data is sensitive? What access controls, authentication, or encryption are required? What compliance standards apply?"""
            },
        ]
    },
    "3.3.4": {
        "title": "Organization and policy",
        "specific_rules": """The specific org/policy implication: who owns what, what changes.""",
        "dependencies": [
            {
                "to_id": "3.3.2",
                "type": "S",
                "reason": """Organizational and policy implications follow from the process description.""",
                "big_question": """Who owns this process and under what policies?""",
                "info_needed": """Which teams or roles are responsible? What policies or governance apply? Are new roles or approvals needed?"""
            },
            {
                "to_id": "1.4",
                "type": "W",
                "reason": """Organizational impact partly depends on the type of program, e.g. new system versus enhancement.""",
                "big_question": """Who owns this process and under what policies?""",
                "info_needed": """Which teams or roles are responsible? What policies or governance apply? Are new roles or approvals needed?"""
            },
        ]
    },
    "3.3.5": {
        "title": "Service Delivery Plan (for new application)",
        "specific_rules": """How the service is delivered operationally (Write "Not applicable" if not a new application).""",
        "dependencies": [
            {
                "to_id": "3.3.2",
                "type": "S",
                "reason": """Delivery plan operationalizes the process description.""",
                "big_question": """How will this new application or service actually be delivered and operated?""",
                "info_needed": """What is the delivery or support model? What SLAs apply? Who operates it post-launch?"""
            },
            {
                "to_id": "3.3.4",
                "type": "S",
                "reason": """Delivery plan must align with the organization and policy structure just defined.""",
                "big_question": """How will this new application or service actually be delivered and operated?""",
                "info_needed": """What is the delivery or support model? What SLAs apply? Who operates it post-launch?"""
            },
            {
                "to_id": "1.4",
                "type": "S",
                "reason": """This subsection is explicitly conditional ("for new application") on the program type.""",
                "big_question": """How will this new application or service actually be delivered and operated?""",
                "info_needed": """What is the delivery or support model? What SLAs apply? Who operates it post-launch?"""
            },
        ]
    },
    "3.4": {
        "title": "Complain Handling",
        "specific_rules": """The specific mechanism for handling related customer complaints.""",
        "dependencies": [
            {
                "to_id": "3.2",
                "type": "W",
                "reason": """Complaint handling relates to the product or service being offered.""",
                "big_question": """How will customer or user complaints be managed?""",
                "info_needed": """What channels exist for complaints? What's the escalation and resolution process? What SLAs apply to resolution?"""
            },
            {
                "to_id": "3.3.2",
                "type": "S",
                "reason": """Complaint handling procedures build on the process already described.""",
                "big_question": """How will customer or user complaints be managed?""",
                "info_needed": """What channels exist for complaints? What's the escalation and resolution process? What SLAs apply to resolution?"""
            },
        ]
    },
    "3.5": {
        "title": "Reporting",
        "specific_rules": """What gets reported, to whom, and how often. Name mechanism, audience, and frequency — all three.""",
        "dependencies": [
            {
                "to_id": "3.3.2",
                "type": "S",
                "reason": """Reporting covers the process just described.""",
                "big_question": """What will be measured and reported, and to whom?""",
                "info_needed": """What KPIs or metrics matter? Who are the report recipients? What's the reporting frequency and format?"""
            },
            {
                "to_id": "2.2",
                "type": "S",
                "reason": """Reporting metrics should tie back to the assumptions and calculations used to justify the benefit case.""",
                "big_question": """What will be measured and reported, and to whom?""",
                "info_needed": """What KPIs or metrics matter? Who are the report recipients? What's the reporting frequency and format?"""
            },
        ]
    },
    "3.6": {
        "title": "Monitoring (if required)",
        "specific_rules": """What gets monitored, how, and who is alerted (Write "Not applicable" if not required).""",
        "dependencies": [
            {
                "to_id": "3.5",
                "type": "S",
                "reason": """Monitoring builds directly on what is being reported.""",
                "big_question": """How will ongoing performance and risk be tracked?""",
                "info_needed": """What thresholds or alerts trigger action? What tools or dashboards are used? Who monitors it?"""
            },
            {
                "to_id": "1.5",
                "type": "S",
                "reason": """Monitoring should specifically track the risks already identified.""",
                "big_question": """How will ongoing performance and risk be tracked?""",
                "info_needed": """What thresholds or alerts trigger action? What tools or dashboards are used? Who monitors it?"""
            },
        ]
    },
    "3.7": {
        "title": "Settlement Plan (if applicable)",
        "specific_rules": """(Write "Not applicable" if no financial settlement is involved).""",
        "dependencies": [
            {
                "to_id": "3.2",
                "type": "W",
                "reason": """Settlement relates to the product/service specification.""",
                "big_question": """How will financial settlement or reconciliation be handled?""",
                "info_needed": """What are the settlement terms, parties involved, and timing? How are discrepancies resolved?"""
            },
            {
                "to_id": "2.2",
                "type": "S",
                "reason": """Settlement terms should be consistent with the financial assumptions and calculations already made.""",
                "big_question": """How will financial settlement or reconciliation be handled?""",
                "info_needed": """What are the settlement terms, parties involved, and timing? How are discrepancies resolved?"""
            },
        ]
    },
    "3.8": {
        "title": "Assumptions and Dependencies",
        "specific_rules": """Every value elsewhere in the document that wasn't explicitly confirmed goes here in plain language, along with other systems, teams, contracts, or approvals this relies on. Dependencies must be named specifically.""",
        "dependencies": [
            {
                "to_id": "3.3",
                "type": "S",
                "reason": """Wraps up assumptions across the service description, most directly building on the business process.""",
                "big_question": """What must be true, or what external factors, for this to succeed?""",
                "info_needed": """What are we assuming about systems, teams, timing, or budget? What external dependencies, such as vendors or other projects, exist?"""
            },
            {
                "to_id": "3.7",
                "type": "S",
                "reason": """Should incorporate any settlement-related assumptions just defined.""",
                "big_question": """What must be true, or what external factors, for this to succeed?""",
                "info_needed": """What are we assuming about systems, teams, timing, or budget? What external dependencies, such as vendors or other projects, exist?"""
            },
            {
                "to_id": "2.2",
                "type": "W",
                "reason": """Should not contradict assumptions already stated in the Benefit Analysis.""",
                "big_question": """What must be true, or what external factors, for this to succeed?""",
                "info_needed": """What are we assuming about systems, teams, timing, or budget? What external dependencies, such as vendors or other projects, exist?"""
            },
        ]
    },
    "4.1": {
        "title": "Target Ready for Service",
        "specific_rules": """A concrete date or milestone, or an explicit reason it's still pending (e.g. "pending sprint planning") — never "soon" or "TBD" with no reason.""",
        "dependencies": [
            {
                "to_id": "3.1",
                "type": "W",
                "reason": """Target readiness is scoped by the general requirement.""",
                "big_question": """When will this be ready to go live?""",
                "info_needed": """What's the target completion date? What milestones must be hit before go-live?"""
            },
            {
                "to_id": "3.3.5",
                "type": "S",
                "reason": """Readiness date should reflect the delivery plan already defined.""",
                "big_question": """When will this be ready to go live?""",
                "info_needed": """What's the target completion date? What milestones must be hit before go-live?"""
            },
            {
                "to_id": "3.8",
                "type": "S",
                "reason": """Readiness must account for the assumptions and dependencies flagged at the end of Section 3.""",
                "big_question": """When will this be ready to go live?""",
                "info_needed": """What's the target completion date? What milestones must be hit before go-live?"""
            },
        ]
    },
    "4.2": {
        "title": "Commercial Launch",
        "specific_rules": """Commercial launch plan and timing, same standard as 4.1.""",
        "dependencies": [
            {
                "to_id": "4.1",
                "type": "S",
                "reason": """Commercial launch is scheduled relative to the readiness date.""",
                "big_question": """How and when will this be launched to the market?""",
                "info_needed": """What's the launch date and go-to-market approach? What marketing or sales activities are planned?"""
            },
            {
                "to_id": "2.1",
                "type": "W",
                "reason": """Launch timing affects when benefit realization begins, so should reference the benefit summary.""",
                "big_question": """How and when will this be launched to the market?""",
                "info_needed": """What's the launch date and go-to-market approach? What marketing or sales activities are planned?"""
            },
        ]
    },
    "4.3": {
        "title": "Internal Socialization Plan (if applicable)",
        "specific_rules": """How internal teams are informed/trained ahead of launch (or "Not applicable").""",
        "dependencies": [
            {
                "to_id": "4.1",
                "type": "W",
                "reason": """Internal socialization timing follows from the readiness date.""",
                "big_question": """How will internal stakeholders be informed and prepared?""",
                "info_needed": """Who needs to be briefed internally? What training or communication is needed before launch?"""
            },
            {
                "to_id": "3.3.4",
                "type": "S",
                "reason": """Internal communication plan should address the organizational impact already described.""",
                "big_question": """How will internal stakeholders be informed and prepared?""",
                "info_needed": """Who needs to be briefed internally? What training or communication is needed before launch?"""
            },
        ]
    },
    "4.4": {
        "title": "Rollout Scenario (if any)",
        "specific_rules": """Phased, pilot, big-bang, or other rollout approach (or "Not applicable").""",
        "dependencies": [
            {
                "to_id": "4.1",
                "type": "W",
                "reason": """Rollout builds on the readiness milestone.""",
                "big_question": """How will this be rolled out — all at once or in phases?""",
                "info_needed": """Is this a pilot, phased, or big-bang rollout? What are the phase criteria and timeline?"""
            },
            {
                "to_id": "4.2",
                "type": "S",
                "reason": """Rollout scenario is a direct extension of the commercial launch plan.""",
                "big_question": """How will this be rolled out — all at once or in phases?""",
                "info_needed": """Is this a pilot, phased, or big-bang rollout? What are the phase criteria and timeline?"""
            },
            {
                "to_id": "1.4",
                "type": "S",
                "reason": """Rollout approach (pilot versus full launch) is often dictated by the program type.""",
                "big_question": """How will this be rolled out — all at once or in phases?""",
                "info_needed": """Is this a pilot, phased, or big-bang rollout? What are the phase criteria and timeline?"""
            },
        ]
    },
    "5": {
        "title": "Product/Service Retirement Plan",
        "dependencies": [
            {
                "to_id": "3.2",
                "type": "W",
                "reason": """Retirement plan concerns the same product/service that was specified.""",
                "big_question": """How and when will this eventually be retired or replaced?""",
                "info_needed": """What triggers retirement? What's the migration or decommissioning plan for existing users and data?"""
            },
            {
                "to_id": "4.4",
                "type": "S",
                "reason": """Retirement should account for how the rollout was structured, e.g. phased rollout implies phased retirement.""",
                "big_question": """How and when will this eventually be retired or replaced?""",
                "info_needed": """What triggers retirement? What's the migration or decommissioning plan for existing users and data?"""
            },
            {
                "to_id": "1.5",
                "type": "S",
                "reason": """Retirement triggers are often tied to the risks originally identified.""",
                "big_question": """How and when will this eventually be retired or replaced?""",
                "info_needed": """What triggers retirement? What's the migration or decommissioning plan for existing users and data?"""
            },
        ]
    },
}

def get_section_rules_prompt(section_id: str, context_answers: dict[str, str] = None) -> str:
    """Generates the specific prompt portion based on the rule engine for a given section."""
    if context_answers is None:
        context_answers = {}
        
    rules = DEPENDENCY_RULES.get(section_id)
    if not rules:
        return "No specific dependencies for this section."
    
    prompt = f"**{section_id} {rules['title']}**\n"
    if rules.get("specific_rules"):
        prompt += f"- **Specific Requirement for this section**: {rules['specific_rules']}\n\n"
        
    if not rules["dependencies"]:
        prompt += "- This section has no prerequisite dependencies.\n"
    else:
        prompt += "- Dependencies:\n"
        for dep in rules["dependencies"]:
            dep_title = DEPENDENCY_RULES.get(dep["to_id"], {}).get("title", "")
            req_type = "Strict Blocker (Strong)" if dep["type"] == "S" else "Non-blocking context (Weak)"
            
            prompt += f"  * Depends on {dep['to_id']} {dep_title} [{req_type}]: {dep['reason']}\n"
            prompt += f"    - Big Question to answer: {dep['big_question']}\n"
            prompt += f"    - Information needed: {dep['info_needed']}\n"
            
            ans_text = context_answers.get(dep["to_id"])
            if ans_text:
                prompt += f"    - **Current Draft of {dep['to_id']} {dep_title}**:\n"
                indented = "\n".join([f"      > {line}" for line in ans_text.split("\n")])
                prompt += f"{indented}\n"
            else:
                prompt += f"    - **Current Draft of {dep['to_id']} {dep_title}**: (Not yet drafted by user)\n"
    
    return prompt


# ===========================================================================
# AGENT 2 AUDIT & EVALUATION RUBRICS (SENIOR BA REVIEWER)
# ===========================================================================

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
    "Content provides substantive specificity that adds concrete, decision-useful information, and does not merely restate the section heading, title, or claim using synonyms, circular wording, or tautological statements",
]

GLOBAL_CONSISTENCY_CRITERIA: list[str] = [
    "The section is internally consistent with no self-contradictions",
    "The section is logically consistent with other completed BRD sections",
    "Dependencies are properly reflected and no conflict exists with prerequisite section content",
]


# ---------------------------------------------------------------------------
# Field-specific rubrics — Section-Specific Compliance (Component 3)
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

