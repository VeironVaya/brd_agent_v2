// Fixture data ported verbatim from the Figma prototype's own component
// state (frontend/design-reference/*.dc.html). Centralized here so
// src/services/api.js is the only thing that needs to change once a real
// backend exists (see CLAUDE.md "Mocking strategy").

import { GENERAL_ROOM_ID, FIELD_ORDER } from '../utils/draftFields.js'

// ---------------------------------------------------------------------------
// Conversations list (Container_2 / "Conversations 1 - List.dc.html")
// ---------------------------------------------------------------------------

export const CONVERSATIONS_META = [
  {
    id: 'untitled-brd',
    title: 'Untitled BRD',
    timeLabel: 'Created 12 minutes ago',
    answeredCount: 0,
  },
  {
    id: 'q3-vendor-onboarding',
    title: 'Q3 Vendor Onboarding Platform',
    timeLabel: 'Updated 2 hours ago',
    answeredCount: 14,
  },
  {
    id: 'warehouse-automation',
    title: 'Warehouse Automation BRD',
    timeLabel: 'Updated yesterday',
    answeredCount: 26,
  },
  {
    id: 'data-retention-policy',
    title: 'Data Retention Policy Update',
    timeLabel: 'Updated 4 days ago',
    answeredCount: 23,
  },
  {
    id: 'customer-support-chatbot',
    title: 'Customer Support Chatbot Revamp',
    timeLabel: 'Updated 2 weeks ago',
    answeredCount: 4,
  },
]

// ---------------------------------------------------------------------------
// Q3 Vendor Onboarding Platform — full workspace detail
// (Container_3/4/5 · "Workspace *.dc.html")
// ---------------------------------------------------------------------------

const q3Answers = {
  '1.1.1': { status: 'done', completeness: 100, confidence: 92, answer: 'Vendor onboarding for indirect suppliers is currently manual and email-based, taking 3–4 weeks per vendor on average.' },
  '1.1.2': { status: 'done', completeness: 100, confidence: 88, answer: 'Peer companies use automated onboarding platforms; industry benchmarks put onboarding under 5 days.' },
  '1.1.3': { status: 'done', completeness: 100, confidence: 90, answer: 'Procurement processed 640 new vendor requests last year; 22% were delayed by missing compliance docs.' },
  '1.2': { status: 'done', completeness: 100, confidence: 95, answer: 'Reduce vendor onboarding time from weeks to days and cut manual data entry by 70%.' },
  '1.3': { status: 'done', completeness: 100, confidence: 97, answer: 'Define requirements for a self-service vendor onboarding platform integrated with SAP Ariba.' },
  '1.4': { status: 'done', completeness: 100, confidence: 99, answer: 'New application.' },
  '1.5': { status: 'done', completeness: 100, confidence: 85, answer: "Delayed rollout could extend the current onboarding bottleneck into next fiscal year's vendor renewal cycle." },

  '2.1': { status: 'done', completeness: 100, confidence: 90, answer: 'Estimated annual savings of 1,800 procurement hours and faster vendor activation.' },
  '2.2': { status: 'done', completeness: 100, confidence: 82, answer: 'Savings based on an average 4-hour manual review time per vendor across ~450 annual onboardings.' },

  '3.1': { status: 'done', completeness: 100, confidence: 93, answer: 'Web-based self-service portal for vendors to submit and track onboarding status.' },
  '3.2': {
    status: 'progress',
    completeness: 45,
    confidence: 70,
    missing: [
      'Which reporting fields need to feed the BI warehouse',
      'Whether the OCR accuracy target also applies to compliance docs',
      'Confirmation of the 40% scanned-PDF volume estimate',
    ],
  },
  '3.3.1': { status: 'done', completeness: 100, confidence: 87, answer: 'Replaces manual email intake; Procurement shifts from data entry to exception handling.' },
  '3.3.2': { status: 'done', completeness: 100, confidence: 89, answer: 'Vendors self-register, upload documents, and receive automated status updates.' },
  '3.3.3': {
    status: 'review',
    completeness: 45,
    confidence: 54,
    answer: 'Encryption-at-rest requirement and access control model (RBAC vs. ABAC) are unresolved.',
    flagged: true,
    missing: [
      'Encryption-at-rest requirement for scanned contract PDFs',
      'Access control model (RBAC vs. ABAC) not yet decided',
    ],
  },
  '3.3.4': {
    status: 'ready',
    missing: [
      'Which team owns the vendor master data policy',
      'Whether Procurement or IT signs off on policy changes',
      'Any existing policy documents to reference',
    ],
  },
  '3.3.5': {
    status: 'locked',
    missing: [
      'Delivery/support model for the platform once live',
      'Who provides day-2 operational support',
    ],
  },
  '3.4': { status: 'done', completeness: 100, confidence: 84, answer: 'Vendor disputes route to a shared Procurement inbox with a 3-business-day SLA.' },
  '3.5': {
    status: 'review',
    completeness: 55,
    confidence: 61,
    answer: 'Report frequency and recipient list are missing; not yet confirmed to meet audit requirements.',
    flagged: true,
    missing: ['Report frequency (daily vs. weekly) not specified', 'Recipient list for exception reports'],
  },
  '3.6': {
    status: 'locked',
    missing: ['Whether monitoring is required for this platform', 'Alerting thresholds, if required'],
  },
  '3.7': {
    status: 'locked',
    missing: ['Whether financial settlement applies here', 'Settlement cadence, if applicable'],
  },
  '3.8': { status: 'done', completeness: 100, confidence: 79, answer: 'Assumes SAP Ariba remains system of record; OCR accuracy target still pending confirmation.' },

  '4.1': { status: 'locked', missing: ['Concrete target date or milestone for readiness', 'Reason for any uncertainty, if not yet fixed'] },
  '4.2': { status: 'locked', missing: ['Commercial launch plan and timing, consistent with the readiness date'] },
  '4.3': { status: 'locked', missing: ['Whether internal rollout/training is needed', 'Audience and timing, if needed'] },
  '4.4': { status: 'locked', missing: ['Whether a phased or big-bang rollout is planned'] },

  '5.1': { status: 'locked', missing: ['Retirement approach, or explicit confirmation that none applies yet'] },

  // Custom sections get their own Room + answer just like template leaves
  // (see naming glossary in CLAUDE.md). cs1 is answered (with a chat
  // thread below); cs2-1 is answered without a scripted thread; cs2-2-1
  // is left unanswered to demonstrate the "ready, tap to start" state.
  cs1: { status: 'done', completeness: 100, confidence: 91, answer: 'Escalations route to the on-call Procurement lead within 4 business hours; SLA breaches page the Vendor Ops manager directly.' },
  'cs2-1': { status: 'done', completeness: 100, confidence: 74, answer: 'EMEA rollout starts with UK and Germany, contingent on GDPR data residency sign-off from Legal.' },
}

