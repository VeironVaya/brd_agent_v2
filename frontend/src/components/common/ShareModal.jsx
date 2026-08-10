import { useEffect, useState } from 'react'
import Modal, { ModalHeader } from './Modal.jsx'
import Button from './Button.jsx'
import ConfirmModal from './ConfirmModal.jsx'
import { TextField } from './FormField.jsx'
import * as api from '../../services/api.js'

const ERROR_MESSAGES = {
  not_found: 'No account with that email exists.',
  cannot_share_with_self: 'You already own this conversation.',
  already_shared: 'This person already has access — change their role below instead.',
}

function RolePillToggle({ value, onChange, size = 'sm' }) {
  const pad = size === 'sm' ? 'px-3 py-1' : 'px-4 py-1.75'
  return (
    <div className="inline-flex bg-bg-subtlest rounded-pill p-1 gap-0.5 flex-shrink-0">
      {['editor', 'viewer'].map((role) => (
        <button
          key={role}
          type="button"
          onClick={() => onChange(role)}
          className={`${pad} rounded-pill text-[13px] cursor-pointer border-none transition-colors ${
            value === role ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary bg-transparent'
          }`}
        >
          {role === 'editor' ? 'Editor' : 'Viewer'}
        </button>
      ))}
    </div>
  )
}

function initials(name) {
  return (name || '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('')
}

export default function ShareModal({ open, onClose, conversationId }) {
  const [collaborators, setCollaborators] = useState([])
  const [loading, setLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('editor')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [removeTarget, setRemoveTarget] = useState(null)

  useEffect(() => {
    if (!open || !conversationId) return
    let active = true
    setLoading(true)
    api
      .listCollaborators(conversationId)
      .then((list) => {
        if (active) setCollaborators(list)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [open, conversationId])

  function handleClose() {
    setEmail('')
    setRole('editor')
    setError('')
    onClose()
  }

  async function handleAdd() {
    if (!email.trim()) {
      setError('Enter an email address to share with.')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const collaborator = await api.shareConversation(conversationId, { email: email.trim(), role })
      setCollaborators((list) => [...list, collaborator])
      setEmail('')
      setRole('editor')
    } catch (err) {
      setError(ERROR_MESSAGES[err.code] || err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleRoleChange(collaborator, newRole) {
    const updated = await api.updateCollaboratorRole(conversationId, collaborator.id, newRole)
    setCollaborators((list) => list.map((c) => (c.id === collaborator.id ? updated : c)))
  }

  async function handleRemove(collaborator) {
    await api.removeCollaborator(conversationId, collaborator.id)
    setCollaborators((list) => list.filter((c) => c.id !== collaborator.id))
    setRemoveTarget(null)
  }

  return (
    <Modal open={open} onClose={handleClose} maxWidth={520}>
      <ModalHeader title="Share conversation" onClose={handleClose} />
      <div className="text-sm text-text-secondary mt-1.5">
        Invite a registered user by email. Editors can chat and edit sections; viewers can only view and export.
      </div>

      <div className="flex items-end gap-2.5 mt-5.5">
        <TextField
          className="flex-1"
          label="Email"
          type="email"
          placeholder="teammate@company.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value)
            setError('')
          }}
          error={error}
        />
        <div className="flex flex-col gap-1.5">
          <span className="text-[13px] font-semibold opacity-0 select-none">Role</span>
          <RolePillToggle value={role} onChange={setRole} />
        </div>
        <Button variant="primary" size="md" onClick={handleAdd} disabled={submitting}>
          Add
        </Button>
      </div>

      <div className="flex flex-col gap-2 mt-6.5 max-h-64 overflow-y-auto">
        {loading ? (
          <div className="text-sm text-text-tertiary py-3">Loading…</div>
        ) : collaborators.length === 0 ? (
          <div className="text-sm text-text-tertiary py-3">Not shared with anyone yet.</div>
        ) : (
          collaborators.map((collaborator) => (
            <div
              key={collaborator.id}
              className="flex items-center justify-between gap-3 border border-border-light rounded-btn px-3.5 py-2.5"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-full bg-text-primary text-white flex items-center justify-center text-[12px] font-semibold flex-shrink-0">
                  {initials(collaborator.name)}
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-semibold truncate">{collaborator.name}</div>
                  <div className="text-[12.5px] text-text-tertiary truncate">{collaborator.email}</div>
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <RolePillToggle value={collaborator.role} onChange={(newRole) => handleRoleChange(collaborator, newRole)} />
                <button
                  type="button"
                  onClick={() => setRemoveTarget(collaborator)}
                  aria-label={`Remove ${collaborator.name}`}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-text-secondary hover:bg-bg-subtle cursor-pointer border-none bg-transparent"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <path d="M18 6 6 18" />
                    <path d="m6 6 12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex justify-end mt-6.5">
        <Button variant="secondary" size="sm" onClick={handleClose}>
          Done
        </Button>
      </div>

      <ConfirmModal
        open={!!removeTarget}
        onClose={() => setRemoveTarget(null)}
        onConfirm={() => handleRemove(removeTarget)}
        title="Remove access?"
        description={removeTarget ? `${removeTarget.name} will no longer be able to view or edit this BRD.` : ''}
        confirmLabel="Remove"
      />
    </Modal>
  )
}
