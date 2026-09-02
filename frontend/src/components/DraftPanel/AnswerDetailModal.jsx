import Modal, { ModalHeader } from '../common/Modal.jsx'
import { CONFIDENCE_COLOR_HEX } from '../../utils/confidenceColors.js'
import { FIELD_META, confidenceTier } from '../../utils/draftFields.js'
import { findCustomNode, getCodeForNode } from '../../utils/customSectionTree.js'
import ConfidenceBreakdown from './ConfidenceBreakdown.jsx'

export default function AnswerDetailModal({ open, onClose, fieldId, answers, customSections = [] }) {
  const templateLeaf = fieldId ? FIELD_META[fieldId] : null
  const customNode = !templateLeaf && fieldId ? findCustomNode(customSections, fieldId) : null
  const leaf = templateLeaf || (customNode ? { id: customNode.id, title: customNode.title } : null)
  const code = templateLeaf ? templateLeaf.id : customNode ? getCodeForNode(customSections, customNode.id) : null
  const answer = fieldId ? answers[fieldId] : null
  if (!open || !leaf || !answer) return null

  const hasCompleteness = answer.completeness != null
  const hasConfidence = answer.confidence != null
  const tier = hasConfidence ? confidenceTier(answer.confidence) : null
  const missingItems = answer.missing || []

  return (
    <Modal open={open} onClose={onClose}>
      <ModalHeader title={`${code} ${leaf.title}`} onClose={onClose} size="sm" />
      <div className="flex items-center gap-2.5 mt-2.5">
        {hasCompleteness && (
          <span className="text-[11px] font-semibold text-text-tertiary">{answer.completeness}% complete</span>
        )}
        {hasConfidence && tier && (
          <span
            className="text-[11px] font-bold uppercase tracking-wide"
            style={{ color: CONFIDENCE_COLOR_HEX[tier] }}
          >
            {answer.confidence}% {tier} confidence
          </span>
        )}
      </div>

      <ConfidenceBreakdown breakdown={answer.confidence_breakdown} />

      {answer.answer && (
        <div className="mt-4 pt-3 border-t border-border-light">
          <div className="text-[11px] font-bold uppercase tracking-wider text-text-primary/80 mb-1.5">
            Current Draft
          </div>
          <div className="text-sm leading-relaxed text-text-primary bg-bg-subtle p-3 rounded-md border border-border-light">
            {answer.answer}
          </div>
        </div>
      )}

      <div className="mt-4 pt-3 border-t border-border-light">
        <div className="text-[11px] font-bold uppercase tracking-wider text-text-primary/80 mb-1.5">
          What's missing?
        </div>
        {missingItems.length > 0 ? (
          <ul className="m-0 pl-4 list-disc flex flex-col gap-1 text-[13px] text-text-primary leading-snug">
            {missingItems.map((m, idx) => (
              <li key={idx}>{m}</li>
            ))}
          </ul>
        ) : (
          <div className="text-[13px] text-text-tertiary">
            Nothing outstanding — this section is complete.
          </div>
        )}
      </div>

      <div className="flex justify-end mt-5.5">
        <button
          type="button"
          onClick={onClose}
          className="bg-text-primary text-white border-none rounded-btn h-10 px-5 text-[13px] font-semibold cursor-pointer"
        >
          Close
        </button>
      </div>
    </Modal>
  )
}
