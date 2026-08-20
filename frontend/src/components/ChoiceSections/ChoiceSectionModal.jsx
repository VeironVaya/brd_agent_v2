import { useEffect, useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'
import { CHOICE_SECTIONS } from '../../utils/choiceSections.js'

function initialData(config, existing) {
  return Object.fromEntries(Object.entries(config.groups).map(([groupId]) => {
    const saved = existing?.[groupId]
    return [groupId, {
      selected: saved?.selected || [],
      other_text: saved?.other_text || '',
    }]
  }))
}

function needsOther(option) {
  return option.toLowerCase().includes('specify') || option === 'Others'
}

const EMPTY_GROUP = { selected: [], other_text: '' }

export default function ChoiceSectionModal({ open, sectionId, answer, onClose, onDiscuss, onSave }) {
  const config = sectionId ? CHOICE_SECTIONS[sectionId] : null
  const [data, setData] = useState({})
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (open && config) {
      setData(initialData(config, answer?.choiceData))
      setError('')
    }
  }, [open, sectionId, answer, config])

  if (!open || !config) return null

  function toggleOption(groupId, option) {
    setData((current) => {
      const group = current[groupId]
      const selected = group.selected.includes(option)
        ? group.selected.filter((item) => item !== option)
        : config.groups[groupId].multiple ? [...group.selected, option] : [option]
      return { ...current, [groupId]: { ...group, selected } }
    })
    setError('')
  }

  function validate() {
    for (const [groupId, groupConfig] of Object.entries(config.groups)) {
      const group = data[groupId] || EMPTY_GROUP
      if (!group.selected.length) return `${groupConfig.label} requires at least one selection.`
      if (group.selected.some(needsOther) && !group.other_text.trim()) {
        return `Please complete the Other description for ${groupConfig.label}.`
      }
    }
    return ''
  }

  async function handleSave() {
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }
    setSaving(true)
    try {
      await onSave(data)
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal open={open} onClose={onClose} maxWidth={680} zIndex={20}>
      <ModalHeader title={`${sectionId} ${config.title}`} onClose={onClose} />
      <div className="text-sm text-text-secondary mt-1.5">
        Choose the applicable values, or discuss this section first if you need help deciding.
      </div>

      <div className="flex flex-col gap-5 mt-6">
        {Object.entries(config.groups).map(([groupId, groupConfig]) => {
          const group = data[groupId] || EMPTY_GROUP
          const showOther = group.selected.some(needsOther)
          return (
            <fieldset key={groupId} className="border-0 p-0 m-0">
              <legend className="text-sm font-semibold mb-2">{groupConfig.label}</legend>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {groupConfig.options.map((option) => (
                  <label key={option} className="flex items-start gap-2 text-sm text-text-secondary cursor-pointer">
                    <input
                      type={groupConfig.multiple ? 'checkbox' : 'radio'}
                      name={`${sectionId}-${groupId}`}
                      checked={group.selected.includes(option)}
                      onChange={() => toggleOption(groupId, option)}
                      className="mt-0.5"
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
              {showOther && (
                <textarea
                  rows={2}
                  value={group.other_text}
                  onChange={(event) => setData((current) => ({
                    ...current,
                    [groupId]: { ...current[groupId], other_text: event.target.value },
                  }))}
                  placeholder="Please specify"
                  className="w-full mt-3 bg-white font-[inherit] rounded-btn px-3 py-2 text-sm text-text-primary outline-none border border-border focus:border-text-primary resize-none"
                />
              )}
            </fieldset>
          )
        })}
      </div>

      {error && <div className="text-[12.5px] text-confidence-low mt-4">{error}</div>}

      <div className="flex justify-between gap-2.5 mt-6">
        <Button variant="ghost" size="sm" onClick={onDiscuss}>Discuss first</Button>
        <div className="flex gap-2.5">
          <Button variant="secondary" size="sm" onClick={onClose}>Cancel</Button>
          <Button variant="primary" size="sm" onClick={handleSave} disabled={saving}>Choose options</Button>
        </div>
      </div>
    </Modal>
  )
}
