import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from '../components/common/Logo.jsx'
import Button from '../components/common/Button.jsx'
import ConversationRow from '../components/Sidebar/ConversationRow.jsx'
import EmptyState from '../components/Sidebar/EmptyState.jsx'
import NewConversationModal from '../components/Sidebar/NewConversationModal.jsx'
import UserMenu from '../components/common/UserMenu.jsx'
import ConfirmModal from '../components/common/ConfirmModal.jsx'
import ShareModal from '../components/common/ShareModal.jsx'
import * as api from '../services/api.js'

export default function ConversationsPage() {
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [tab, setTab] = useState('owner') // 'owner' | 'shared'
  const [modalOpen, setModalOpen] = useState(false)
  const [logoutOpen, setLogoutOpen] = useState(false)
  const [shareTargetId, setShareTargetId] = useState(null)

  useEffect(() => {
    let active = true
    api.listConversations().then((list) => {
      if (active) {
        setConversations(list)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [])

  const owned = conversations.filter((c) => c.role === 'owner')
  const shared = conversations.filter((c) => c.role !== 'owner')
  const activeList = tab === 'owner' ? owned : shared
  const filtered = activeList.filter((c) => c.title.toLowerCase().includes(query.toLowerCase()))
  const isEmpty = !loading && conversations.length === 0
  const isTabEmpty = !loading && !isEmpty && filtered.length === 0

  async function handleCreate({ title, context, requestorDirectorate, impactedStakeholders }) {
    const { id } = await api.createConversation({ title, context, requestorDirectorate, impactedStakeholders })
    navigate(`/conversations/${id}`)
  }

  async function refreshList() {
    setConversations(await api.listConversations())
  }

  async function handleRename(id, title) {
    await api.updateConversationTitle(id, title)
    await refreshList()
  }

  async function handleDelete(id) {
    await api.deleteConversation(id)
    await refreshList()
  }

  return (
    <div className="w-full min-h-screen bg-white relative">
      <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between gap-5 px-10 pt-8 pb-6 flex-wrap">
        <div className="flex items-center gap-3.5 min-w-0">
          <Logo size={34} />
          <div className="min-w-0">
            <div className="text-[21px] font-bold whitespace-nowrap overflow-hidden text-ellipsis">
              Your Conversations
            </div>
            <div className="text-sm text-text-secondary mt-1 whitespace-nowrap overflow-hidden text-ellipsis">
              {isEmpty
                ? 'No conversations yet'
                : `${activeList.length} ${tab === 'owner' ? 'owned by you' : 'shared with you'} · most recent first`}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="flex items-center gap-2 bg-white border border-border rounded-pill px-5.5 py-3 w-70 max-w-[32vw] shadow-[0_0_0_1px_rgba(0,0,0,.02),0_2px_6px_rgba(0,0,0,.04),0_4px_8px_rgba(0,0,0,.1)]">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#929292" strokeWidth="2" strokeLinecap="round" className="flex-shrink-0">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-4.5-4.5" />
            </svg>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search conversations…"
              className="text-sm text-text-primary placeholder:text-text-tertiary outline-none w-full bg-transparent"
            />
          </div>
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
            New Conversation
          </Button>
          <UserMenu onLogout={() => setLogoutOpen(true)} />
        </div>
      </div>

      {isEmpty ? (
        <EmptyState onNewConversation={() => setModalOpen(true)} />
      ) : (
        <>
          <div className="px-10 flex">
            <div className="inline-flex bg-bg-subtlest rounded-pill p-1 gap-0.5">
              <button
                type="button"
                onClick={() => setTab('owner')}
                className={`px-4 py-1.75 rounded-pill text-sm cursor-pointer border-none transition-colors ${
                  tab === 'owner' ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary bg-transparent'
                }`}
              >
                My BRDs ({owned.length})
              </button>
              <button
                type="button"
                onClick={() => setTab('shared')}
                className={`px-4 py-1.75 rounded-pill text-sm cursor-pointer border-none transition-colors ${
                  tab === 'shared' ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary bg-transparent'
                }`}
              >
                Shared with me ({shared.length})
              </button>
            </div>
          </div>

          {isTabEmpty ? (
            <EmptyState
              hideAction={tab === 'shared' || (tab === 'owner' && query.trim() !== '')}
              onNewConversation={() => setModalOpen(true)}
              title={
                query.trim() !== ''
                  ? 'No conversations match your search'
                  : tab === 'owner'
                    ? 'No conversations yet'
                    : 'No BRDs shared with you yet'
              }
              description={
                query.trim() !== ''
                  ? 'Try a different search.'
                  : tab === 'owner'
                    ? 'Start your first BRD conversation and BRD-Agent will guide you section by section.'
                    : "When someone shares a BRD with you, it'll show up here."
              }
            />
          ) : (
            <div className="px-10 pt-4 pb-10 flex flex-col gap-4">
              {filtered.map((c) => (
                <ConversationRow
                  key={c.id}
                  conversation={c}
                  onRename={handleRename}
                  onDelete={handleDelete}
                  onShare={c.role === 'owner' ? () => setShareTargetId(c.id) : undefined}
                />
              ))}
            </div>
          )}
        </>
      )}
      </div>

      <NewConversationModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreate={handleCreate}
      />
      <ShareModal
        open={!!shareTargetId}
        onClose={() => {
          setShareTargetId(null)
          refreshList()
        }}
        conversationId={shareTargetId}
      />
      <ConfirmModal
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        onConfirm={() => {
          api.logout()
          navigate('/login')
        }}
        title="Log out?"
        description="You'll be signed out of BRD-Agent and returned to the sign-in screen."
        confirmLabel="Log out"
      />
    </div>
  )
}
