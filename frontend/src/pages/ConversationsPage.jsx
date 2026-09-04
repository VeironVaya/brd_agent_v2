import { useEffect, useState, useMemo } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext.jsx'
import Logo from '../components/common/Logo.jsx'
import Button from '../components/common/Button.jsx'
import ConversationRow from '../components/Sidebar/ConversationRow.jsx'
import GroupCard from '../components/Sidebar/GroupCard.jsx'
import EmptyState from '../components/Sidebar/EmptyState.jsx'
import NewConversationModal from '../components/Sidebar/NewConversationModal.jsx'
import GroupModal from '../components/Sidebar/GroupModal.jsx'
import AssignGroupModal from '../components/Sidebar/AssignGroupModal.jsx'
import UserMenu from '../components/common/UserMenu.jsx'
import ConfirmModal from '../components/common/ConfirmModal.jsx'
import ShareModal from '../components/common/ShareModal.jsx'
import GroupShareModal from '../components/Sidebar/GroupShareModal.jsx'
import * as api from '../services/api.js'

export default function ConversationsPage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [conversations, setConversations] = useState([])
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState(false)
  const [query, setQuery] = useState('')
  const [searchParams, setSearchParams] = useSearchParams()
  const activeGroupId = searchParams.get('group') || null
  const tab = searchParams.get('tab') || 'owner'

  const setActiveGroupId = (id) => {
    setSearchParams(prev => {
      if (id) prev.set('group', id)
      else prev.delete('group')
      return prev
    })
  }

  const setTab = (newTab) => {
    setSearchParams(prev => {
      prev.set('tab', newTab)
      return prev
    })
  }

  // Modals
  const [newBrdOpen, setNewBrdOpen] = useState(false)
  const [logoutOpen, setLogoutOpen] = useState(false)
  const [shareTargetId, setShareTargetId] = useState(null)
  
  // Group modals
  const [groupModalMode, setGroupModalMode] = useState('create') // 'create' | 'edit'
  const [groupModalOpen, setGroupModalOpen] = useState(false)
  const [editingGroup, setEditingGroup] = useState(null) // { id, title, description }
  const [deleteGroupTarget, setDeleteGroupTarget] = useState(null) // { id, title }
  const [assignTarget, setAssignTarget] = useState(null) // { conversationId, currentGroupId }
  const [shareGroupTargetId, setShareGroupTargetId] = useState(null)

  useEffect(() => {
    let active = true
    Promise.all([api.listConversations(), api.listGroups()])
      .then(([convList, groupList]) => {
        if (active) {
          setConversations(convList)
          setGroups(groupList)
          setLoading(false)
        }
      })
      .catch(() => {
        if (active) {
          setFetchError(true)
          setLoading(false)
        }
      })
    return () => { active = false }
  }, [])

  async function refreshAll() {
    const [convList, groupList] = await Promise.all([api.listConversations(), api.listGroups()])
    setConversations(convList)
    setGroups(groupList)
  }

  // ── BRD handlers ──────────────────────────────────────────────────────────

  async function handleCreate({ title, context, requestorDirectorate, impactedStakeholders }) {
    const payload = { title, context, requestorDirectorate, impactedStakeholders }
    if (activeGroupId) {
      payload.groupId = activeGroupId
    }
    const { id } = await api.createConversation(payload)
    navigate(`/conversations/${id}`)
  }

  async function handleRename(id, title) {
    await api.updateConversationTitle(id, title)
    await refreshAll()
  }

  async function handleDelete(id) {
    await api.deleteConversation(id)
    await refreshAll()
  }

  async function handleAssignGroup(groupId) {
    if (!assignTarget) return
    await api.assignGroup(assignTarget.conversationId, groupId)
    await refreshAll()
    setAssignTarget(null)
  }

  // ── Group handlers ─────────────────────────────────────────────────────────

  async function handleCreateGroup({ title, description }) {
    await api.createGroup({ title, description })
    await refreshAll()
  }

  async function handleUpdateGroup({ title, description }) {
    if (!editingGroup) return
    await api.updateGroup(editingGroup.id, { title, description })
    await refreshAll()
  }

  async function handleDeleteGroup() {
    if (!deleteGroupTarget) return
    await api.deleteGroup(deleteGroupTarget.id)
    if (activeGroupId === deleteGroupTarget.id) {
      setActiveGroupId(null)
    }
    await refreshAll()
    setDeleteGroupTarget(null)
  }

  // ── Derived state ──────────────────────────────────────────────────────────

  const activeGroup = useMemo(() => groups.find(g => g.id === activeGroupId), [groups, activeGroupId])

  // Filter lists based on tab
  const ownedGroups = groups.filter((g) => g.role === 'owner')
  const sharedGroups = groups.filter((g) => g.role !== 'owner')

  const ownedBrds = conversations.filter((c) => c.role === 'owner')
  // We only show BRDs directly shared with user in the flat list, not ones shared via group
  // (actually api returns group-shared ones too, let's filter them out for the root 'shared with me' flat list if they belong to a group we already show)
  const sharedBrds = conversations.filter((c) => c.role !== 'owner')

  const activeGroupList = tab === 'owner' ? ownedGroups : sharedGroups
  const activeBrdList = tab === 'owner' ? ownedBrds : sharedBrds

  const filteredGroups = activeGroupList
    .map(g => ({
      ...g,
      brdCount: conversations.filter(c => c.groupId === g.id).length
    }))
    .filter((g) => {
      const q = query.toLowerCase()
      const titleMatches = g.title.toLowerCase().includes(q)
      const hasMatchingBrd = conversations.some(c => c.groupId === g.id && c.title.toLowerCase().includes(q))
      return titleMatches || hasMatchingBrd
    })
  
  const filteredBrds = activeBrdList.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))
  
  const isEmpty = !loading && conversations.length === 0 && groups.length === 0
  const isTabEmpty = !loading && !isEmpty && filteredGroups.length === 0 && filteredBrds.length === 0

  // For the root view ungrouped section
  const ungroupedBrds = filteredBrds.filter((c) => c.groupId === null)

  // For the active group view
  const activeGroupBrds = activeGroup ? conversations.filter((c) => c.groupId === activeGroup.id && c.title.toLowerCase().includes(query.toLowerCase())) : []

  return (
    <div className="w-full min-h-screen bg-white relative">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between gap-5 px-10 pt-8 pb-6 flex-wrap">
          <div className="flex items-center gap-3.5 min-w-0">
            <Logo size={34} />
            <div className="min-w-0">
              <div className="text-[21px] font-bold whitespace-nowrap overflow-hidden text-ellipsis flex items-center gap-2">
                {activeGroup ? (
                  <>
                    <button 
                      onClick={() => setActiveGroupId(null)}
                      className="hover:underline cursor-pointer bg-transparent border-none p-0 text-text-secondary"
                    >
                      Your BRDs
                    </button>
                    <span className="text-text-tertiary">/</span>
                    <span>{activeGroup.title}</span>
                  </>
                ) : (
                  'Your BRDs'
                )}
              </div>
              <div className="text-sm text-text-secondary mt-1 whitespace-nowrap overflow-hidden text-ellipsis">
                {activeGroup 
                  ? `${activeGroupBrds.length} BRDs` 
                  : isEmpty
                    ? 'No BRDs yet'
                    : tab === 'owner' ? 'Owned by you' : 'Shared with you'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 flex-shrink-0">
            {/* Search */}
            <div className="flex items-center gap-2 bg-white border border-border rounded-pill px-5.5 py-3 w-70 max-w-[32vw] shadow-[0_0_0_1px_rgba(0,0,0,.02),0_2px_6px_rgba(0,0,0,.04),0_4px_8px_rgba(0,0,0,.1)]">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#929292" strokeWidth="2" strokeLinecap="round" className="flex-shrink-0">
                <circle cx="11" cy="11" r="7" />
                <path d="M20 20l-4.5-4.5" />
              </svg>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search BRDs…"
                className="text-sm text-text-primary placeholder:text-text-tertiary outline-none w-full bg-transparent"
              />
            </div>
            
            {/* Action buttons */}
            {activeGroup ? (
              // Inside a group
              <>
                {activeGroup.role === 'owner' && (
                  <Button variant="secondary" onClick={() => setShareGroupTargetId(activeGroup.id)}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" />
                      <polyline points="16 6 12 2 8 6" />
                      <line x1="12" y1="2" x2="12" y2="15" />
                    </svg>
                    Share Group
                  </Button>
                )}
                {(activeGroup.role === 'owner' || activeGroup.role === 'editor') && (
                  <Button variant="primary" onClick={() => setNewBrdOpen(true)}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                      <path d="M12 5v14M5 12h14" />
                    </svg>
                    New BRD
                  </Button>
                )}
                {activeGroup.role === 'owner' && (
                  <GroupActionsMenu
                    onEdit={() => {
                      setEditingGroup({ id: activeGroup.id, title: activeGroup.title, description: activeGroup.description })
                      setGroupModalMode('edit')
                      setGroupModalOpen(true)
                    }}
                    onDelete={() => setDeleteGroupTarget({ id: activeGroup.id, title: activeGroup.title })}
                  />
                )}
              </>
            ) : (
              // Root view
              <>
                {tab === 'owner' && (
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setGroupModalMode('create')
                      setEditingGroup(null)
                      setGroupModalOpen(true)
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                      <path d="M12 11v6M9 14h6" />
                    </svg>
                    New Group
                  </Button>
                )}
                <Button variant="primary" onClick={() => setNewBrdOpen(true)}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M12 5v14M5 12h14" />
                  </svg>
                  New BRD
                </Button>
              </>
            )}
            <UserMenu onLogout={() => setLogoutOpen(true)} />
          </div>
        </div>

        {fetchError ? (
          <div className="flex flex-col items-center justify-center py-24 text-text-secondary text-sm gap-3">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 8v4M12 16h.01" />
            </svg>
            <span>Couldn't load your BRDs. Please try refreshing the page.</span>
          </div>
        ) : isEmpty && !activeGroup ? (
          <EmptyState onNewConversation={() => setNewBrdOpen(true)} />
        ) : activeGroup ? (
          /* ── Group View ─────────────────────────────── */
          <div className="px-10 pt-4 pb-10 flex flex-col gap-6">
            {activeGroup.description && (
              <div className="text-sm text-text-secondary mb-2">{activeGroup.description}</div>
            )}
            
            {activeGroupBrds.length === 0 ? (
               <div className="py-12 flex flex-col items-center justify-center border-2 border-dashed border-border-light rounded-xl">
                 <div className="text-[15px] font-semibold text-text-primary mb-1">This group is empty</div>
                 <div className="text-sm text-text-tertiary">Create a new BRD or move an existing one here.</div>
               </div>
            ) : (
              <div className="flex flex-col gap-4">
                {activeGroupBrds.map((c) => (
                  <ConversationRow
                    key={c.id}
                    conversation={c}
                    onRename={handleRename}
                    onDelete={handleDelete}
                    onShare={() => setShareTargetId(c.id)}
                    onAssignGroup={() => setAssignTarget({ conversationId: c.id, currentGroupId: c.groupId })}
                  />
                ))}
              </div>
            )}
          </div>
        ) : (
          /* ── Root View ─────────────────────────────── */
          <>
            {/* Tab switcher */}
            <div className="px-10 flex">
              <div className="inline-flex bg-bg-subtlest rounded-pill p-1 gap-0.5">
                <button
                  type="button"
                  onClick={() => { setTab('owner'); setQuery('') }}
                  className={`px-4 py-1.75 rounded-pill text-sm cursor-pointer border-none transition-colors ${
                    tab === 'owner' ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary bg-transparent'
                  }`}
                >
                  My BRDs ({ownedBrds.length + ownedGroups.length})
                </button>
                <button
                  type="button"
                  onClick={() => { setTab('shared'); setQuery('') }}
                  className={`px-4 py-1.75 rounded-pill text-sm cursor-pointer border-none transition-colors ${
                    tab === 'shared' ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary bg-transparent'
                  }`}
                >
                  Shared with me ({sharedBrds.length + sharedGroups.length})
                </button>
              </div>
            </div>

            {isTabEmpty ? (
              <EmptyState
                hideAction={tab === 'shared' || (tab === 'owner' && query.trim() !== '')}
                onNewConversation={() => setNewBrdOpen(true)}
                title={
                  query.trim() !== ''
                    ? 'No items match your search'
                    : tab === 'owner'
                      ? 'No items yet'
                      : 'Nothing shared with you yet'
                }
                description={
                  query.trim() !== ''
                    ? 'Try a different search.'
                    : tab === 'owner'
                      ? 'Start your first BRD and BRD-Agent will guide you section by section.'
                      : "When someone shares a BRD or Group with you, it'll show up here."
                }
              />
            ) : (
              <div className="px-10 pt-8 pb-10 flex flex-col gap-10">
                {/* Groups Grid */}
                {filteredGroups.length > 0 && (
                  <div>
                    <div className="text-[13px] font-semibold text-text-tertiary mb-4 uppercase tracking-wider">
                      Groups
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {filteredGroups.map(group => (
                        <GroupCard 
                          key={group.id} 
                          group={group} 
                          onClick={() => {
                            setActiveGroupId(group.id)
                            setQuery('')
                          }} 
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Ungrouped BRDs */}
                {ungroupedBrds.length > 0 && (
                  <div>
                    <div className="text-[13px] font-semibold text-text-tertiary mb-4 uppercase tracking-wider">
                      BRDs
                    </div>
                    <div className="flex flex-col gap-4">
                      {ungroupedBrds.map((c) => (
                        <ConversationRow
                          key={c.id}
                          conversation={c}
                          onRename={handleRename}
                          onDelete={handleDelete}
                          onShare={() => setShareTargetId(c.id)}
                          onAssignGroup={() => setAssignTarget({ conversationId: c.id, currentGroupId: c.groupId })}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* ── Modals ─────────────────────────────────────────────────────────── */}
      <NewConversationModal
        open={newBrdOpen}
        groupName={activeGroup?.title}
        onClose={() => setNewBrdOpen(false)}
        onCreate={handleCreate}
      />
      <GroupModal
        key={editingGroup?.id ?? 'create'}
        open={groupModalOpen}
        mode={groupModalMode}
        initialTitle={editingGroup?.title ?? ''}
        initialDesc={editingGroup?.description ?? ''}
        onClose={() => setGroupModalOpen(false)}
        onSave={groupModalMode === 'edit' ? handleUpdateGroup : handleCreateGroup}
      />
      <ConfirmModal
        open={!!deleteGroupTarget}
        onClose={() => setDeleteGroupTarget(null)}
        onConfirm={handleDeleteGroup}
        title="Delete folder?"
        description={`"${deleteGroupTarget?.title}" will be deleted. BRDs inside it will not be deleted, they will just be moved out of this folder.`}
        confirmLabel="Delete"
      />
      <AssignGroupModal
        open={!!assignTarget}
        groups={groups}
        currentGroupId={assignTarget?.currentGroupId ?? null}
        onClose={() => setAssignTarget(null)}
        onAssign={handleAssignGroup}
      />
      <ShareModal
        open={!!shareTargetId}
        onClose={() => {
          setShareTargetId(null)
          refreshAll()
        }}
        conversationId={shareTargetId}
      />
      <GroupShareModal
        open={!!shareGroupTargetId}
        onClose={() => {
          setShareGroupTargetId(null)
          refreshAll()
        }}
        groupId={shareGroupTargetId}
      />
      <ConfirmModal
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        onConfirm={async () => {
          setLogoutOpen(false)
          await logout()
        }}
        title="Log out?"
        description="You'll be signed out of BRD-Agent and returned to the sign-in screen."
        confirmLabel="Log out"
      />
    </div>
  )
}

// ── Small inline component for the group's 3-dot menu ───────────────────────
function GroupActionsMenu({ onEdit, onDelete }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="relative flex-shrink-0">
      <Button variant="secondary" onClick={() => setOpen((v) => !v)}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="5" r="1.6" />
          <circle cx="12" cy="12" r="1.6" />
          <circle cx="12" cy="19" r="1.6" />
        </svg>
      </Button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute top-11 right-0 bg-white border border-border rounded-btn shadow-dropdown z-20 overflow-hidden w-36">
            <button
              type="button"
              onClick={() => { setOpen(false); onEdit() }}
              className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-text-primary cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
              </svg>
              Edit
            </button>
            <button
              type="button"
              onClick={() => { setOpen(false); onDelete() }}
              className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-confidence-low cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                <path d="M3 6h18" /><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" /><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
              </svg>
              Delete
            </button>
          </div>
        </>
      )}
    </div>
  )
}
