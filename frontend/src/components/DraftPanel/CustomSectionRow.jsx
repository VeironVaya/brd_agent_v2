import { useState } from 'react'
import RenameModal from '../common/RenameModal.jsx'
import ConfirmModal from '../common/ConfirmModal.jsx'
import DonutBadge from './DonutBadge.jsx'
import { CONFIDENCE_COLOR_HEX } from '../../utils/confidenceColors.js'
import { fieldState, confidenceTier } from '../../utils/draftFields.js'

const TIER_LABEL = { HIGH: 'HIGH', MEDIUM: 'MEDIUM', LOW: 'LOW' }

function IconButton({ onClick, label, hoverClass, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={`bg-transparent border-none cursor-pointer p-0.5 text-[#c1c1c1] ${hoverClass} flex-shrink-0`}
    >
      {children}
    </button>
  )
}

function EditIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4Z" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
      <path d="M3 6h18" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
    </svg>
  )
}

function ReadyIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ff385c" strokeWidth="1.8" className="flex-shrink-0">
      <circle cx="12" cy="12" r="9" />
    </svg>
  )
}

/** Recursively renders one custom section node and its children, at any depth. */
export default function CustomSectionRow({ node, code, onRename, onRemove, answers, focusedFieldId, onFocus, onViewAnswer, indent = false }) {
  const [renameOpen, setRenameOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  const renameModal = (
    <RenameModal
      open={renameOpen}
      onClose={() => setRenameOpen(false)}
      onSave={(title) => onRename(node.id, title)}
      initialValue={node.title}
      title="Rename Section"
      label="Title"
      errorMessage="Title is required."
    />
  )

  if (node.hasChildren) {
    return (
      <div className={indent ? 'border-l-2 border-border-light ml-2 pl-3.5' : ''}>
        <div className="flex items-center justify-between gap-1.5 mt-2.5 py-1.5 pl-1">
          <div className="flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ff385c" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
              <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            </svg>
            <span className="text-xs font-bold text-[#3f3f3f] uppercase tracking-wide">
              {code} {node.title}
            </span>
          </div>
          <div className="flex items-center gap-1">
            <IconButton label="Rename section" hoverClass="hover:text-text-primary" onClick={() => setRenameOpen(true)}>
              <EditIcon />
            </IconButton>
            <IconButton label="Remove section" hoverClass="hover:text-confidence-low" onClick={() => setDeleteOpen(true)}>
              <TrashIcon />
            </IconButton>
          </div>
        </div>
        {node.children.map((child, i) => (
          <CustomSectionRow
            key={child.id}
            node={child}
            code={`${code}.${i + 1}`}
            onRename={onRename}
            onRemove={onRemove}
            answers={answers}
            focusedFieldId={focusedFieldId}
            onFocus={onFocus}
            onViewAnswer={onViewAnswer}
            indent
          />
        ))}
        {renameModal}
        <ConfirmModal
          open={deleteOpen}
          onClose={() => setDeleteOpen(false)}
          onConfirm={() => {
            setDeleteOpen(false)
            onRemove(node.id)
          }}
          title="Delete this section?"
          description={
            node.children.length > 0
              ? `"${node.title}" and its ${node.children.length} sub-section${node.children.length === 1 ? '' : 's'} will be permanently deleted.`
              : `"${node.title}" will be permanently deleted.`
          }
          confirmLabel="Delete"
        />
      </div>
    )
  }

  // Leaf: same Room/answer/focus behavior as a template SectionRow, plus
  // its own rename/delete controls.
  const status = fieldState(node.id, answers)
  const answer = answers[node.id] || {}
  const hasMetrics = answer.completeness != null && answer.confidence != null
  const tier = hasMetrics ? confidenceTier(answer.confidence) : null
  const isFocused = node.id === focusedFieldId
  const hasAnswer = !!answer.answer
  const missingItems = answer.missing || []

  return (
    <div className={indent ? 'border-l-2 border-border-light ml-2 pl-3.5' : ''}>
      <div
        onClick={() => onFocus(node.id)}
        className={`flex items-center gap-2.5 rounded-md cursor-pointer ${
          isFocused ? '-mx-2 px-2 py-2.25 bg-bg-subtler border-l-3 border-text-primary' : 'py-2.25 border-l-3 border-transparent'
        }`}
      >
        {hasMetrics ? (
          <DonutBadge
            completeness={answer.completeness}
            confidence={answer.confidence}
            tier={tier}
            flagged={status === 'review'}
          />
        ) : (
          <ReadyIcon />
        )}

        <div className="flex-1 min-w-0 flex items-baseline gap-2">
          <span className={`text-sm ${status === 'progress' ? 'font-semibold' : 'font-normal'}`}>
            {code} {node.title}
          </span>
          {hasMetrics ? (
            <span className="ml-auto flex items-baseline gap-2 flex-shrink-0">
              <span className="text-[10.5px] font-semibold text-text-tertiary">
                {answer.completeness}% complete
              </span>
              <span
                className="text-[10.5px] font-bold uppercase tracking-wide"
                style={{ color: CONFIDENCE_COLOR_HEX[tier] }}
              >
                {answer.confidence}% {TIER_LABEL[tier]}
              </span>
            </span>
          ) : (
            <span className="ml-auto text-[11px] text-text-tertiary flex-shrink-0">Custom · no fixed checklist</span>
          )}
        </div>

        <div className="flex items-center gap-1 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
          <IconButton label="Rename section" hoverClass="hover:text-text-primary" onClick={() => setRenameOpen(true)}>
            <EditIcon />
          </IconButton>
          <IconButton label="Remove section" hoverClass="hover:text-confidence-low" onClick={() => setDeleteOpen(true)}>
            <TrashIcon />
          </IconButton>
        </div>
      </div>

      {isFocused && (
        <div className="my-0.5 mb-1.5 px-3 py-2.5 bg-bg-subtle rounded-md">
          {hasAnswer && (
            <div className="mb-3 pb-3 border-b border-border-light">
              <div className="flex items-center justify-between mb-1.25">
                <span className="text-[11px] font-bold uppercase tracking-wider text-text-primary/80">Result</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onViewAnswer(node.id)
                  }}
                  className="bg-transparent border-none text-text-primary text-[11px] font-semibold cursor-pointer underline whitespace-nowrap"
                >
                  See details
                </button>
              </div>
              <div className="text-[13px] leading-relaxed">{answer.answer}</div>
            </div>
          )}
          <div className="text-[11px] font-bold uppercase tracking-wider mb-1.25">What's missing?</div>
          {missingItems.length > 0 ? (
            <ul className="m-0 pl-4 flex flex-col gap-0.75">
              {missingItems.map((m) => (
                <li key={m} className="text-[13px] leading-snug">
                  {m}
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-[13px] text-text-tertiary">Nothing outstanding — this answer is complete.</div>
          )}
        </div>
      )}

      {renameModal}
      <ConfirmModal
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        onConfirm={() => {
          setDeleteOpen(false)
          onRemove(node.id)
        }}
        title="Delete this section?"
        description={`"${node.title}" will be permanently deleted.`}
        confirmLabel="Delete"
      />
    </div>
  )
}
