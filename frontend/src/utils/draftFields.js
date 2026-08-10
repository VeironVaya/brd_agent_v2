// Section tree for the 26-question BRD template.
//
// The dependsOn graph is resolved from the real business rules in
// brainstorming/brd_dependency_matrix_v1.xlsx ("Dependency Matrix" sheet),
// not hand-invented — mirrors backend/app/services/template_service.py
// exactly; keep the two in sync if either changes. Resolution rules
// (agreed 2026-08-10, see brainstorming/integration_1.md for the fuller
// writeup):
//   1. Strong (S) and Weak (W) marks are both treated as real
//      dependencies — no strength distinction exists in this schema.
//   2. A dependency listed on a non-leaf header row (e.g. "3.3 Business
//      Process") is propagated to every leaf under that header —
//      headers have no answer/status of their own to gate on.
//   3. Same propagation applied when a header is the *target* of a
//      dependency, except: if the header is the dependent leaf's own
//      ancestor, that edge is dropped entirely rather than expanded —
//      it would otherwise turn into the leaf depending on its own
//      later siblings, a forward-reference the spreadsheet's own
//      convention (unused here) would flag as a conflict.
//   4. The matrix's single "5" row/column (no separate "5.1" row
//      exists) maps directly onto our actual leaf, 5.1.

export const GENERAL_ROOM_ID = 'general'

export const SECTIONS = [
  {
    id: '1',
    title: 'Introduction',
    children: [
      {
        id: '1.1',
        title: 'Overview',
        children: [
          { id: '1.1.1', title: 'Background' },
          { id: '1.1.2', title: 'Business and Market Analysis', dependsOn: ['1.1.1'] },
          { id: '1.1.3', title: 'Relevant Historical Data', dependsOn: ['1.1.1'] },
        ],
      },
      { id: '1.2', title: 'Business Objective', dependsOn: ['1.1.1', '1.1.2', '1.1.3'] },
      { id: '1.3', title: 'Purpose of this Business Requirement', dependsOn: ['1.2'] },
      { id: '1.4', title: 'Program Type', dependsOn: ['1.1.1', '1.2'] },
      { id: '1.5', title: 'Business Risk', dependsOn: ['1.2', '1.3', '1.4'] },
    ],
  },
  {
    id: '2',
    title: 'Benefit Analysis',
    children: [
      { id: '2.1', title: 'Summary', dependsOn: ['1.1.3', '1.2', '1.3'] },
      { id: '2.2', title: 'Assumption and Calculation', dependsOn: ['1.1.3', '2.1'] },
    ],
  },
  {
    id: '3',
    title: 'Service Description',
    children: [
      { id: '3.1', title: 'General Requirement', dependsOn: ['1.2', '1.4', '2.1'] },
      { id: '3.2', title: 'Product / Service Specification', dependsOn: ['3.1'] },
      {
        id: '3.3',
        title: 'Business Process',
        children: [
          { id: '3.3.1', title: 'Business process impact', dependsOn: ['1.1.1', '3.1', '3.2'] },
          { id: '3.3.2', title: 'Description', dependsOn: ['3.1', '3.2'] },
          { id: '3.3.3', title: 'Security', dependsOn: ['3.1', '3.2', '3.3.2'] },
          { id: '3.3.4', title: 'Organization and policy', dependsOn: ['1.4', '3.1', '3.2', '3.3.2'] },
          {
            id: '3.3.5',
            title: 'Service Delivery Plan',
            dependsOn: ['1.4', '3.1', '3.2', '3.3.2', '3.3.4'],
          },
        ],
      },
      { id: '3.4', title: 'Complain Handling', dependsOn: ['3.2', '3.3.2'] },
      { id: '3.5', title: 'Reporting', dependsOn: ['2.2', '3.3.2'] },
      {
        id: '3.6',
        title: 'Monitoring',
        dependsOn: ['1.5', '3.5'],
      },
      {
        id: '3.7',
        title: 'Settlement Plan',
        dependsOn: ['2.2', '3.2'],
      },
      {
        id: '3.8',
        title: 'Assumptions and Dependencies',
        dependsOn: ['2.2', '3.3.1', '3.3.2', '3.3.3', '3.3.4', '3.3.5', '3.7'],
      },
    ],
  },
  {
    id: '4',
    title: 'Release Plan',
    children: [
      { id: '4.1', title: 'Target Ready for Service', dependsOn: ['3.1', '3.3.5', '3.8'] },
      { id: '4.2', title: 'Commercial Launch', dependsOn: ['2.1', '4.1'] },
      {
        id: '4.3',
        title: 'Internal Socialization Plan',
        dependsOn: ['3.3.4', '4.1'],
      },
      {
        id: '4.4',
        title: 'Rollout Scenario',
        dependsOn: ['1.4', '4.1', '4.2'],
      },
    ],
  },
  {
    id: '5',
    title: 'Product/Service Retirement Plan',
    children: [{ id: '5.1', title: 'Retirement Plan', dependsOn: ['1.5', '3.2', '4.4'] }],
  },
]

// Document Signoff is a boilerplate section — auto-filled placeholders, not
// gathered through chat, and excluded from the 26-leaf completion count.
export const BOILERPLATE_SECTIONS = [
  {
    id: 'signoff',
    title: 'Document Signoff',
    description:
      'Name / Role / Date placeholders for approvers — included automatically, not gathered through chat.',
  },
]

