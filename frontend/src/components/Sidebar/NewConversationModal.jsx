import { useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import { TextField, TextAreaField } from '../common/FormField.jsx'
import { DIRECTORATE_OPTIONS } from '../../utils/choiceSections.js'

export default function NewConversationModal({ open, onClose, onCreate, groupName }) {
  const [title, setTitle] = useState('')
  const [context, setContext] = useState('')
  const [requestorDirectorate, setRequestorDirectorate] = useState('')
  const [impactedStakeholders, setImpactedStakeholders] = useState([])
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function handleClose() {
    setTitle('')
    setContext('')
    setRequestorDirectorate('')
    setImpactedStakeholders([])
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
      await onCreate({ title, context, requestorDirectorate, impactedStakeholders })
      handleClose()
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalHeader title="New BRD" onClose={handleClose} />
      <div className="text-sm text-text-secondary mt-1.5">
        Give it a name and short context — BRD-Agent will ask the rest.
        {groupName && (
          <div className="mt-1 flex items-center gap-1.5 text-accent font-medium">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            </svg>
            Will be created in {groupName}
          </div>
        )}
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
        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-semibold">Requestor Directorate</label>
          <select
            value={requestorDirectorate}
            onChange={(e) => setRequestorDirectorate(e.target.value)}
            className="h-12 bg-white rounded-btn px-4 text-[15px] border border-border outline-none focus:border-text-primary"
          >
            <option value="">Select a directorate</option>
            {DIRECTORATE_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
          </select>
        </div>
        <fieldset className="flex flex-col gap-2 border-0 p-0 m-0">
          <legend className="text-[13px] font-semibold mb-1">Impacted Stakeholder</legend>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {DIRECTORATE_OPTIONS.map((option) => (
              <label key={option} className="flex items-start gap-2 text-[13px] text-text-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={impactedStakeholders.includes(option)}
                  onChange={() => setImpactedStakeholders((current) => current.includes(option)
                    ? current.filter((item) => item !== option)
                    : [...current, option])}
                  className="mt-0.5"
                />
                {option}
              </label>
            ))}
          </div>
        </fieldset>
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
