// Single API client — all network calls go through here, nowhere else
// (see CLAUDE.md). Talks to the real FastAPI backend (backend/) over
// HTTP. This file is the snake_case (wire) <-> camelCase (frontend)
// translation boundary CLAUDE.md's "Mocking strategy" always intended —
// components never see snake_case field names.

// NOTE: intentionally NOT `import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'` —
// `||` treats an explicitly-set empty string as falsy, which broke prod:
// the Docker build sets VITE_API_BASE_URL="" on purpose (same-origin,
// nginx proxies /api and /auth to the backend — see frontend/Dockerfile),
// but `"" || fallback` always evaluated to the fallback, so the browser
// tried to fetch http://localhost:8000 directly and got blocked by CORS.
// `??` only falls back when the value is null/undefined (unset), not on
// an intentional empty string.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'brdAgentToken'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 204) return null

  // 401 mid-session: token expired or revoked server-side.
  // Clear the stored token and notify AuthContext via a CustomEvent so
  // it can redirect to /login. api.js stays React-free — no imports of
  // navigate or context here.
  if (res.status === 401) {
    clearToken()
    window.dispatchEvent(new CustomEvent('auth:expired'))
    const data = await res.json().catch(() => null)
    const message = data?.message || data?.detail || 'Your session has expired. Please sign in again.'
    const err = new Error(message)
    err.code = data?.error
    err.status = 401
    throw err
  }

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const message = data?.message || data?.detail || 'Something went wrong. Please try again.'
    const err = new Error(message)
    err.code = data?.error
    err.status = res.status
    throw err
  }
  return data
}

// ---------------------------------------------------------------------------
// Formatting helpers — the backend sends raw timestamps; relative/human
// labels are a frontend display concern (see brainstorming/api_contract.md's
// note on why time_label was dropped from the wire shape).
// ---------------------------------------------------------------------------

