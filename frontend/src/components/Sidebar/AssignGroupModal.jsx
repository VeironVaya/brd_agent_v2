import Modal, { ModalHeader } from '../common/Modal.jsx'
import Button from '../common/Button.jsx'

/**
 * Modal that lets the user assign the current BRD to one of their groups,
 * or remove it from any group (Ungrouped).
 *
 * Props:
 *   open            – boolean
 *   groups          – array of { id, title, description }
 *   currentGroupId  – string | null
 *   onClose         – () => void
 *   onAssign        – (groupId: string | null) => Promise<void>
 */
export default function AssignGroupModal({ open, groups, currentGroupId, onClose, onAssign }) {
  async function handlePick(groupId) {
    await onAssign(groupId === currentGroupId ? currentGroupId : groupId)
    onClose()
  }

  return (
    <Modal open={open} onClose={onClose} maxWidth={400}>
      <ModalHeader title="Assign to Group" onClose={onClose} size="sm" />
      <div className="text-[13.5px] text-text-secondary mt-1.5 leading-relaxed">
        Choose a group for this BRD, or remove it from its current group.
      </div>

      <div className="flex flex-col gap-1.5 mt-4">
        {/* Ungrouped option */}
        <button
          type="button"
          onClick={() => handlePick(null)}
          className={`flex items-center gap-3 w-full text-left px-4 py-3 rounded-btn border transition-colors cursor-pointer ${
            currentGroupId === null
              ? 'border-text-primary bg-bg-subtle font-semibold'
              : 'border-border-light bg-white hover:bg-bg-subtle'
          }`}
        >
          <span className="w-7 h-7 rounded-full bg-bg-subtlest flex items-center justify-center flex-shrink-0">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#929292" strokeWidth="1.8" strokeLinecap="round">
              <path d="M5 8h14M5 12h9M5 16h5" />
            </svg>
          </span>
          <div className="min-w-0">
            <div className="text-[13.5px] font-medium truncate">Ungrouped</div>
            <div className="text-xs text-text-tertiary">Remove from any group</div>
          </div>
          {currentGroupId === null && (
            <svg className="ml-auto flex-shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          )}
        </button>

        {/* Group options */}
        {groups.map((group) => (
          <button
            key={group.id}
            type="button"
            onClick={() => handlePick(group.id)}
            className={`flex items-center gap-3 w-full text-left px-4 py-3 rounded-btn border transition-colors cursor-pointer ${
              currentGroupId === group.id
                ? 'border-text-primary bg-bg-subtle font-semibold'
                : 'border-border-light bg-white hover:bg-bg-subtle'
            }`}
          >
            <span className="w-7 h-7 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              </svg>
            </span>
            <div className="min-w-0">
              <div className="text-[13.5px] font-medium truncate">{group.title}</div>
              {group.description && (
                <div className="text-xs text-text-tertiary truncate">{group.description}</div>
              )}
            </div>
            {currentGroupId === group.id && (
              <svg className="ml-auto flex-shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                <path d="M20 6 9 17l-5-5" />
              </svg>
            )}
          </button>
        ))}

        {groups.length === 0 && (
          <div className="text-center text-[13px] text-text-tertiary py-4">
            No groups yet — create one first.
          </div>
        )}
      </div>

      <div className="flex justify-end mt-5">
        <Button variant="secondary" size="sm" onClick={onClose}>
          Cancel
        </Button>
      </div>
    </Modal>
  )
}
