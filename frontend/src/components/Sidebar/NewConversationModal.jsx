import { useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import { TextField, TextAreaField } from '../common/FormField.jsx'

export default function NewConversationModal({ open, onClose, onCreate }) {
  const [title, setTitle] = useState('')
  const [context, setContext] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleClose() {
    setTitle('')
    setContext('')
    setError('')
    onClose()
  }

  async function handleCreate() {
    if (!title.trim()) {
      setError('Title is required — give this BRD a name.')
      return
    }
    setSubmitting(true)
    try {
      await onCreate({ title, context })
      handleClose()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalHeader title="New Conversation" onClose={handleClose} />
      <div className="text-sm text-text-secondary mt-1.5">
        Give it a name and short context — BRD-Agent will ask the rest.
      </div>

      <div className="flex flex-col gap-4 mt-5.5">
        <TextField
          label="Title"
          placeholder="e.g. Vendor Onboarding Platform"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value)
            setError('')
          }}
          error={error}
        />
        <TextAreaField
          label="Context"
          hint="(optional)"
          placeholder="A sentence or two on what this BRD is for."
          value={context}
          onChange={(e) => setContext(e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-2.5 mt-6.5">
        <Button variant="secondary" size="sm" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" size="sm" onClick={handleCreate} disabled={submitting}>
          Create
        </Button>
      </div>
    </Modal>
  )
}