export function isLeaf(node) {
  return !node.children
}

/** Flat list of every leaf node (id, title, dependsOn, sectionId). */
export function flattenLeaves(sections = SECTIONS) {
  const leaves = []
  const walk = (nodes, topSectionId) => {
    for (const node of nodes) {
      if (isLeaf(node)) {
        leaves.push({ dependsOn: [], ...node, sectionId: topSectionId })
      } else {
        walk(node.children, topSectionId)
      }
    }
  }
  for (const top of sections) walk(top.children, top.id)
  return leaves
}

export const FIELD_ORDER = flattenLeaves().map((leaf) => leaf.id)

export const FIELD_META = Object.fromEntries(
  flattenLeaves().map((leaf) => [leaf.id, leaf]),
)

/**
 * A leaf's status is authored directly on its answer record (mirrors the
 * source prototype's data model): 'done' | 'progress' | 'ready' | 'locked'
 * | 'review'. When a conversation hasn't fully simulated an answer for a
 * leaf, fall back to a sensible default derived from the dependency graph.
 */
export function fieldState(fieldId, answers) {
  const answer = answers[fieldId]
  // 'flagged' takes priority over the raw stored status — the backend
  // never persists status='review' (chat_service only ever derives
  // 'done'/'progress'), it's a separately-computed boolean layered on
  // top each time (erd.md: recomputed on demand, never stored). Without
  // this check, fieldState could never return 'review' at all — the
  // DonutBadge's flag icon and the "needs review" bucket count would
  // silently stay 0 forever regardless of real flagged items, even
  // though the Review Flagged modal (reads flaggedItems directly,
  // bypassing fieldState) correctly showed them.
  if (answer?.flagged) return 'review'
  if (answer?.status) return answer.status

  const meta = FIELD_META[fieldId]
  if (!meta) return 'ready'
  // Bug fix: this used to check only whether dependsOn was non-empty, never
  // whether those dependencies were actually satisfied — so any leaf with
  // declared dependencies showed as permanently 'locked' even after they
  // were all done. Only invisible before because the placeholder dependency
  // graph was sparse; the real one (25 of 26 leaves have a dependency) made
  // it obvious immediately. isBlocked does the real recursive check.
  if (isBlocked(fieldId, answers)) return 'locked'
  return 'ready'
}

/** True if any of the leaf's dependencies aren't yet 'done'. */
export function isBlocked(fieldId, answers) {
  const meta = FIELD_META[fieldId]
  if (!meta?.dependsOn?.length) return false
  return meta.dependsOn.some((depId) => fieldState(depId, answers) !== 'done')
}

/** { done, total } for one top-level section, e.g. "5/12". */
export function sectionProgress(sectionId, answers) {
  const section = SECTIONS.find((s) => s.id === sectionId)
  if (!section) return { done: 0, total: 0 }
  const leaves = flattenLeaves([section])
  const done = leaves.filter((l) => fieldState(l.id, answers) === 'done').length
  return { done, total: leaves.length }
}

/** { done, total } across the whole 26-leaf template. */
export function overallProgress(answers) {
  const leaves = flattenLeaves()
  const done = leaves.filter((l) => fieldState(l.id, answers) === 'done').length
  return { done, total: leaves.length }
}

/** Counts for the DraftPanel's 4-bucket stats line. */
export function statusBuckets(answers) {
  const buckets = { answered: 0, ready: 0, locked: 0, needs_review: 0 }
  for (const id of FIELD_ORDER) {
    const status = fieldState(id, answers)
    if (status === 'done') buckets.answered += 1
    else if (status === 'progress' || status === 'ready') buckets.ready += 1
    else if (status === 'review') buckets.needs_review += 1
    else buckets[status] += 1
  }
  return buckets
}

export const CONFIDENCE_TIERS = ['HIGH', 'MEDIUM', 'LOW']

export function confidenceTier(confidencePct) {
  if (confidencePct == null) return null
  if (confidencePct >= 85) return 'HIGH'
  if (confidencePct >= 60) return 'MEDIUM'
  return 'LOW'
}

// Tailwind utility class per confidence tier — maps to the tokens defined
// in src/index.css (@theme --color-confidence-*).
export const CONFIDENCE_COLOR_CLASS = {
  HIGH: 'text-confidence-high',
  MEDIUM: 'text-confidence-medium',
  LOW: 'text-confidence-low',
  NONE: 'text-confidence-none',
}

export const STATUS_LABEL = {
  answered: 'Answered',
  ready: 'Ready',
  locked: 'Locked',
  needs_review: 'Need review',
}

/** Generic "still gathering" copy for a focused leaf that has no scripted chat thread. */
export function missingByStatus(status, note) {
  if (status === 'done') return 'Already answered — you can amend it below if anything changed.'
  if (status === 'progress') return 'Still gathering details — continue the thread below.'
  if (status === 'ready') return "Not started yet. Tell me about this and I'll capture it."
  if (status === 'review') return 'This answer was flagged for review — reply below to resolve it.'
  if (status === 'locked') return `${note} before this can start.`
  return ''
}
