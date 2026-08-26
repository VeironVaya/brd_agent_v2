import { useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import { TextField, TextAreaField } from '../common/FormField.jsx'

/**
 * Modal for creating or editing a BRD group.
 *
 * Props:
 *   open           – boolean
 *   initialTitle   – string (empty for new, pre-filled for edit)
 *   initialDesc    – string | null
 *   onClose        – () => void
 *   onSave         – ({ title, description }) => Promise<void>
 *   mode           – 'create' | 'edit'
 */
export default function GroupModal({ open, initialTitle = '', initialDesc = '', onClose, onSave, mode = 'create' }) {
  const [title, setTitle] = useState(initialTitle)
  const [description, setDescription] = useState(initialDesc || '')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleClose() {
    setTitle(initialTitle)
    setDescription(initialDesc || '')
    setError('')
    onClose()
  }

  async function handleSave() {
    if (!title.trim()) {
      setError('Group title is required.')
      return
    }
    setSubmitting(true)
    try {
      await onSave({ title: title.trim(), description: description.trim() || null })
      handleClose()
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setSubmitting(false)
    }
  }

  // Sync state when modal reopens with new initial values (e.g. edit different group)
  if (!open) return null

  return (
    <Modal open={open} onClose={handleClose} maxWidth={440}>
      <ModalHeader
        title={mode === 'edit' ? 'Edit Group' : 'New Group'}
        onClose={handleClose}
      />
      <div className="text-sm text-text-secondary mt-1.5">
        {mode === 'edit'
          ? 'Update the group name or description.'
          : 'Create a group to organise your BRDs.'}
      </div>

      <div className="flex flex-col gap-4 mt-5.5">
        <TextField
          label="Group Title"
          placeholder="e.g. Q3 Initiatives"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value)
            setError('')
          }}
          error={error}
        />
        <TextAreaField
          label="Description"
          hint="(optional)"
          placeholder="A short description of what this group contains."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-2.5 mt-6.5">
        <Button variant="secondary" size="sm" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" size="sm" onClick={handleSave} disabled={submitting}>
          {mode === 'edit' ? 'Save changes' : 'Create group'}
        </Button>
      </div>
    </Modal>
  )
}
