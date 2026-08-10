import { useEffect, useState } from 'react'
import Modal, { ModalHeader } from './Modal.jsx'
import Button from './Button.jsx'
import { TextField } from './FormField.jsx'

export default function RenameModal({
  open,
  onClose,
  onSave,
  initialValue = '',
  title = 'Rename',
  label = 'Title',
  errorMessage = 'Title is required.',
}) {
  const [value, setValue] = useState(initialValue)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (open) {
      setValue(initialValue)
      setError('')
    }
  }, [open, initialValue])

  function handleClose() {
    setError('')
    onClose()
  }

  async function handleSave() {
    if (!value.trim()) {
      setError(errorMessage)
      return
    }
    setSubmitting(true)
    try {
      await onSave(value.trim())
      handleClose()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={handleClose} maxWidth={420}>
      <ModalHeader title={title} onClose={handleClose} size="sm" />
      <div className="mt-4">
        <TextField
          label={label}
          value={value}
          onChange={(e) => {
            setValue(e.target.value)
            setError('')
          }}
          onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          error={error}
          autoFocus
        />
      </div>
      <div className="flex justify-end gap-2.5 mt-5.5">
        <Button variant="secondary" size="sm" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" size="sm" onClick={handleSave} disabled={submitting}>
          Save
        </Button>
      </div>
    </Modal>
  )
}