const q3FlaggedItems = [
  {
    fieldId: '3.3.3',
    label: '3.3.3 Security',
    dependsOnLabel: '3.2 Product / Service Specification',
    reason:
      '3.2 Product / Service Specification was updated — its answer no longer matches what this item assumed. Re-verify encryption-at-rest and access control requirements against the new data sources.',
  },
  {
    fieldId: '3.5',
    label: '3.5 Reporting',
    dependsOnLabel: '3.2 Product / Service Specification',
    reason:
      '3.2 Product / Service Specification was updated — reporting fields may need to change to match the new data sources.',
  },
]

const q3CustomSections = [
  // Nested under template section 3.3 — demonstrates a custom node inline
  // in the outline, code computed as 3.3.6 (continues after 3.3.1–3.3.5).
  { id: 'cs1', title: 'Vendor Escalation Path', hasChildren: false, nestUnder: '3.3', children: [] },
  // Standalone group with nested children, three levels deep out of the
  // box (code 6, 6.1, 6.2, 6.2.1) — proves arbitrary depth works without
  // requiring manual setup first.
  {
    id: 'cs2',
    title: 'Regional Rollout Notes',
    hasChildren: true,
    nestUnder: null,
    children: [
      { id: 'cs2-1', title: 'EMEA', hasChildren: false, children: [] },
      {
        id: 'cs2-2',
        title: 'APAC',
        hasChildren: true,
        children: [{ id: 'cs2-2-1', title: 'Singapore pilot', hasChildren: false, children: [] }],
      },
    ],
  },
]

