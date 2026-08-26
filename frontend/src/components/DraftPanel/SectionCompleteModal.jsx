import Modal from '../common/Modal.jsx'
import Button from '../common/Button.jsx'

/**
 * Blocking modal that fires when the AI marks the currently focused section
 * as complete. Gives the user a choice: jump to the next available section
 * or stay in the current chat thread.
 *
 * Props:
 *   open           – boolean
 *   completedTitle – display name of the section that just finished
 *   nextTitle      – display name of the next section (or null if none left)
 *   onProceed      – () => void  – navigate to next section + close
 *   onStay         – () => void  – stay in current section + close
 */
export default function SectionCompleteModal({
  open,
  completedTitle,
  nextTitle,
  onProceed,
  onStay,
}) {
  return (
    <Modal open={open} onClose={onStay} maxWidth={440} zIndex={40}>
      {/* Icon + heading */}
      <div className="flex flex-col items-center text-center gap-4 pb-1">
        {/* Checkmark circle */}
        <div className="w-14 h-14 rounded-full bg-[#f0faf4] flex items-center justify-center flex-shrink-0">
          <svg
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#22c55e"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>

        <div className="flex flex-col gap-1.5">
          <span className="text-[17px] font-bold text-text-primary leading-snug">
            Section complete!
          </span>
          <p className="text-[13.5px] text-text-secondary leading-relaxed">
            <span className="font-semibold text-text-primary">
              &ldquo;{completedTitle}&rdquo;
            </span>{' '}
            has been marked as answered by the AI.
          </p>
        </div>
      </div>

      {/* Next section hint */}
      {nextTitle && (
        <div className="mt-4 rounded-lg bg-bg-subtle border border-border-light px-4 py-3 text-[13px] text-text-secondary leading-relaxed">
          <span className="font-semibold text-text-primary">Up next: </span>
          {nextTitle}
        </div>
      )}

      {!nextTitle && (
        <div className="mt-4 rounded-lg bg-bg-subtle border border-border-light px-4 py-3 text-[13px] text-text-secondary leading-relaxed text-center">
          🎉 All available sections are answered — great work!
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-2.5 mt-5.5">
        {nextTitle && (
          <Button variant="primary" size="sm" className="w-full" onClick={onProceed}>
            Proceed to next section →
          </Button>
        )}
        <Button variant="secondary" size="sm" className="w-full" onClick={onStay}>
          Stay in this chat
        </Button>
      </div>
    </Modal>
  )
}
