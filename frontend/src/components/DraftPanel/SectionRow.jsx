import DonutBadge from './DonutBadge.jsx'
import { CONFIDENCE_COLOR_HEX } from '../../utils/confidenceColors.js'
import { FIELD_META, fieldState, isBlocked, confidenceTier } from '../../utils/draftFields.js'

const TIER_LABEL = { HIGH: 'HIGH', MEDIUM: 'MEDIUM', LOW: 'LOW' }

export function buildNote(leaf, answers) {
  const blocked = isBlocked(leaf.id, answers)
  const neededLabels = blocked
    ? leaf.dependsOn
        .filter((depId) => fieldState(depId, answers) !== 'done')
        .map((depId) => `${depId} ${FIELD_META[depId].title}`)
    : []
  let note = ''
  if (blocked) {
    note = 'Needs: ' + neededLabels.join(', ')
  }
  return note
}

export default function SectionRow({ leaf, answers, focusedFieldId, onFocus, onViewAnswer, grouped }) {
  const status = fieldState(leaf.id, answers)
  const answer = answers[leaf.id] || {}
  const blocked = isBlocked(leaf.id, answers)
  const hasCompleteness = answer.completeness != null
  const hasConfidence = answer.confidence != null
  const hasMetrics = hasCompleteness || hasConfidence
  const tier = hasConfidence ? confidenceTier(answer.confidence) : null
  const isFocused = !blocked && leaf.id === focusedFieldId
  const note = buildNote(leaf, answers)
  const hasAnswer = !!answer.answer
  const missingItems = answer.missing || []

  const textColorClass = status === 'locked' ? 'text-text-tertiary' : 'text-text-primary'

  return (
    <div className={grouped ? 'border-l-2 border-border-light ml-2 pl-3.5' : ''}>
      <div
        onClick={blocked ? undefined : () => onFocus(leaf.id)}
        className={`flex gap-2.5 rounded-md ${note ? 'items-start' : 'items-center'} ${
          isFocused ? '-mx-2 px-2 py-2.25 bg-bg-subtler border-l-3 border-text-primary' : 'py-2.25 border-l-3 border-transparent'
        } ${blocked ? 'cursor-default' : 'cursor-pointer'}`}
      >
        {status === 'locked' ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c1c1c1" strokeWidth="1.8" className="flex-shrink-0 mt-0.5">
            <rect x="5.5" y="10.5" width="13" height="9" rx="2" />
            <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
          </svg>
        ) : (hasMetrics || status === 'progress' || status === 'done' || status === 'review') ? (
          <DonutBadge
            completeness={answer.completeness}
            confidence={answer.confidence}
            tier={tier}
            flagged={status === 'review' || !!answer.flagged}
          />
        ) : status === 'ready' ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c1c1c1" strokeWidth="1.8" className="flex-shrink-0">
            <circle cx="12" cy="12" r="9" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#c1c1c1" strokeWidth="1.8" className="flex-shrink-0">
            <circle cx="12" cy="12" r="9" />
          </svg>
        )}

        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-2">
            <span className={`text-sm ${textColorClass} ${status === 'progress' ? 'font-semibold' : 'font-normal'}`}>
              {leaf.id} {leaf.title}
            </span>
            {hasMetrics && (
              <span className="ml-auto flex items-baseline gap-2 flex-shrink-0">
                {hasCompleteness && (
                  <span className="text-[10.5px] font-semibold text-text-tertiary">
                    {answer.completeness}% complete
                  </span>
                )}
                {hasConfidence && tier && (
                  <span
                    className="text-[10.5px] font-bold uppercase tracking-wide"
                    style={{ color: CONFIDENCE_COLOR_HEX[tier] }}
                  >
                    {answer.confidence}% {TIER_LABEL[tier]}
                  </span>
                )}
              </span>
            )}
          </div>
          {note && <div className="text-[11px] text-text-tertiary mt-0.25">{note}</div>}
        </div>
      </div>

      {isFocused && (
        <div className="my-0.5 mb-1.5 px-3 py-2.5 bg-bg-subtle rounded-md">
          {hasAnswer && (
            <div className="mb-3 pb-3 border-b border-border-light">
              <div className="flex items-center justify-between mb-1.25">
                <span className="text-[11px] font-bold uppercase tracking-wider text-text-primary/80">
                  Result
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    onViewAnswer(leaf.id)
                  }}
                  className="bg-transparent border-none text-text-primary text-[11px] font-semibold cursor-pointer underline whitespace-nowrap"
                >
                  See details
                </button>
              </div>
              <div className="text-[13px] leading-relaxed">
                {answer.answer && answer.answer.length > 120
                  ? answer.answer.slice(0, 120).trimEnd() + '…'
                  : answer.answer}
              </div>
            </div>
          )}
          <div className="text-[11px] font-bold uppercase tracking-wider mb-1.25">What's missing?</div>
          {missingItems.length > 0 ? (
            <ul className="m-0 pl-4 list-disc flex flex-col gap-0.75">
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
    </div>
  )
}