const q3Messages = {
  '3.2': [
    { id: 'm1', role: 'agent', text: 'What data sources will feed the vendor onboarding platform, and where does each one currently live (system of record)?' },
    { id: 'm2', role: 'user', text: "We'll pull vendor master data, contract terms, and compliance docs. Should be pretty straightforward." },
    { id: 'm3', role: 'agent', text: '"Pretty straightforward" isn\'t something I can put in the document. Which system holds vendor master data today, and are contract terms structured fields or scanned PDFs?' },
    { id: 'm4', role: 'user', text: "Vendor master data lives in SAP Ariba. Contract terms are a mix — about 60% structured fields, 40% scanned PDFs we'd need to OCR." },
    { id: 'm5', role: 'assumption', text: 'Assumption logged — OCR accuracy target not yet specified. Added to Assumptions & Dependencies.' },
    { id: 'm6', role: 'agent', text: 'Logged. One more: compliance docs (W-9s, insurance certificates) — do those need automatic validation, or is manual review acceptable for this phase?' },
  ],
  // Long thread on purpose — used to verify the message thread scrolls
  // independently of the header/input, per user feedback.
  '3.3.4': [
    { id: 'o1', role: 'agent', text: 'Who owns the vendor master data policy today — is that Procurement, IT, or a shared function?' },
    { id: 'o2', role: 'user', text: "It's owned by Procurement, but IT maintains the SAP Ariba integration that enforces it." },
    { id: 'o3', role: 'agent', text: 'Got it. When the policy changes — say, a new required field for vendor onboarding — who has final sign-off: Procurement alone, or does IT need to approve too?' },
    { id: 'o4', role: 'user', text: 'Procurement owns the business rules. IT only signs off if the change requires a schema or integration update on the Ariba side.' },
    { id: 'o5', role: 'agent', text: "That's a useful distinction. Is there a documented escalation path if Procurement and IT disagree on a policy change, or does that go up to a shared steering committee?" },
    { id: 'o6', role: 'user', text: 'There\'s a monthly Vendor Data Governance meeting with reps from both teams. Anything unresolved there goes to the CPO and CIO jointly.' },
    { id: 'o7', role: 'agent', text: 'Are there any existing policy documents I should reference for the standard checklist — a data governance charter, a vendor onboarding SOP, anything already written down?' },
    { id: 'o8', role: 'user', text: 'Yes — there\'s a "Vendor Master Data Governance Charter" from 2024. I can share the doc ID if that helps ground the answers.' },
    { id: 'o9', role: 'assumption', text: 'Assumption logged — exact charter document ID not yet provided. Added to Assumptions & Dependencies.' },
    { id: 'o10', role: 'agent', text: 'Thanks, no rush on the doc ID — a follow-up link works too. One more: does the policy distinguish between domestic and international vendors, or is ownership the same regardless of vendor location?' },
    { id: 'o11', role: 'user', text: 'International vendors go through an extra compliance review by Legal before Procurement can approve them, but ownership of the policy itself stays with Procurement either way.' },
    { id: 'o12', role: 'agent', text: 'Understood. Last one for this section: is there a defined SLA for how quickly a policy exception request gets reviewed, or is that handled case by case?' },
    { id: 'o13', role: 'user', text: 'Case by case today — that\'s actually one of the pain points we want this platform to help standardize.' },
    { id: 'o14', role: 'agent', text: 'Noted — I\'ll flag that as a gap rather than assume a target SLA. That\'s everything I need for Organization and policy for now; you can move on to the next item whenever you\'re ready.' },
  ],
  cs1: [
    { id: 'p1', role: 'agent', text: "This is a custom section — no fixed questions, so tell me what \"Vendor Escalation Path\" should cover and I'll capture it." },
    { id: 'p2', role: 'user', text: 'If a vendor issue blows past SLA, it should escalate to the on-call Procurement lead within 4 business hours, and page Vendor Ops if that SLA is also missed.' },
    { id: 'p3', role: 'agent', text: 'Logged. Anything about how the vendor themselves gets notified during an escalation, or is that internal-only for now?' },
  ],
  [GENERAL_ROOM_ID]: [],
}

// ---------------------------------------------------------------------------
// Warehouse Automation BRD — complete (26/26), used for the export flow
// (Container_6 · "Export *.dc.html")
// ---------------------------------------------------------------------------

