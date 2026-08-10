import { useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import { TextField, TextAreaField } from '../common/FormField.jsx'
import { getContainerOptions } from '../../utils/customSectionTree.js'

const initialState = {
  title: '',
  purpose: '',
  hasChildren: false,
  children: [],
  childDraft: '',
  target: null, // null = standalone; otherwise { id, kind, label }
}

export default function AddCustomSectionModal({ open, onClose, onCreate, customSections }) {
  const [form, setForm] = useState(initialState)
  const [titleError, setTitleError] = useState('')
  const [nestOpen, setNestOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const options = getContainerOptions(customSections)

  function set(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
    if (field === 'title') setTitleError('')
  }

  function handleClose() {
    setForm(initialState)
    setTitleError('')
    setNestOpen(false)
    onClose()
  }

  function addChildDraft() {
    const t = form.childDraft.trim()
    if (!t) return
    setForm((f) => ({ ...f, children: [...f.children, t], childDraft: '' }))
  }

  function removeChildDraft(idx) {
    setForm((f) => ({ ...f, children: f.children.filter((_, i) => i !== idx) }))
  }

  async function handleSubmit() {
    if (!form.title.trim()) {
      setTitleError('Section title is required.')
      return
    }
    setSubmitting(true)
    try {
      const created = await onCreate(form.target, {
        title: form.title,
        hasChildren: form.hasChildren,
        purpose: form.purpose.trim() || null,
      })
      // Quick sub-sections typed during creation become real children of
      // the node we just created, one API call each (the mock only
      // supports adding one node at a time).
      for (const childTitle of form.children) {
        await onCreate({ id: created.id, kind: 'custom' }, { title: childTitle, hasChildren: false })
      }
      handleClose()
    } finally {
      setSubmitting(false)
    }
  }

  const nestLabel = form.target ? form.target.label : 'None — standalone top-level section'

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalHeader title="Add Custom Section" onClose={handleClose} />
      <div className="text-sm text-text-secondary mt-1.5">
        For content this document needs that isn't part of the standard checklist. No fixed
        questions — tell BRD-Agent what to capture and it'll ask you in chat.
      </div>

      <div className="flex flex-col gap-4 mt-5.5">
        <TextField
          label="Section title"
          placeholder="e.g. Vendor Escalation Path"
          value={form.title}
          onChange={(e) => set('title', e.target.value)}
          error={titleError}
        />

        <div className="flex flex-col gap-1.5 relative">
          <label className="text-[13px] font-semibold">Nest under</label>
          <div
            onClick={() => setNestOpen((v) => !v)}
            className="h-12 bg-white border border-border rounded-btn px-4 text-[15px] flex items-center justify-between cursor-pointer"
          >
            <span>{nestLabel}</span>
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#6a6a6a"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ transform: nestOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform .15s' }}
            >
              <path d="m6 9 6 6 6-6" />
            </svg>
          </div>
          {nestOpen && (
            <div className="absolute top-19 left-0 right-0 max-h-70 overflow-y-auto bg-white border border-border rounded-btn shadow-dropdown z-10">
              {options.map((opt) =>
                opt.kind === 'divider' ? (
                  <div
                    key={opt.id}
                    className="px-4 py-2 text-[11px] font-semibold uppercase tracking-wide text-text-tertiary bg-bg-subtle"
                  >
                    {opt.label}
                  </div>
                ) : (
                  <div
                    key={opt.id ?? 'standalone'}
                    onClick={() => {
                      set('target', opt.id === null ? null : opt)
                      setNestOpen(false)
                    }}
                    style={{ paddingLeft: `${16 + opt.depth * 16}px` }}
                    className={`py-2.5 pr-4 text-sm cursor-pointer ${
                      (form.target?.id ?? null) === opt.id ? 'bg-bg-subtler font-semibold' : 'bg-white font-normal'
                    }`}
                  >
                    {opt.label}
                  </div>
                ),
              )}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-1.5">
          <label className="text-[13px] font-semibold">Structure</label>
          <div className="flex items-center bg-bg-subtlest rounded-pill p-1 gap-0.5 w-fit">
            <span
              onClick={() => set('hasChildren', false)}
              className={`px-4 py-1.75 rounded-pill text-[13px] cursor-pointer ${
                !form.hasChildren ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary'
              }`}
            >
              Single item
            </span>
            <span
              onClick={() => set('hasChildren', true)}
              className={`px-4 py-1.75 rounded-pill text-[13px] cursor-pointer ${
                form.hasChildren ? 'font-semibold text-white bg-text-primary' : 'font-medium text-text-secondary'
              }`}
            >
              Has sub-sections
            </span>
          </div>
          <div className="text-xs text-text-tertiary">
            {form.hasChildren
              ? 'Shown as a group header. Reopen "+ Add custom section" afterwards and nest under it to go deeper, however many levels you need.'
              : 'Shown as a single row, like a regular checklist item.'}
          </div>
        </div>

        {form.hasChildren && (
          <div className="flex flex-col gap-2">
            <label className="text-[13px] font-semibold">Sub-sections (optional, added right under this one)</label>
            {form.children.map((child, i) => (
              <div key={i} className="flex items-center gap-2">
                <span className="flex-1 text-sm bg-bg-subtle border border-border-light rounded-btn px-3 py-2">
                  {child}
                </span>
                <button
                  type="button"
                  onClick={() => removeChildDraft(i)}
                  aria-label="Remove"
                  className="bg-transparent border-none cursor-pointer p-0.5 text-[#c1c1c1] hover:text-confidence-low flex-shrink-0"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M3 6h18" />
                    <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                  </svg>
                </button>
              </div>
            ))}
            <div className="flex gap-2">
              <input
                placeholder="Sub-section title"
                value={form.childDraft}
                onChange={(e) => set('childDraft', e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addChildDraft()}
                className="flex-1 h-11 bg-white border border-border rounded-btn px-3.5 text-sm outline-none"
              />
              <Button variant="secondary" size="sm" onClick={addChildDraft}>
                + Add
              </Button>
            </div>
          </div>
        )}

        <TextAreaField
          label="What should this section cover?"
          placeholder="A sentence or two on what to capture here — BRD-Agent uses this to guide its questions."
          value={form.purpose}
          onChange={(e) => set('purpose', e.target.value)}
        />
      </div>

      <div className="flex justify-end gap-2.5 mt-6.5">
        <Button variant="secondary" size="sm" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" size="sm" onClick={handleSubmit} disabled={submitting}>
          Add Section
        </Button>
      </div>
    </Modal>
  )
}
