import { CONFIDENCE_COLOR_HEX } from '../../utils/confidenceColors.js'
import { FIELD_META, confidenceTier } from '../../utils/draftFields.js'
import { findCustomNode, getCodeForNode } from '../../utils/customSectionTree.js'
import Accordion from '../common/Accordion.jsx'
import { isChoiceSection } from '../../utils/choiceSections.js'
import { 
  ReviewRequiredBanner, 
  ScoringCards, 
  StrengthsCard, 
  IssuesCard, 
  SuggestionsCard,
  DEP_STATUS_STYLES
} from './ConfidenceBreakdown.jsx'

function AlertTriangleIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <path d="M12 9v4"/>
      <path d="M12 17h.01"/>
    </svg>
  )
}

function DocumentIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
  )
}

function BarChartIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="20" x2="12" y2="10"/>
      <line x1="18" y1="20" x2="18" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="16"/>
    </svg>
  )
}

export default function AnswerDetailPanel({ fieldId, answers, customSections = [] }) {
  const templateLeaf = fieldId ? FIELD_META[fieldId] : null
  const customNode = !templateLeaf && fieldId ? findCustomNode(customSections, fieldId) : null
  const leaf = templateLeaf || (customNode ? { id: customNode.id, title: customNode.title } : null)
  const code = templateLeaf ? templateLeaf.id : customNode ? getCodeForNode(customSections, customNode.id) : null
  const answer = fieldId ? answers[fieldId] : null

  if (!leaf) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-text-tertiary p-6 text-center">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="mb-4 opacity-40">
          <rect x="3" y="3" width="18" height="18" rx="3" ry="3" />
          <line x1="9" y1="3" x2="9" y2="21" />
        </svg>
        <p className="text-[13px] font-medium tracking-wide opacity-80">Select a section to view its details</p>
      </div>
    )
  }

  if (!answer) {
    return (
      <div className="p-7">
        <div className="text-[22px] font-extrabold text-text-primary tracking-tight mb-1">
          {code} {leaf.title}
        </div>
        <div className="text-[14px] text-text-tertiary mt-6 font-medium">
          No answer has been started for this section yet.
        </div>
      </div>
    )
  }

  const hasCompleteness = answer.completeness != null
  const hasConfidence = answer.confidence != null
  const tier = hasConfidence ? confidenceTier(answer.confidence) : null
  const missingItems = answer.missing || []
  const breakdown = answer.confidence_breakdown

  const isFiller = (text) => {
    const t = text.toLowerCase()
    return t.includes('no critical issues') || t.includes('no issues') || t.includes('no significant issues') || t.includes('no suggestions') || t.trim() === 'none'
  }

  const cleanBreakdown = breakdown ? {
    ...breakdown,
    critique_issues: (breakdown.critique_issues || []).filter(i => !isFiller(i)),
    critique_suggestions: (breakdown.critique_suggestions || []).filter(s => !isFiller(s))
  } : null

  const depStyle = cleanBreakdown?.dependency_status ? DEP_STATUS_STYLES[cleanBreakdown.dependency_status] : null
  
  // Calculate action items count
  const missingCount = missingItems.length
  const issuesCount = cleanBreakdown?.critique_issues?.length || 0
  const suggestionsCount = cleanBreakdown?.critique_suggestions?.length || 0
  const hasActionItems = missingCount > 0 || issuesCount > 0 || suggestionsCount > 0

  const actionItemsBadge = (
    <>
      {missingCount > 0 && (
        <span className="flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-bold bg-orange-100 text-orange-700 rounded-full border border-orange-200" title="Missing Items">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          {missingCount}
        </span>
      )}
      {issuesCount > 0 && (
        <span className="flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-bold bg-amber-100 text-amber-700 rounded-full border border-amber-200" title="Issues">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          {issuesCount}
        </span>
      )}
      {suggestionsCount > 0 && (
        <span className="flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-bold bg-blue-100 text-blue-700 rounded-full border border-blue-200" title="Suggestions">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v2M12 20v2m-7.07-15.07 1.41 1.41m12.72 12.72 1.41 1.41M2 12h2m16 0h2m-13.66 5.66-1.41 1.41m12.72-12.72-1.41 1.41"></path></svg>
          {suggestionsCount}
        </span>
      )}
    </>
  )

  return (
    <div className="flex flex-col h-full overflow-y-auto relative">
      {/* Sticky Header with Frosted Glass Effect */}
      <div className="sticky top-0 z-10 p-7 pb-4 bg-white/90 backdrop-blur-md border-b border-border-light/50">
        <div className="text-[22px] font-extrabold text-text-primary tracking-tight leading-snug">
          {code} {leaf.title}
        </div>
        
        <div className="flex items-center gap-3 mt-3">
          {hasCompleteness && (
            <span className="text-[11.5px] font-bold text-text-tertiary">{answer.completeness}% complete</span>
          )}
          {hasConfidence && tier && (
            <span
              className="text-[11.5px] font-extrabold uppercase tracking-wide"
              style={{ color: CONFIDENCE_COLOR_HEX[tier] }}
            >
              {answer.confidence}% {tier} confidence
            </span>
          )}
          {depStyle && (
            <span
              title={
                breakdown.dependency_status === 'NOT_YET_VERIFIABLE'
                  ? "This section's logic cannot be fully verified yet because other sections it depends on have not been drafted."
                  : breakdown.dependency_status === 'CONFLICT'
                  ? "This section contradicts information in other drafted sections."
                  : "This section is consistent with all other drafted sections."
              }
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border shadow-sm tracking-wide ml-auto cursor-help ${depStyle.bg} ${depStyle.text} ${depStyle.border}`}
            >
              {depStyle.label}
            </span>
          )}
        </div>
      </div>

      <div className="p-7 pt-4">
        {/* Banner */}
        <ReviewRequiredBanner breakdown={cleanBreakdown} />

        {isChoiceSection(fieldId) && (
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-5 mb-4 text-center">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="mx-auto mb-3 text-slate-400">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <h4 className="text-[13px] font-bold text-slate-700 mb-1">Structured Choice Section</h4>
            <p className="text-[12.5px] text-slate-500 leading-relaxed">
              This is a rigid choice section. You can use the chat to brainstorm, but you must click the <strong>"Choose options"</strong> button on the left to officially record your answer. The AI Quality Reviewer does not evaluate choice sections.
            </p>
          </div>
        )}

        {/* Current Draft (Accordion) */}
        {answer.answer && (
          <Accordion 
            title="Current Draft" 
            icon={<DocumentIcon />} 
            defaultOpen={true}
          >
            <div className="text-[13.5px] leading-relaxed text-text-primary mt-2">
              {answer.answer}
            </div>
          </Accordion>
        )}

        {/* Accordion 1: Action Items */}
        {hasActionItems && !isChoiceSection(fieldId) && (
          <Accordion 
            title="Action Items" 
            icon={<AlertTriangleIcon />} 
            badge={actionItemsBadge}
            defaultOpen={hasActionItems}
          >
            <div className="flex flex-col gap-4">
              {/* Missing Items */}
              {missingItems.length > 0 && (
                <div className="rounded-xl bg-orange-50/70 p-4 border border-orange-100/50 mt-3">
                  <div className="flex items-center gap-1.5 text-[10.5px] font-bold text-orange-700 uppercase tracking-wide mb-1.5">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span>What's missing?</span>
                  </div>
                  <ul className="m-0 pl-6 text-[12px] text-orange-900 leading-relaxed list-disc space-y-1.5">
                    {missingItems.map((m, idx) => (
                      <li key={idx}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Issues & Suggestions */}
              <IssuesCard breakdown={cleanBreakdown} />
              <SuggestionsCard breakdown={cleanBreakdown} />
            </div>
          </Accordion>
        )}

        {/* Accordion 2: Scoring & Strengths */}
        {!isChoiceSection(fieldId) && (
          <Accordion title="Confidence & Analysis" icon={<BarChartIcon />}>
            <div className="flex flex-col gap-4">
              <div className="mt-2">
                <ScoringCards breakdown={cleanBreakdown} />
              </div>
              <StrengthsCard breakdown={cleanBreakdown} />
            </div>
          </Accordion>
        )}
      </div>
    </div>
  )
}