const warehouseItems = [
  ['1.1.1', 'Manual picking across three distribution centers is at capacity; peak-season order accuracy has dropped to 94%.'],
  ['1.1.2', 'Competitors operating automated fulfillment centers report 30% higher throughput per square foot.'],
  ['1.1.3', 'Order volume grew 42% over the past two years; labor costs for picking rose in step.'],
  ['1.2', 'Increase picking throughput by 60% and reduce mis-picks below 0.5%.'],
  ['1.3', 'Define requirements for an automated storage and retrieval system (AS/RS) across three distribution centers.'],
  ['1.4', 'New application.'],
  ['1.5', 'Delayed automation risks missing peak holiday volume commitments next year.'],
  ['2.1', 'Projected $4.2M annual savings from reduced labor and error-related returns.'],
  ['2.2', 'Savings based on a 60% throughput increase and mis-pick rate dropping from 3% to 0.5%.'],
  ['3.1', 'Automated storage and retrieval system integrated with the existing WMS.'],
  ['3.2', 'AS/RS handles small-parts and each-picking totes; pick-to-light stations complete final order assembly; integrates with the existing WMS via REST API.'],
  ['3.3.1', 'Manual picking roles shift to system oversight and exception handling.'],
  ['3.3.2', 'Robotic shuttles retrieve totes; pick-to-light stations handle final order assembly.'],
  ['3.3.3', 'Role-based access to the control system; audit log for all manual overrides.'],
  ['3.3.4', 'Distribution Center Operations owns the system; IT co-owns integration with the WMS.'],
  ['3.3.5', '24/7 operation with a dedicated on-site maintenance team during business hours.'],
  ['3.4', 'Fulfillment errors route to a shared Ops inbox with a same-day resolution target.'],
  ['3.5', 'Daily throughput and accuracy dashboards; weekly exception reports to Ops leadership.'],
  ['3.6', 'Real-time equipment health monitoring with automated maintenance alerts.'],
  ['3.7', 'Not applicable — no financial settlement is involved.'],
  ['3.8', 'Assumes WMS integration is complete before AS/RS go-live.'],
  ['4.1', 'Target readiness: Q2 next year, ahead of peak season.'],
  ['4.2', 'Phased activation starting with the largest distribution center.'],
  ['4.3', 'Operations training begins six weeks before go-live at each site.'],
  ['4.4', 'Phased rollout across three distribution centers, one per quarter.'],
  ['5.1', 'Manual picking stations decommissioned once each site reaches full automation capacity.'],
]

const warehouseAnswers = Object.fromEntries(
  warehouseItems.map(([id, answer]) => [id, { status: 'done', completeness: 100, confidence: 90, answer }]),
)

const warehouseSectionDescriptions = {
  1: 'Covers background, business objective, purpose, program type, and business risk for the proposed warehouse automation initiative.',
  2: 'Projected labor savings, throughput improvements, and payback period based on current warehouse volumes.',
  3: 'Functional requirements, business process changes, security, and reporting for the automated fulfillment system.',
  4: 'Target readiness date, commercial launch milestones, and phased rollout scenario across three distribution centers.',
  5: 'Sunset plan for the legacy manual picking process once automation reaches full capacity.',
}

// ---------------------------------------------------------------------------
// Lightweight conversations — only aggregate progress is shown in the
// mockups for these, so leaves are answered in FIELD_ORDER up to the target
// count with generic placeholder content.
// ---------------------------------------------------------------------------

function genericAnswers(count) {
  const answers = {}
  for (let i = 0; i < count; i++) {
    answers[FIELD_ORDER[i]] = {
      status: 'done',
      completeness: 100,
      confidence: 80,
      answer: 'Captured via chat during the initial drafting pass.',
    }
  }
  return answers
}

// ---------------------------------------------------------------------------

export const CONVERSATION_DETAILS = {
  'untitled-brd': {
    answers: {},
    customSections: [],
    flaggedItems: [],
    messages: { [GENERAL_ROOM_ID]: [] },
    focusedFieldId: '1.1.1',
  },
  'q3-vendor-onboarding': {
    answers: q3Answers,
    customSections: q3CustomSections,
    flaggedItems: q3FlaggedItems,
    messages: q3Messages,
    focusedFieldId: '3.2',
  },
  'warehouse-automation': {
    answers: warehouseAnswers,
    customSections: [],
    flaggedItems: [],
    messages: { [GENERAL_ROOM_ID]: [] },
    focusedFieldId: '1.1.1',
    sectionDescriptions: warehouseSectionDescriptions,
    docVersion: 'Version 1.0',
    docGeneratedLabel: 'Generated August 5, 2026',
  },
  'data-retention-policy': {
    answers: genericAnswers(23),
    customSections: [],
    flaggedItems: [],
    messages: { [GENERAL_ROOM_ID]: [] },
    focusedFieldId: '1.1.1',
  },
  'customer-support-chatbot': {
    answers: genericAnswers(4),
    customSections: [],
    flaggedItems: [],
    messages: { [GENERAL_ROOM_ID]: [] },
    focusedFieldId: '1.1.1',
  },
}
