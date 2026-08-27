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
  const tier = confidenceTier(answer.confidence)

  return (
    <Modal open={open} onClose={onClose}>
      <ModalHeader title={`${code} ${leaf.title}`} onClose={onClose} size="sm" />
      <div className="flex items-center gap-2.5 mt-2.5">
        <span className="text-[11px] font-semibold text-text-tertiary">{answer.completeness}% complete</span>
        <span
          className="text-[11px] font-bold uppercase tracking-wide"
          style={{ color: CONFIDENCE_COLOR_HEX[tier] }}
        >
          {answer.confidence}% {tier} confidence
        </span>
      </div>
      <ConfidenceBreakdown breakdown={answer.confidence_breakdown} />
      <div className="text-sm mt-3.5 leading-relaxed">{answer.answer}</div>
      {answer.confidence_reason && (
        <div className="mt-3.5 p-3 bg-bg-subtle rounded-md border border-border text-[12.5px] text-text-secondary leading-relaxed">
          <div className="font-semibold text-text-primary mb-1 text-[11px] uppercase tracking-wider">
            Reason
          </div>
          {answer.confidence_reason}
        </div>
      )}
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
