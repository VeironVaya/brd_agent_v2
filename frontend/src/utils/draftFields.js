// Section tree for the 26-question BRD template.
// Ported directly from the Figma prototype's own component logic
// (frontend/design-reference/Workspace 1 - Main.dc.html) — that file is the
// single source of truth for dependency graph, statuses, and copy.

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
          { id: '1.1.2', title: 'Business and Market Analysis' },
          { id: '1.1.3', title: 'Relevant Historical Data' },
        ],
      },
      { id: '1.2', title: 'Business Objective' },
      { id: '1.3', title: 'Purpose of this Business Requirement' },
      { id: '1.4', title: 'Program Type' },
      { id: '1.5', title: 'Business Risk' },
    ],
  },
  {
    id: '2',
    title: 'Benefit Analysis',
    children: [
      { id: '2.1', title: 'Summary' },
      { id: '2.2', title: 'Assumption and Calculation' },
    ],
  },
  {
    id: '3',
    title: 'Service Description',
    children: [
      { id: '3.1', title: 'General Requirement' },
      { id: '3.2', title: 'Product / Service Specification' },
      {
        id: '3.3',
        title: 'Business Process',
        children: [
          { id: '3.3.1', title: 'Business process impact' },
          { id: '3.3.2', title: 'Description' },
          { id: '3.3.3', title: 'Security' },
          { id: '3.3.4', title: 'Organization and policy' },
          {
            id: '3.3.5',
            title: 'Service Delivery Plan',
            dependsOn: ['3.3.4'],
          },
        ],
      },
      { id: '3.4', title: 'Complain Handling' },
      { id: '3.5', title: 'Reporting' },
      {
        id: '3.6',
        title: 'Monitoring',
        dependsOn: ['3.5'],
      },
      {
        id: '3.7',
        title: 'Settlement Plan',
        dependsOn: ['2.2'],
      },
      { id: '3.8', title: 'Assumptions and Dependencies' },
    ],
  },
  {
    id: '4',
    title: 'Release Plan',
    children: [
      { id: '4.1', title: 'Target Ready for Service', dependsOn: ['3.3.5', '3.8'] },
      { id: '4.2', title: 'Commercial Launch', dependsOn: ['4.1'] },
      {
        id: '4.3',
        title: 'Internal Socialization Plan',
        dependsOn: ['3.3.4'],
      },
      {
        id: '4.4',
        title: 'Rollout Scenario',
        dependsOn: ['4.2'],
      },
    ],
  },
  {
    id: '5',
    title: 'Product/Service Retirement Plan',
    children: [{ id: '5.1', title: 'Retirement Plan', dependsOn: ['4.4'] }],
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
  if (answer?.status) return answer.status

  const meta = FIELD_META[fieldId]
  if (!meta) return 'ready'
  if (meta.dependsOn?.length) return 'locked'
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
