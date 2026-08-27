import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import RenameModal from '../common/RenameModal.jsx'
import ConfirmModal from '../common/ConfirmModal.jsx'
import RoleBadge from '../common/RoleBadge.jsx'

export default function ConversationRow({ conversation, onRename, onDelete, onShare, onAssignGroup }) {
  const navigate = useNavigate()
  const percent = Math.round((conversation.answeredCount / 26) * 100)
  const isOwner = conversation.role === 'owner'
  const [menuOpen, setMenuOpen] = useState(false)
  const [renameOpen, setRenameOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  return (
    <div className="flex items-center justify-between gap-6 flex-wrap bg-white border border-border-light rounded-[14px] px-6 py-5">
      <div className="flex-1 min-w-55">
        <div className="flex items-center gap-2">
          <div className="text-base font-semibold">{conversation.title}</div>
          {!isOwner && <RoleBadge role={conversation.role} />}
        </div>
        <div className="text-sm text-text-secondary mt-1">
          {isOwner
            ? `${conversation.timeLabel} · ${conversation.answeredCount} of 26 answered`
            : `Shared by ${conversation.ownerName} · ${conversation.answeredCount} of 26 answered`}
        </div>
      </div>
      <div className="flex flex-col gap-1.5 w-47.5 flex-shrink-0">
        <div className="w-full h-1.5 rounded-pill bg-bg-subtlest overflow-hidden">
          <div className="h-full bg-text-primary" style={{ width: `${percent}%` }} />
        </div>
        <span className="text-[13px] font-semibold">{percent}% complete</span>
      </div>
      <div className="flex items-center gap-1.5 flex-shrink-0">
        <button
          type="button"
          onClick={() => navigate(`/conversations/${conversation.id}`)}
          className="bg-white text-text-primary border border-text-primary rounded-btn h-10 px-5 text-sm font-medium cursor-pointer whitespace-nowrap"
        >
          Open
        </button>

        {isOwner && (
        <div className="relative">
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="More actions"
            className="w-10 h-10 rounded-full flex items-center justify-center text-text-secondary hover:bg-bg-subtle cursor-pointer border-none bg-transparent"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="5" r="1.6" />
              <circle cx="12" cy="12" r="1.6" />
              <circle cx="12" cy="19" r="1.6" />
            </svg>
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
              <div className="absolute top-11 right-0 bg-white border border-border rounded-btn shadow-dropdown z-20 overflow-hidden w-40">
                {onShare && (
                  <button
                    type="button"
                    onClick={() => {
                      setMenuOpen(false)
                      onShare()
                    }}
                    className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-text-primary cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="18" cy="5" r="3" />
                      <circle cx="6" cy="12" r="3" />
                      <circle cx="18" cy="19" r="3" />
                      <path d="M8.6 10.5l6.8-3.9M8.6 13.5l6.8 3.9" />
                    </svg>
                    Share
                  </button>
                )}
                {onAssignGroup && (
                  <button
                    type="button"
                    onClick={() => {
                      setMenuOpen(false)
                      onAssignGroup()
                    }}
                    className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-text-primary cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                    </svg>
                    Assign to group
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false)
                    setRenameOpen(true)
                  }}
                  className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-text-primary cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
                  </svg>
                  Rename
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMenuOpen(false)
                    setDeleteOpen(true)
                  }}
                  className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-confidence-low cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M3 6h18" />
                    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                  </svg>
                  Delete
                </button>
              </div>
            </>
          )}
        </div>
        )}
      </div>

      <RenameModal
        open={renameOpen}
        onClose={() => setRenameOpen(false)}
        onSave={(title) => onRename(conversation.id, title)}
        initialValue={conversation.title}
        title="Rename BRD"
        label="Title"
        errorMessage="Title is required — give this BRD a name."
      />
      <ConfirmModal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={() => {
          setDeleteOpen(false)
          onDelete(conversation.id)
        }}
        title="Delete this BRD?"
        description={`"${conversation.title}" and all of its answers will be permanently deleted. This can't be undone.`}
        confirmLabel="Delete"
      />
    </div>
  )
}
