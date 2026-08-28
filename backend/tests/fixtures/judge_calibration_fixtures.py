"""Calibration fixtures for Agent 2 (Senior BA Reviewer / Judge).

26 fields × 3 quality levels (GOOD, MEDIUM, POOR) = 78 minimum samples.

PURPOSE:
  These fixtures exist SOLELY for future calibration of Agent 2 against human
  Business Analyst judgments. They are NOT used in the Agent 2 production
  prompt and must NEVER be injected into any LLM system prompt.

FORMAT:
  Each fixture is a dict with:
    field_id:                  str — canonical field ID (e.g. "1.1.1")
    quality:                   "GOOD" | "MEDIUM" | "POOR"
    content:                   str — the BRD section text to evaluate
    expected_confidence_level: "HIGH" | "MEDIUM" | "LOW" — human annotator expectation
    notes:                     str — brief explanation of why this quality level was assigned

USAGE:
  Load CALIBRATION_FIXTURES and pass each sample to judge.evaluate_section().
  Compare Agent 2's output confidence_level to expected_confidence_level.
  Track agreement rate (target: >= 70% on first run, improve via prompt tuning).
"""

from __future__ import annotations

CALIBRATION_FIXTURES: list[dict] = [
    # -------------------------------------------------------------------------
    # 1.1.1 Background
    # -------------------------------------------------------------------------
    {
        "field_id": "1.1.1",
        "quality": "GOOD",
        "content": (
            "PT Maju Bersama currently processes customer loan applications through a paper-based "
            "workflow involving three departments: Branch Operations, Credit Analysis, and Legal Review. "
            "The average processing time is 14 working days, with 23% of applications requiring "
            "re-submission due to incomplete documentation. This results in an estimated Rp 2.1 billion "
            "in annual opportunity cost from delayed approvals. The root cause is the absence of a "
            "centralized document repository and automated validation at the point of submission."
        ),
        "expected_confidence_level": "HIGH",
        "notes": (
            "Describes current state clearly, identifies root cause vs symptom, "
            "uses user-confirmed metrics, solution-neutral."
        ),
    },
    {
        "field_id": "1.1.1",
        "quality": "MEDIUM",
        "content": (
            "The company currently faces challenges in its loan processing workflow. "
            "Many applications are delayed and customers are unhappy with the long wait times. "
            "The business needs a better system to handle these applications more efficiently."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": (
            "Identifies a problem but lacks specificity: no current state metrics, "
            "vague language ('better system', 'more efficiently'), no root cause analysis."
        ),
    },
    {
        "field_id": "1.1.1",
        "quality": "POOR",
        "content": (
            "We need to implement a modern digital transformation solution using AI and machine learning "
            "to improve our loan approval process with blockchain technology for security."
        ),
        "expected_confidence_level": "LOW",
        "notes": (
            "Prescribes technology solution (violates solution neutrality), "
            "no current state description, no problem/opportunity, invented technical direction."
        ),
    },

    # -------------------------------------------------------------------------
    # 1.1.2 Business and Market Analysis
    # -------------------------------------------------------------------------
    {
        "field_id": "1.1.2",
        "quality": "GOOD",
        "content": (
            "The Indonesian digital lending market has grown by approximately 42% year-on-year according "
            "to OJK's 2023 Fintech Report (cited by user). PT Maju Bersama holds a 3.2% market share "
            "in the SME lending segment (per internal 2023 annual report shared by user). Three major "
            "competitors—BankDigital, FinTrust, and QuickLoan—have launched fully digital application "
            "portals within the last 18 months, reducing their average approval time to under 3 days. "
            "Failure to digitize risks losing an estimated 15–20% of SME customers who have indicated "
            "preference for digital-first services in the user's 2024 customer satisfaction survey."
        ),
        "expected_confidence_level": "HIGH",
        "notes": (
            "External claims traced to user-cited sources, market context relevant, "
            "competitive context specific, business implication clear."
        ),
    },
    {
        "field_id": "1.1.2",
        "quality": "MEDIUM",
        "content": (
            "The digital banking market is growing rapidly. Many competitors have already launched "
            "digital products. The company needs to respond to remain competitive in the market."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": (
            "Market context present but vague. No specific competitor data, no market size, "
            "no business implication quantified. Directionally correct but lacks substance."
        ),
    },
    {
        "field_id": "1.1.2",
        "quality": "POOR",
        "content": (
            "The global fintech market is worth $312 billion and growing at 23.4% CAGR. "
            "Indonesia ranks 3rd in ASEAN for digital adoption. Our main competitor captured 45% market "
            "share last year. We must act immediately or lose everything."
        ),
        "expected_confidence_level": "LOW",
        "notes": (
            "Multiple unsupported numeric facts with no evidence trace, "
            "alarmist language ('lose everything'), competitor claim unsubstantiated."
        ),
    },

    # -------------------------------------------------------------------------
    # 1.1.3 Relevant Historical Data
    # -------------------------------------------------------------------------
    {
        "field_id": "1.1.3",
        "quality": "GOOD",
        "content": (
            "Based on internal operational data shared by user (FY2021–FY2023): "
            "Average monthly loan applications: 1,240 (FY2021), 1,580 (FY2022), 1,920 (FY2023). "
            "Rejection rate due to incomplete docs: 23% (stable across 3 years). "
            "Average processing time: 14 days (FY2023 baseline). "
            "These figures establish the baseline against which the new system's performance will be measured."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Evidence-traced metrics, clear timeframe, explicit baseline, direct link to business need.",
    },
    {
        "field_id": "1.1.3",
        "quality": "MEDIUM",
        "content": (
            "The company has historical data showing growth in loan applications over the past few years. "
            "Processing times have also been an issue historically. This data supports the need for improvement."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "References historical data but provides no actual numbers, timeframe, or baseline.",
    },
    {
        "field_id": "1.1.3",
        "quality": "POOR",
        "content": (
            "Industry studies show that companies that digitize loan processing see a 67% reduction in costs "
            "and 89% improvement in customer satisfaction. Our data will likely follow the same trend."
        ),
        "expected_confidence_level": "LOW",
        "notes": "No actual company historical data. Uses industry benchmarks as if they are project truth. Speculative projection.",
    },

    # -------------------------------------------------------------------------
    # 1.2 Business Objective
    # -------------------------------------------------------------------------
    {
        "field_id": "1.2",
        "quality": "GOOD",
        "content": (
            "1. Reduce the average loan application processing time from 14 working days to 5 working days "
            "within 6 months of go-live.\n"
            "2. Reduce the application re-submission rate from 23% to below 5% within the first year.\n"
            "3. Enable the branch network to process 30% more applications per month without additional headcount."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Outcome-oriented, measurable (user confirmed figures), linked to problem, technology-neutral, within scope.",
    },
    {
        "field_id": "1.2",
        "quality": "MEDIUM",
        "content": (
            "The objective is to improve the loan application process to make it faster and more efficient. "
            "We also want to improve customer experience and reduce operational costs."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Directionally correct but unmeasurable. 'Faster', 'more efficient', 'improve experience' are vague aspirations.",
    },
    {
        "field_id": "1.2",
        "quality": "POOR",
        "content": (
            "Deploy a cloud-based loan management system using REST APIs and microservices architecture "
            "with a mobile-first approach to achieve digital transformation goals."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Activity/technology-oriented, not outcome-oriented. No link to problem. Prescribes architecture.",
    },

    # -------------------------------------------------------------------------
    # 1.3 Purpose of This Business Requirement
    # -------------------------------------------------------------------------
    {
        "field_id": "1.3",
        "quality": "GOOD",
        "content": (
            "This Business Requirement Document defines the functional and non-functional requirements "
            "for the Loan Application Digitization project at PT Maju Bersama. It covers the end-to-end "
            "digital application submission, document validation, and credit scoring integration workflow. "
            "Out of scope: core banking system replacement, customer onboarding (KYC), and post-disbursement "
            "loan servicing. This document serves as the authoritative basis for solution design, "
            "vendor evaluation, and project sign-off."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Clear purpose, aligned with objectives, explicit scope boundary (in/out), no implementation detail.",
    },
    {
        "field_id": "1.3",
        "quality": "MEDIUM",
        "content": (
            "This document describes the requirements for the loan digitization project. "
            "It will be used by the development team to build the solution."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Identifies purpose but no scope boundary, no out-of-scope, audience limited to 'development team'.",
    },
    {
        "field_id": "1.3",
        "quality": "POOR",
        "content": (
            "PT Maju Bersama is a leading financial institution with 25 years of experience in the banking "
            "sector. We serve over 50,000 customers across Indonesia. This document was created by the "
            "IT department in collaboration with Operations."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Duplicates background. No purpose statement, no scope, no alignment with objectives.",
    },

    # -------------------------------------------------------------------------
    # 1.4 Program Type
    # -------------------------------------------------------------------------
    {
        "field_id": "1.4",
        "quality": "GOOD",
        "content": (
            "This initiative is classified as a Process Digitization and Automation program. "
            "It transforms an existing manual, paper-based workflow into a digital end-to-end process "
            "without replacing the core banking system or introducing a new product. This classification "
            "is consistent with the defined scope (submission, validation, credit scoring integration) "
            "and the stated business objectives of reducing processing time and re-submission rates."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Clear classification, evidence-backed, aligned with purpose and scope, no architectural substitution.",
    },
    {
        "field_id": "1.4",
        "quality": "MEDIUM",
        "content": "This is a digital transformation project aimed at improving internal processes.",
        "expected_confidence_level": "MEDIUM",
        "notes": "'Digital transformation' is vague. Partially aligned with scope but no evidence-backed classification.",
    },
    {
        "field_id": "1.4",
        "quality": "POOR",
        "content": (
            "This is a greenfield microservices platform development using cloud-native architecture "
            "on AWS with Kubernetes orchestration."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Prescribes architecture instead of classifying program type. No alignment with scope or objectives.",
    },

    # -------------------------------------------------------------------------
    # 1.5 Business Risk
    # -------------------------------------------------------------------------
    {
        "field_id": "1.5",
        "quality": "GOOD",
        "content": (
            "Risk 1 — Adoption Resistance (IF proceeding): Branch staff may resist transitioning from "
            "paper-based to digital workflows, causing adoption delays of 2–3 months post-go-live. "
            "This could prevent the processing time reduction objective from being realized in Year 1. "
            "Trigger: insufficient change management and training. Impact: HIGH.\n\n"
            "Risk 2 — Credit Scoring Integration Failure (IF proceeding): The external credit bureau API "
            "may not meet the required response SLA, causing processing bottlenecks. "
            "Trigger: vendor SLA non-compliance. Impact: MEDIUM.\n\n"
            "Risk 3 — NOT Proceeding: Continued paper-based processing risks a projected 15–20% customer "
            "attrition to digital-first competitors within 18 months (per user's customer survey data)."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Risk events described, causes/triggers identified, business impact stated, if-proceeding vs not-proceeding distinction, evidence-backed severity.",
    },
    {
        "field_id": "1.5",
        "quality": "MEDIUM",
        "content": (
            "There is a risk that the project may face delays due to technical complexity. "
            "There is also a risk that users may not adopt the new system easily. "
            "These risks should be managed carefully during implementation."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Risk events mentioned but vague. No causes, no business impact quantification, no risk vs issue distinction.",
    },
    {
        "field_id": "1.5",
        "quality": "POOR",
        "content": (
            "Risk: The project might fail.\n"
            "Mitigation: Hire more resources and use Agile methodology. "
            "Conduct daily standups and use Jira for tracking."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Non-specific risk ('might fail'). Invented mitigations as confirmed requirements. No business impact.",
    },

    # -------------------------------------------------------------------------
    # 2.1 Benefit Analysis
    # -------------------------------------------------------------------------
    {
        "field_id": "2.1",
        "quality": "GOOD",
        "content": (
            "Benefit 1 — Processing Capacity: Branch operations can handle 30% more applications per month "
            "without additional headcount, freeing staff for higher-value advisory activities. "
            "Beneficiary: Branch Operations.\n\n"
            "Benefit 2 — Customer Conversion: Reducing approval time from 14 to 5 days is expected to "
            "reduce customer dropout rate during the approval process (current dropout: 12% per user data). "
            "Beneficiary: Business Development.\n\n"
            "Benefit 3 — Compliance Readiness: Automated document validation reduces manual review errors, "
            "supporting OJK audit preparedness. Beneficiary: Compliance team."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Clear benefits, named beneficiaries, linked to objectives, outcome-oriented, no fabricated ROI.",
    },
    {
        "field_id": "2.1",
        "quality": "MEDIUM",
        "content": (
            "The project will improve efficiency and reduce costs. Customers will also benefit from "
            "faster service. The company will save money and increase revenue."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Benefits present but generic. 'Save money', 'increase revenue' without evidence. No beneficiaries.",
    },
    {
        "field_id": "2.1",
        "quality": "POOR",
        "content": (
            "Expected ROI: 340% in the first year. Cost savings: Rp 8.5 billion annually. "
            "Revenue increase: Rp 12 billion. Productivity improvement: 78%."
        ),
        "expected_confidence_level": "LOW",
        "notes": "All figures fabricated with no project evidence. No beneficiaries. Pure overclaiming.",
    },

    # -------------------------------------------------------------------------
    # 2.2 Assumption and Calculation
    # -------------------------------------------------------------------------
    {
        "field_id": "2.2",
        "quality": "GOOD",
        "content": (
            "Estimated additional loan volume enabled by capacity improvement:\n"
            "- Current monthly applications: 1,920 (FY2023, confirmed by user)\n"
            "- Target capacity increase: 30% = 576 additional applications/month\n"
            "- Assumption [A1]: Average loan size remains at Rp 250 juta (based on FY2023 average, user-confirmed)\n"
            "- Assumption [A2]: Approval rate remains at 72% (FY2023 average, user-confirmed)\n"
            "- Additional approved loans/month: 576 × 72% = 415\n"
            "- Additional portfolio value/month: 415 × Rp 250 juta = Rp 103.75 miliar\n"
            "Note: These projections assume market demand absorbs additional capacity, which is an untested assumption."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Inputs identified, formula explicit, units specified, period stated, assumptions labeled, inputs traced to evidence, math correct.",
    },
    {
        "field_id": "2.2",
        "quality": "MEDIUM",
        "content": (
            "We assume the system will handle 30% more applications. With current volumes of roughly "
            "2,000 per month and an average loan of around Rp 200-300 million, additional revenue "
            "could be significant."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Inputs present but imprecise (range not exact). No explicit formula. No assumption labeling. Vague conclusion.",
    },
    {
        "field_id": "2.2",
        "quality": "POOR",
        "content": (
            "The system will generate Rp 500 billion in additional revenue in the first year "
            "based on industry benchmarks showing 45% productivity gains for digitization projects."
        ),
        "expected_confidence_level": "LOW",
        "notes": "No project evidence. Fabricated industry benchmark. No formula, no inputs, no assumption labeling.",
    },

    # -------------------------------------------------------------------------
    # 3.1 General Requirement
    # -------------------------------------------------------------------------
    {
        "field_id": "3.1",
        "quality": "GOOD",
        "content": (
            "The system shall enable loan applicants to submit a complete loan application package "
            "digitally, including all required documents, through a self-service portal. "
            "The system shall automatically validate that all mandatory document types are present "
            "and legible before accepting the submission. "
            "Branch credit analysts shall be able to review, annotate, and escalate submitted applications "
            "within the system without requiring physical document handling. "
            "The system shall integrate with the credit bureau (BI Checking) to retrieve credit scores "
            "as part of the analysis workflow."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Business capability stated, actors identified, scope-aligned, appropriate abstraction, no design prescription.",
    },
    {
        "field_id": "3.1",
        "quality": "MEDIUM",
        "content": (
            "The system should be easy to use and allow users to submit loan applications online. "
            "It should also provide notifications and status updates."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "'Easy to use' is vague. Missing actors, boundary undefined. Requirements are present but not testable.",
    },
    {
        "field_id": "3.1",
        "quality": "POOR",
        "content": (
            "Build a React.js frontend with a Node.js backend API that connects to a PostgreSQL database "
            "to store loan applications. Use JWT for authentication and AWS S3 for document storage."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Prescribes full technology stack. No business capability stated. No actors. Design, not requirement.",
    },

    # -------------------------------------------------------------------------
    # 3.2 Product/Service Specification
    # -------------------------------------------------------------------------
    {
        "field_id": "3.2",
        "quality": "GOOD",
        "content": (
            "The digital loan application portal shall:\n"
            "- Accept applications from individual and SME applicants within the defined loan product categories\n"
            "- Support upload of the following document types: KTP, NPWP, financial statements (PDF/JPG, max 10MB each)\n"
            "- Validate document completeness against the loan type's required document checklist before submission\n"
            "- Provide real-time status visibility to applicants at each workflow stage\n"
            "- Generate a formal acknowledgment record upon successful submission\n"
            "Out of scope for this portal: loan product configuration, interest rate management, disbursement processing."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Capability described, boundary explicit, behavior/constraints stated, aligned with 3.1, no premature design.",
    },
    {
        "field_id": "3.2",
        "quality": "MEDIUM",
        "content": "The portal should allow users to upload documents and track their application status.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Correct direction but minimal. No boundary, no constraints, no specific document types, no behavior detail.",
    },
    {
        "field_id": "3.2",
        "quality": "POOR",
        "content": (
            "The system shall use OCR with 99.9% accuracy for document validation, support 100,000 "
            "concurrent users, and achieve sub-100ms response times using Redis caching."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented technical SLA without evidence. Premature design (OCR, Redis). No product capability statement.",
    },

    # -------------------------------------------------------------------------
    # 3.3.1 Business Process Impact
    # -------------------------------------------------------------------------
    {
        "field_id": "3.3.1",
        "quality": "GOOD",
        "content": (
            "Affected process: Loan Application Intake and Initial Review\n"
            "Affected roles: Branch Teller (intake), Credit Analyst (review), Branch Manager (approval threshold)\n\n"
            "Nature of change:\n"
            "- Current: Teller receives physical documents, performs manual checklist, forwards physical folder to Credit Analyst.\n"
            "- Future: Applicant self-submits digitally; system performs automated completeness check; "
            "Credit Analyst receives validated digital package in the system queue.\n\n"
            "Impact: Teller role shifts from document handling to applicant guidance. "
            "Credit Analyst productivity improves as pre-validation reduces rework. "
            "Adjacent impact: Physical document archive process will require redesign (out of scope for this BRD)."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Affected process named, roles identified, nature of change described (current vs future), adjacent impact noted.",
    },
    {
        "field_id": "3.3.1",
        "quality": "MEDIUM",
        "content": (
            "The new system will change how loan applications are processed. Staff will need to learn "
            "the new digital system. The process will be faster and more efficient."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Process impact acknowledged but vague. No specific roles, no current-to-future detail, just assertions.",
    },
    {
        "field_id": "3.3.1",
        "quality": "POOR",
        "content": (
            "We will implement BPM (Business Process Management) software to automate all banking processes "
            "across all departments. This will require restructuring the entire organization."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented scope ('all banking processes', 'entire organization'). Material scope leak. Technology prescription.",
    },

    # -------------------------------------------------------------------------
    # 3.3.2 Description
    # -------------------------------------------------------------------------
    {
        "field_id": "3.3.2",
        "quality": "GOOD",
        "content": (
            "Trigger: Applicant initiates a loan application via the digital portal.\n\n"
            "Process steps:\n"
            "1. Applicant selects loan product type and fills in the application form.\n"
            "2. Applicant uploads required documents (system validates file type and size).\n"
            "3. System performs automated completeness check against the loan-type checklist.\n"
            "   - If incomplete: system returns error list to applicant for correction.\n"
            "   - If complete: system generates submission reference number.\n"
            "4. Application enters Credit Analyst queue with validated documents and BI Checking score.\n"
            "5. Credit Analyst reviews, annotates, and either approves, declines, or escalates to Branch Manager.\n\n"
            "End state: Application has a recorded decision with audit trail."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Trigger defined, participants listed, logical steps with decision branch, end state described, consistent with 3.1 and 3.2.",
    },
    {
        "field_id": "3.3.2",
        "quality": "MEDIUM",
        "content": (
            "The applicant submits documents online. The system checks the documents and sends them to "
            "the credit team for review. The credit team will then make a decision."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Flow described but no branching logic, no trigger explicitly stated, minimal detail on steps.",
    },
    {
        "field_id": "3.3.2",
        "quality": "POOR",
        "content": "The system automates the loan process end-to-end using AI to make credit decisions automatically.",
        "expected_confidence_level": "LOW",
        "notes": "No steps, no participants, no trigger. Invents AI decision-making without evidence. Not a process description.",
    },

    # -------------------------------------------------------------------------
    # 3.3.3 Security
    # -------------------------------------------------------------------------
    {
        "field_id": "3.3.3",
        "quality": "GOOD",
        "content": (
            "Protected concern: Applicant personal data (KTP, NPWP, financial documents) and "
            "credit assessment records.\n\n"
            "Access boundary: Only authenticated branch staff assigned to an application may view "
            "its documents. Applicants may only view their own submissions. "
            "System administrators have audit-log access only, not document content access.\n\n"
            "Required controls:\n"
            "- Role-based access control (RBAC) aligned with the organizational roles defined in 3.3.4\n"
            "- All document transmissions must be encrypted in transit\n"
            "- Applicant data must be stored in compliance with OJK Regulation No. 11/2022 on data governance "
            "(cited as applicable regulation by user)\n\n"
            "No specific technology or encryption algorithm is mandated at this stage."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Protected assets identified, access boundary clear, controls stated, regulation cited with user evidence, no vendor prescription.",
    },
    {
        "field_id": "3.3.3",
        "quality": "MEDIUM",
        "content": (
            "The system must be secure. Only authorized users should access customer data. "
            "The system should comply with relevant regulations."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Security intent present but vague. No access boundary detail, no specific controls, vague regulation reference.",
    },
    {
        "field_id": "3.3.3",
        "quality": "POOR",
        "content": (
            "The system must implement AES-256 encryption, OAuth 2.0 with JWT tokens, WAF (Web Application "
            "Firewall) from Cloudflare, and achieve ISO 27001 certification within 6 months of launch."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Prescribes specific technology (Cloudflare, AES-256). ISO 27001 timeline invented. No protected asset, no access boundary.",
    },

    # -------------------------------------------------------------------------
    # 3.3.4 Organization and Policy
    # -------------------------------------------------------------------------
    {
        "field_id": "3.3.4",
        "quality": "GOOD",
        "content": (
            "Affected organization: Branch Operations, Credit Analysis, and Compliance departments.\n\n"
            "Role changes:\n"
            "- Branch Teller: Shifts from physical document handling to digital submission guidance. "
            "Job description update required.\n"
            "- Credit Analyst: Receives pre-validated digital packages instead of physical folders. "
            "Workflow SOPs to be updated.\n\n"
            "Policy impact:\n"
            "- The Loan Application Intake SOP (version 3.2, 2022) must be revised to reflect digital workflow.\n"
            "- Document retention policy must address digital document archiving per OJK Regulation "
            "No. 11/2022 (user-confirmed applicable).\n\n"
            "Governance: The Head of Credit Operations (user-confirmed owner) is responsible for SOP revision."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Org units named, role changes described, policy impact specific, evidence-backed ownership, no invented roles.",
    },
    {
        "field_id": "3.3.4",
        "quality": "MEDIUM",
        "content": (
            "The project will affect HR, IT, and Operations departments. "
            "Staff will need training. Some policies may need to be updated."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Departments mentioned but no role changes, no specific policies, no ownership, speculative.",
    },
    {
        "field_id": "3.3.4",
        "quality": "POOR",
        "content": (
            "A new Digital Transformation Office (DTO) must be established with a Chief Digital Officer. "
            "All existing departments must report to the DTO. A company-wide digital policy framework "
            "must be created within 3 months."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented organizational restructuring with no evidence. Material scope leak. Invented role (CDO, DTO).",
    },

    # -------------------------------------------------------------------------
    # 3.3.5 Service Delivery Plan
    # -------------------------------------------------------------------------
    {
        "field_id": "3.3.5",
        "quality": "GOOD",
        "content": (
            "Service delivery readiness activities required before go-live:\n"
            "1. Staff training on digital portal usage — coordinated by Branch Operations (user-confirmed owner)\n"
            "2. Integration testing with BI Checking API — IT Operations responsible\n"
            "3. User acceptance testing (UAT) with 3 pilot branches selected by Regional Director (user-confirmed)\n"
            "4. Update of Loan Application Intake SOP — Credit Operations owner (per 3.3.4)\n"
            "5. Operational handover checklist completion before cutover\n\n"
            "Prerequisites: 3.3.4 organizational policy updates must be completed before staff training. "
            "No go-live date is confirmed at this stage."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Readiness activities listed, sequence/prerequisites stated, confirmed owners only, handover criteria, delivery vs launch distinction, no invented dates.",
    },
    {
        "field_id": "3.3.5",
        "quality": "MEDIUM",
        "content": (
            "Before launch, the team will need to train staff and test the system. "
            "An IT team will handle the technical deployment."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Activities present but minimal. No sequence, no confirmed owners, no handover criteria.",
    },
    {
        "field_id": "3.3.5",
        "quality": "POOR",
        "content": (
            "The system will go live on March 1, 2025. All 50 branches will be onboarded simultaneously. "
            "Vendor ABC will provide 24/7 support. Training will take 2 days per branch."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Specific date invented. Vendor named without evidence. Simultaneous 50-branch rollout stated as plan without evidence.",
    },

    # -------------------------------------------------------------------------
    # 3.4 Complaint Handling
    # -------------------------------------------------------------------------
    {
        "field_id": "3.4",
        "quality": "GOOD",
        "content": (
            "Complaint types in scope: Application submission failures, document upload errors, "
            "and delayed status updates.\n\n"
            "Channel: Complaints may be submitted via the branch's existing complaint desk "
            "(user-confirmed primary channel) or the OJK complaint portal where applicable.\n\n"
            "Owner: Branch Operations Manager is responsible for first-line complaint resolution "
            "(user-confirmed).\n\n"
            "Escalation path: Unresolved complaints within 3 business days escalate to Regional Credit Operations. "
            "No system-specific SLA has been confirmed at this stage.\n\n"
            "Alignment: Complaint types are directly linked to the digitized submission workflow in 3.3.2."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Complaint types defined, channel confirmed by user, owner confirmed, escalation path described, SLA caveat honest, aligned with process.",
    },
    {
        "field_id": "3.4",
        "quality": "MEDIUM",
        "content": (
            "Customers can complain about the system through the customer service team. "
            "Complaints will be resolved as quickly as possible."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Complaint handling acknowledged but no types, no specific channel, no owner, no escalation, no SLA context.",
    },
    {
        "field_id": "3.4",
        "quality": "POOR",
        "content": (
            "Implement a Salesforce Service Cloud ticketing system with SLA of 2 hours for P1 complaints, "
            "4 hours for P2, and 24 hours for P3. Integrate with WhatsApp Business API for customer communication."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented vendor (Salesforce), invented SLA tiers with no evidence, invented integration. Design prescription, not business requirement.",
    },

    # -------------------------------------------------------------------------
    # 3.5 Reporting
    # -------------------------------------------------------------------------
    {
        "field_id": "3.5",
        "quality": "GOOD",
        "content": (
            "Report 1 — Application Status Dashboard\n"
            "Content: Count of applications by status (submitted, in-review, approved, declined, pending-docs)\n"
            "Recipient: Branch Manager and Regional Credit Head\n"
            "Purpose: Operational monitoring of workload and bottlenecks\n"
            "Frequency: Real-time (refreshed on demand)\n\n"
            "Report 2 — Monthly Processing Performance Report\n"
            "Content: Average processing time, re-submission rate, approval rate by loan type\n"
            "Recipient: Head of Credit Operations\n"
            "Purpose: Track progress against business objectives (1.2)\n"
            "Frequency: Monthly, by 5th working day of the following month\n\n"
            "Note: All metrics and recipients are user-confirmed."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Report subject, content, recipient, purpose, and frequency defined with evidence. Aligned with business objectives.",
    },
    {
        "field_id": "3.5",
        "quality": "MEDIUM",
        "content": (
            "The system will provide reports on application status to management. "
            "Reports will be generated regularly."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Reporting present but no report content, no specific recipients, no frequency definition, no purpose.",
    },
    {
        "field_id": "3.5",
        "quality": "POOR",
        "content": (
            "Generate 47 different reports covering all aspects of loan processing, risk management, "
            "compliance, HR performance, and financial analytics using Power BI with real-time dashboards."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Fabricated report count (47), massive scope expansion, technology prescription (Power BI), no business purpose.",
    },

    # -------------------------------------------------------------------------
    # 3.6 Monitoring
    # -------------------------------------------------------------------------
    {
        "field_id": "3.6",
        "quality": "GOOD",
        "content": (
            "Monitoring subject: Digital loan application portal availability and BI Checking API integration.\n\n"
            "Business purpose: Ensure that branch operations can continue processing applications "
            "without unplanned interruptions during business hours (08:00–17:00 WIB, Monday–Saturday).\n\n"
            "Indicators (user-confirmed):\n"
            "- Portal uptime during business hours\n"
            "- BI Checking API response success rate\n"
            "- Application queue backlog (number of applications awaiting Credit Analyst action > 24 hours)\n\n"
            "No specific uptime percentage threshold has been confirmed at this stage. "
            "Trigger/action: Operational team to be notified upon system unavailability. "
            "Alert mechanism to be defined during solution design."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Subject and purpose clear, indicators from evidence, threshold honestly deferred, monitoring vs reporting distinguished, no tool mandate.",
    },
    {
        "field_id": "3.6",
        "quality": "MEDIUM",
        "content": (
            "The system should be monitored to ensure it works properly. "
            "Any issues should be reported to IT immediately."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Monitoring intent present but no subject, no indicators, no threshold, not distinguished from reporting.",
    },
    {
        "field_id": "3.6",
        "quality": "POOR",
        "content": (
            "Implement Datadog APM with 99.99% uptime SLA, alert latency < 100ms, and automated "
            "PagerDuty escalation for P0 incidents. All microservices must have Prometheus metrics."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented SLA (99.99%), multiple vendor prescriptions (Datadog, PagerDuty, Prometheus), no business monitoring purpose.",
    },

    # -------------------------------------------------------------------------
    # 3.7 Settlement Plan
    # -------------------------------------------------------------------------
    {
        "field_id": "3.7",
        "quality": "GOOD",
        "content": (
            "Settlement scope: This project does not introduce new financial settlement obligations. "
            "The loan disbursement and repayment settlement process remains within the existing core "
            "banking system and is out of scope for this BRD.\n\n"
            "If, during solution design, it is determined that the new portal must trigger disbursement "
            "instructions, a separate settlement requirements analysis will be initiated. "
            "This determination is a dependency (see 3.8)."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Honest N/A with scope boundary. No invented settlement rules. Clear dependency flagged.",
    },
    {
        "field_id": "3.7",
        "quality": "MEDIUM",
        "content": "Settlement will be handled by the finance department according to existing procedures.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Defers settlement but no scope boundary, no dependency noted, vague reference to 'existing procedures'.",
    },
    {
        "field_id": "3.7",
        "quality": "POOR",
        "content": (
            "Settlement must occur within T+1 days. The system will automatically reconcile with SWIFT "
            "and generate ISO 20022 payment messages for all approved loans."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented T+1 settlement SLA, invented SWIFT integration, invented ISO 20022 requirement. No evidence for any of these.",
    },

    # -------------------------------------------------------------------------
    # 3.8 Assumptions and Dependencies
    # -------------------------------------------------------------------------
    {
        "field_id": "3.8",
        "quality": "GOOD",
        "content": (
            "Assumptions:\n"
            "[A1] The existing BI Checking API contract covers integration with new digital channels "
            "(not yet confirmed — requires Legal review).\n"
            "[A2] Branch staff have access to devices capable of running the web portal "
            "(based on current IT asset inventory, user-confirmed).\n\n"
            "Dependencies:\n"
            "[D1] 3.3.4 Organizational policy updates must be completed before staff training (3.3.5) begins.\n"
            "[D2] BI Checking API integration specification must be provided by IT before solution design starts.\n"
            "[D3] OJK compliance review of the data governance approach is required before go-live (4.1).\n\n"
            "Impact if D2 not met: Credit scoring integration cannot be designed, affecting 3.2 scope."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Assumptions explicitly labeled, distinguished from dependencies, no assumption promoted to fact, dependencies have targets and impact.",
    },
    {
        "field_id": "3.8",
        "quality": "MEDIUM",
        "content": (
            "We assume the project will have adequate budget and resources. "
            "The project depends on IT team availability and vendor cooperation."
        ),
        "expected_confidence_level": "MEDIUM",
        "notes": "Some assumptions/dependencies present but generic. Not labeled, no impact stated, no target specificity.",
    },
    {
        "field_id": "3.8",
        "quality": "POOR",
        "content": (
            "We assume the project will succeed. There are no significant dependencies "
            "since the project team is fully capable and experienced."
        ),
        "expected_confidence_level": "LOW",
        "notes": "No real assumptions, no real dependencies, wishful thinking statements. Useless for requirement governance.",
    },

    # -------------------------------------------------------------------------
    # 4.1 Target Ready for Service
    # -------------------------------------------------------------------------
    {
        "field_id": "4.1",
        "quality": "GOOD",
        "content": (
            "Target go-live window: Q3 2025 (July–September). No specific date confirmed. "
            "Final date to be determined after solution design completion.\n\n"
            "Business readiness criteria (user-confirmed):\n"
            "- All branch staff in pilot locations have completed portal training\n"
            "- UAT completed and signed off by Regional Director\n"
            "- Loan Application Intake SOP updated and approved\n"
            "- BI Checking API integration successfully tested\n"
            "- OJK compliance review of data handling completed\n\n"
            "Prerequisite dependency: 3.3.5 Service Delivery readiness activities must be completed. "
            "Technical completion does not constitute readiness — business sign-off is required."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Readiness target is a range (honest), criteria confirmed by user, prerequisites identified, technical vs business readiness distinguished.",
    },
    {
        "field_id": "4.1",
        "quality": "MEDIUM",
        "content": "The system should be ready by mid-next year. We need to ensure everything is tested before launch.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Target mentioned but vague. No criteria, no prerequisites, no distinction from commercial launch.",
    },
    {
        "field_id": "4.1",
        "quality": "POOR",
        "content": "Go-live date: January 15, 2025. All 50 branches operational from day one. Zero downtime deployment.",
        "expected_confidence_level": "LOW",
        "notes": "Specific date invented with no evidence. 50-branch simultaneous launch and zero downtime stated as facts without basis.",
    },

    # -------------------------------------------------------------------------
    # 4.2 Commercial Launch
    # -------------------------------------------------------------------------
    {
        "field_id": "4.2",
        "quality": "GOOD",
        "content": (
            "Commercial launch scope: The digital loan application portal will be made available to "
            "individual and SME applicants in the pilot branch network upon completion of business "
            "readiness criteria (4.1).\n\n"
            "Target audience: Existing and new PT Maju Bersama loan applicants in pilot branch catchment areas.\n\n"
            "Timing: Commercial launch is expected in Q3 2025, contingent on Ready for Service sign-off. "
            "No separate marketing campaign date has been confirmed.\n\n"
            "Commercial launch is distinct from full branch network rollout, which is addressed in 4.4."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Scope defined, audience identified, timing evidence-based, aligned with 4.1, distinct from rollout, no invented go/no-go criteria.",
    },
    {
        "field_id": "4.2",
        "quality": "MEDIUM",
        "content": "The product will be launched to customers after testing is completed. A marketing campaign will support the launch.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Launch intent present but no scope, no audience specificity, no timing, marketing mentioned without evidence.",
    },
    {
        "field_id": "4.2",
        "quality": "POOR",
        "content": (
            "We will launch on App Store and Google Play on February 14, 2025 (Valentine's Day) "
            "as a marketing strategy. We expect 100,000 downloads in the first month."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented channels (App Store), invented date with marketing rationale, fabricated download target.",
    },

    # -------------------------------------------------------------------------
    # 4.3 Internal Socialization Plan
    # -------------------------------------------------------------------------
    {
        "field_id": "4.3",
        "quality": "GOOD",
        "content": (
            "Internal audience: Branch Tellers, Credit Analysts, Branch Managers, and Compliance officers "
            "at pilot branches.\n\n"
            "Communication needs:\n"
            "- Briefing on process changes and role impacts (per 3.3.4)\n"
            "- Portal demonstration and hands-on training\n"
            "- Updated SOP distribution\n\n"
            "Owner: Branch Operations (user-confirmed responsible for internal socialization).\n\n"
            "Timing: Socialization to occur during the service delivery readiness period (3.3.5), "
            "before go-live. No specific dates confirmed.\n\n"
            "No mandatory external certification or training program has been confirmed."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Internal audience named, communication needs specific, owner confirmed by user, timing tied to 3.3.5, no invented obligations.",
    },
    {
        "field_id": "4.3",
        "quality": "MEDIUM",
        "content": "All staff will be informed about the new system. Training will be provided before launch.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Socialization intent present but no audience specificity, no content detail, no owner.",
    },
    {
        "field_id": "4.3",
        "quality": "POOR",
        "content": (
            "A mandatory 40-hour e-learning certification program must be completed by all 2,000 employees "
            "company-wide within 30 days of launch, delivered through Cornerstone OnDemand LMS."
        ),
        "expected_confidence_level": "LOW",
        "notes": "40-hour requirement invented, 2000-employee scope invented, 30-day timeline invented, vendor (Cornerstone) invented.",
    },

    # -------------------------------------------------------------------------
    # 4.4 Rollout Scenario
    # -------------------------------------------------------------------------
    {
        "field_id": "4.4",
        "quality": "GOOD",
        "content": (
            "Rollout strategy: Phased geographic rollout following commercial launch (4.2).\n\n"
            "Phase 1 — Pilot (3 branches, user-confirmed selection): Upon Ready for Service sign-off.\n"
            "Phase 2 — Regional expansion: Remaining branches in the pilot region, subject to Phase 1 "
            "operational review. No timeline confirmed.\n"
            "Phase 3 — National rollout: All remaining branches, subject to Phase 2 review. "
            "No timeline confirmed.\n\n"
            "Entry condition for each phase: Operational performance review by Head of Credit Operations.\n"
            "No invented go/no-go threshold has been specified."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Phased strategy described, segments identified, entry conditions stated, timing honest (not invented), aligned with 4.2.",
    },
    {
        "field_id": "4.4",
        "quality": "MEDIUM",
        "content": "The system will be rolled out in phases, starting with a pilot and then expanding to all branches.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Phased approach mentioned but no segments, no entry conditions, no timing context.",
    },
    {
        "field_id": "4.4",
        "quality": "POOR",
        "content": (
            "Big bang rollout to all 50 branches on Day 1. Week 1: Jakarta. Week 2: Surabaya. "
            "Week 3: all other cities. Rollout team of 20 from HQ will travel to each location."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Contradicts phased approach implied by 4.1. Invented timelines, invented team structure. No entry/exit conditions.",
    },

    # -------------------------------------------------------------------------
    # 5.1 Product/Service Retirement Plan
    # -------------------------------------------------------------------------
    {
        "field_id": "5.1",
        "quality": "GOOD",
        "content": (
            "Retirement scope: The legacy paper-based loan application intake process.\n\n"
            "Retirement trigger: Completion of Phase 2 rollout (4.4) and confirmation that digital "
            "portal handles ≥ 95% of application volume (metric to be confirmed during rollout).\n\n"
            "Affected users/services: Branch Tellers (role transitions per 3.3.4), physical document archive.\n\n"
            "Transition requirements:\n"
            "- Applications in-flight at cutover must be completed through the legacy process before retirement\n"
            "- Physical document archive protocol must be finalized (currently out of scope — see 3.8 [D2])\n\n"
            "Communication: Branch staff to be notified per the socialization plan (4.3). "
            "No replacement product is planned — the digital portal IS the replacement."
        ),
        "expected_confidence_level": "HIGH",
        "notes": "Retirement trigger with honest metric, affected users, transition requirement, data closure addressed, lifecycle consistent, no invented ownership.",
    },
    {
        "field_id": "5.1",
        "quality": "MEDIUM",
        "content": "The old paper process will be retired once the new system is fully operational.",
        "expected_confidence_level": "MEDIUM",
        "notes": "Retirement intent present but no trigger, no affected users, no transition requirement, no data handling.",
    },
    {
        "field_id": "5.1",
        "quality": "POOR",
        "content": (
            "All legacy systems will be decommissioned immediately on go-live date. "
            "Data migration of 10 years of records will be completed in 2 weeks by the IT team."
        ),
        "expected_confidence_level": "LOW",
        "notes": "Invented immediate decommission, invented 10-year migration timeline (2 weeks), no transition for in-flight cases.",
    },
]


# ---------------------------------------------------------------------------
# Quick sanity check (not a production test — for calibration workflow use)
# ---------------------------------------------------------------------------

def get_fixtures_by_field(field_id: str) -> list[dict]:
    """Return the 3 fixtures for a specific field_id."""
    return [f for f in CALIBRATION_FIXTURES if f["field_id"] == field_id]


def get_fixtures_by_quality(quality: str) -> list[dict]:
    """Return all fixtures of a given quality level (GOOD, MEDIUM, POOR)."""
    return [f for f in CALIBRATION_FIXTURES if f["quality"] == quality]
