import { useState } from 'react'
import Modal, { ModalHeader } from '../common/Modal.jsx'

export default function ReviewFlaggedModal({ open, onClose, flaggedItems, answers, onResolveInChat }) {

  return (
    <Modal open={open} onClose={onClose} maxWidth={640}>
      <ModalHeader title="Review Flagged Answers" onClose={onClose} />
      <div className="text-sm text-text-secondary mt-1.5 mb-5">
        Items flagged because an answer they depend on changed since they were last completed.
      </div>

      <div className="flex flex-col gap-3.5">
        {flaggedItems.map((f) => {
          const missing = answers[f.fieldId]?.missing || []
          return (
            <div key={f.fieldId} className="border border-border-light rounded-xl px-4.5 py-4">
              <div className="flex items-center gap-2">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#c13515" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
                  <path d="M4 22V4" />
                  <path d="M4 4h13l-2.5 4L17 12H4" />
                </svg>
                <span className="text-sm font-semibold">{f.label}</span>
              </div>
              <div className="text-[11px] text-text-tertiary mt-1 ml-5.75">
                Depends on {f.dependsOnLabel} — changed
              </div>
              <div className="text-[13px] text-text-secondary mt-2 leading-relaxed">{f.reason}</div>



              <div className="flex gap-2.5 mt-3.5">
                <button
                  type="button"
                  onClick={() => onResolveInChat(f.fieldId)}
                  className="bg-accent text-white border-none rounded-btn h-9.5 px-4 text-[13px] font-semibold cursor-pointer"
                >
                  Resolve in chat
                </button>
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex justify-end mt-5.5">
        <button
          type="button"
          onClick={onClose}
          className="bg-text-primary text-white border-none rounded-btn h-11 px-5.5 text-sm font-semibold cursor-pointer"
        >
          Done
        </button>
      </div>
    </Modal>
  )
}