function formatRelativeTime(isoString) {
  if (!isoString) return ''
  const diffMs = Math.max(0, Date.now() - new Date(isoString).getTime())
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return 'Updated just now'
  if (minutes < 60) return `Updated ${minutes} minute${minutes === 1 ? '' : 's'} ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `Updated ${hours} hour${hours === 1 ? '' : 's'} ago`
  const days = Math.floor(hours / 24)
  if (days === 1) return 'Updated yesterday'
  if (days < 7) return `Updated ${days} days ago`
  const weeks = Math.floor(days / 7)
  if (weeks < 5) return `Updated ${weeks} week${weeks === 1 ? '' : 's'} ago`
  return `Updated ${new Date(isoString).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`
}

function formatGeneratedDate(isoString) {
  return new Date(isoString).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

// ---------------------------------------------------------------------------
// Wire (snake_case) -> frontend (camelCase) mappers
// ---------------------------------------------------------------------------

function mapCustomSectionNode(node) {
  return {
    id: node.id,
    title: node.title,
    purpose: node.purpose ?? null,
    hasChildren: node.has_children,
    nestUnder: node.nest_under ?? null,
    children: (node.children || []).map(mapCustomSectionNode),
  }
}

function mapFlaggedItem(item) {
  return {
    fieldId: item.field_id,
    label: item.label,
    dependsOnLabel: item.depends_on_label,
    reason: item.reason,
  }
}

function mapConversationListItem(item) {
  return {
    id: item.id,
    title: item.title,
    timeLabel: formatRelativeTime(item.updated_at),
    answeredCount: item.answered_count,
    // "owner" | "editor" | "viewer" — the caller's own access to this BRD.
    // ownerName/ownerEmail are null for the caller's own conversations
    // (role === 'owner'); populated for shared ones ("Shared by Priya Shah").
    role: item.role,
    ownerName: item.owner_name ?? null,
    ownerEmail: item.owner_email ?? null,
    groupId: item.group_id ?? null,
  }
}

function mapGroup(item) {
  return {
    id: item.id,
    title: item.title,
    description: item.description ?? null,
    role: item.role,
  }
}

function mapConversationDetail(detail) {
  return {
    id: detail.id,
    title: detail.title,
    requestorDirectorate: detail.requestor_directorate || null,
    impactedStakeholders: detail.impacted_stakeholders || [],
    timeLabel: formatRelativeTime(detail.updated_at),
    docVersion: detail.last_generated_version || null,
    docGeneratedLabel: detail.last_generated_at ? `Generated ${formatGeneratedDate(detail.last_generated_at)}` : null,
    answeredCount: detail.answered_count,
    focusedFieldId: detail.focused_field_id,
    role: detail.role,
    // answers/messages values already use single-word keys matching the
    // frontend's expectations 1:1 (status, completeness, confidence,
    // answer, missing / id, role, text) — no key translation needed.
    answers: Object.fromEntries(
      Object.entries(detail.answers).map(([key, answer]) => [key, { ...answer, choiceData: answer.choice_data || null }]),
    ),
    customSections: (detail.custom_sections || []).map(mapCustomSectionNode),
    flaggedItems: (detail.flagged_items || []).map(mapFlaggedItem),
    messages: detail.messages,
  }
}

function mapCollaborator(item) {
  return {
    id: item.id,
    userId: item.user_id,
    email: item.email,
    name: item.name,
    role: item.role,
  }
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function register({ email, password, name }) {
  const data = await request('/auth/register', { method: 'POST', body: { email, password, name } })
  setToken(data.token)
  return data.user
}

export async function login({ email, password }) {
  const data = await request('/auth/login', { method: 'POST', body: { email, password } })
  setToken(data.token)
  return data.user
}

export async function logout() {
  // The API call must happen BEFORE clearToken() — the backend now
  // actually revokes this specific token server-side (see
  // api_contract.md §1), so it needs the token still attached to know
  // which one to invalidate. Clearing local storage first would send an
  // unauthenticated request and silently skip revocation entirely.
  try {
    await request('/auth/logout', { method: 'POST' })
  } catch {
    // Revocation is best-effort from the client's perspective — even if
    // this fails (offline, expired token, etc.), we still want the user
    // logged out of *this* browser, which clearToken() below guarantees.
  } finally {
    clearToken()
  }
}

export async function getSession() {
  if (!getToken()) return null
  try {
    const data = await request('/auth/session')
    return data.user
  } catch {
    clearToken()
    return null
  }
}

// ---------------------------------------------------------------------------
// Conversations
// ---------------------------------------------------------------------------

export async function listConversations() {
  const data = await request('/api/conversations')
  return data.conversations.map(mapConversationListItem)
}

export async function getConversation(id) {
  const data = await request(`/api/conversations/${id}`)
  return mapConversationDetail(data)
}

export async function createConversation({ title, context, requestorDirectorate, impactedStakeholders, groupId }) {
  const data = await request('/api/conversations', {
    method: 'POST',
    body: {
      title,
      context,
      requestor_directorate: requestorDirectorate || null,
      impacted_stakeholders: impactedStakeholders || [],
      group_id: groupId || null,
    },
  })
  return { id: data.id }
}

export async function updateConversationTitle(conversationId, title) {
  const data = await request(`/api/conversations/${conversationId}`, { method: 'PATCH', body: { title } })
  return { id: data.id, title: data.title }
}

export async function deleteConversation(conversationId) {
  await request(`/api/conversations/${conversationId}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Groups — organise owned BRDs into named collections.
// ---------------------------------------------------------------------------

export async function listGroups() {
  const data = await request('/api/groups')
  return (data.groups || []).map(mapGroup)
}

export async function createGroup({ title, description }) {
  const data = await request('/api/groups', {
    method: 'POST',
    body: { title, description: description || null },
  })
  return mapGroup(data)
}

export async function updateGroup(groupId, { title, description }) {
  const data = await request(`/api/groups/${groupId}`, {
    method: 'PATCH',
    body: { title, description: description || null },
  })
  return mapGroup(data)
}

export async function deleteGroup(groupId) {
  await request(`/api/groups/${groupId}`, { method: 'DELETE' })
}

export async function assignGroup(conversationId, groupId) {
  await request(`/api/conversations/${conversationId}/group`, {
    method: 'PATCH',
    body: { group_id: groupId },
  })
}

// ---------------------------------------------------------------------------
// Group Sharing
// ---------------------------------------------------------------------------

export async function addGroupCollaborator(groupId, { email, role }) {
  const data = await request(`/api/groups/${groupId}/collaborators`, {
    method: 'POST',
    body: { email, role },
  })
  return mapCollaborator(data)
}

export async function listGroupCollaborators(groupId) {
  const data = await request(`/api/groups/${groupId}/collaborators`)
  return (data.collaborators || []).map(mapCollaborator)
}

export async function updateGroupCollaboratorRole(groupId, collaboratorId, role) {
  const data = await request(`/api/groups/${groupId}/collaborators/${collaboratorId}`, {
    method: 'PATCH',
    body: { role },
  })
  return mapCollaborator(data)
}

export async function removeGroupCollaborator(groupId, collaboratorId) {
  await request(`/api/groups/${groupId}/collaborators/${collaboratorId}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Sharing — owner-only management of who else can access a conversation.
// `role` is "editor" | "viewer" (owner is implicit, never a collaborator row).
// ---------------------------------------------------------------------------

export async function shareConversation(conversationId, { email, role }) {
  const data = await request(`/api/conversations/${conversationId}/collaborators`, {
    method: 'POST',
    body: { email, role },
  })
  return mapCollaborator(data)
}

export async function listCollaborators(conversationId) {
  const data = await request(`/api/conversations/${conversationId}/collaborators`)
  return (data.collaborators || []).map(mapCollaborator)
}

export async function updateCollaboratorRole(conversationId, collaboratorId, role) {
  const data = await request(`/api/conversations/${conversationId}/collaborators/${collaboratorId}`, {
    method: 'PATCH',
    body: { role },
  })
  return mapCollaborator(data)
}

export async function removeCollaborator(conversationId, collaboratorId) {
  await request(`/api/conversations/${conversationId}/collaborators/${collaboratorId}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Chat / Rooms
// ---------------------------------------------------------------------------

export async function postMessage(conversationId, roomId, text) {
  const data = await request(`/api/conversations/${conversationId}/rooms/${roomId}/messages`, {
    method: 'POST',
    body: { text },
  })
  return { messages: data.messages }
}

export async function initChatRoom(conversationId, roomId) {
  const data = await request(`/api/conversations/${conversationId}/rooms/${roomId}/init`, {
    method: 'POST',
  })
  return { messages: data.messages }
}

export async function saveChoices(conversationId, sectionId, choiceData) {
  const data = await request(`/api/conversations/${conversationId}/sections/${sectionId}/choices`, {
    method: 'PUT',
    body: { choice_data: choiceData },
  })
  return {
    status: data.status,
    completeness: data.completeness,
    confidence: data.confidence,
    answer: data.answer,
    missing: data.missing,
    choiceData: data.choice_data,
  }
}

// ---------------------------------------------------------------------------
// Custom Sections
// ---------------------------------------------------------------------------

/**
 * `target` mirrors utils/customSectionTree.js#getContainerOptions:
 *   - null                      -> standalone top-level entry
 *   - { kind: 'template', id }  -> nested under that template section
 *   - { kind: 'custom', id }    -> appended as a child of that custom node
 */
export async function addCustomSectionNode(conversationId, target, payload) {
  const data = await request(`/api/conversations/${conversationId}/custom-sections`, {
    method: 'POST',
    body: {
      target: target ? { kind: target.kind, id: target.id } : null,
      title: payload.title,
      has_children: !!payload.hasChildren,
      purpose: payload.purpose || null,
    },
  })
  return {
    id: data.id,
    title: data.title,
    purpose: data.purpose ?? null,
    hasChildren: data.has_children,
    children: [],
  }
}

export async function renameCustomSectionNode(conversationId, nodeId, title) {
  await request(`/api/conversations/${conversationId}/custom-sections/${nodeId}`, {
    method: 'PATCH',
    body: { title },
  })
}

export async function removeCustomSectionNode(conversationId, nodeId) {
  await request(`/api/conversations/${conversationId}/custom-sections/${nodeId}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Review
// ---------------------------------------------------------------------------

export async function recomputeReview(conversationId) {
  const data = await request(`/api/conversations/${conversationId}/review/recompute`, { method: 'POST' })
  return { flaggedItems: (data.flagged_items || []).map(mapFlaggedItem) }
}

// ---------------------------------------------------------------------------
// Document Generation / Export
// ---------------------------------------------------------------------------

let forceNextGenerateError = false

/** Dev-only hook so the Export flow's error state is reachable from the UI. */
export function setForceNextGenerateError(value) {
  forceNextGenerateError = value
}

export async function generateDocument(conversationId, format) {
  if (forceNextGenerateError) {
    forceNextGenerateError = false
    throw new Error("We couldn't generate this document. Please try again.")
  }
  const data = await request(`/api/conversations/${conversationId}/generate`, {
    method: 'POST',
    body: { format },
  })
  return { filename: data.filename, markdown: data.markdown }
}
