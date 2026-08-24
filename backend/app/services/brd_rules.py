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
            {
                "to_id": "1.4",
                "type": "S!",
                "reason": """A strong purpose statement typically frames itself against the program type, but Program Type is generated after Purpose in this sequence.""",
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
            if dep["type"] == "S!":
                req_type = "Forward Reference Anomaly (S!)"
            
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
