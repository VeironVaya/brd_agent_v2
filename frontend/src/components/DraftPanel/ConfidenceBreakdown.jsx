import React from 'react'

const DIMENSIONS = [
  { key: 'grounding',          label: 'Grounding / Factual Support' },
  { key: 'reference_context',  label: 'Reference & Context Alignment' },
  { key: 'section_compliance', label: 'Section-Specific Compliance' },
  { key: 'testability',        label: 'Testability & Actionability' },
  { key: 'consistency',        label: 'Consistency & Logical Coherence' },
]

function scoreTier(score) {
  if (score == null) return 'na'
  if (score >= 85) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

const TIER_STYLES = {
  high:   { bar: 'bg-green-600', text: 'text-green-700', bg: 'bg-green-100' },
  medium: { bar: 'bg-amber-600', text: 'text-amber-700', bg: 'bg-amber-100' },
  low:    { bar: 'bg-red-600',   text: 'text-red-700',   bg: 'bg-red-100' },
  na:     { bar: 'bg-gray-300',  text: 'text-gray-500',  bg: 'bg-gray-100' },
}

export const DEP_STATUS_STYLES = {
  CONSISTENT:          { text: 'text-green-700', bg: 'bg-green-50', border: 'border-green-200', label: 'Dependencies Consistent' },
  CONFLICT:            { text: 'text-red-700',   bg: 'bg-red-50',   border: 'border-red-200',   label: 'Dependency Conflict' },
  NOT_YET_VERIFIABLE:  { text: 'text-gray-600',  bg: 'bg-gray-50',  border: 'border-gray-200',  label: 'Prerequisites Pending' },
}

function DimensionCard({ label, score, reason }) {
  const tier = scoreTier(score)
  const styles = TIER_STYLES[tier]
  const isNA = score == null

  return (
    <div className="flex flex-col gap-2 p-3.5 bg-bg-subtle/40 rounded-xl transition-all duration-200 hover:bg-bg-subtle/80">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11.5px] font-semibold text-text-primary leading-snug">
          {label}
        </span>
        <span
          className={`text-[10.5px] font-bold px-2 py-0.5 rounded-md flex-shrink-0 tracking-wide ${styles.text} ${styles.bg}`}
        >
          {isNA ? 'N/A' : score + '%'}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-gray-200 overflow-hidden w-full">
        <div
          className={`h-full rounded-full transition-all duration-500 ease-out ${styles.bar}`}
          style={{ width: isNA ? '0%' : score + '%' }}
        />
      </div>
      <p className="m-0 text-[11.5px] text-text-secondary leading-relaxed mt-1">
        {reason || (isNA ? 'Not applicable for this section.' : '')}
      </p>
    </div>
  )
}

export function ReviewRequiredBanner({ breakdown }) {
  if (!breakdown) return null
  const isReviewRequired = breakdown.review_status === 'REVIEW_REQUIRED' || (breakdown.critical_flags && breakdown.critical_flags.length > 0)
  if (!isReviewRequired) return null

  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 shadow-sm mb-4">
      <div className="flex items-center gap-1.5 text-red-700 font-bold text-xs uppercase tracking-wide">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <path d="M12 9v4"/>
          <path d="M12 17h.01"/>
        </svg>
        <span>IMPORTANT: Critical Issues Detected</span>
      </div>
      {breakdown.critical_flags && breakdown.critical_flags.length > 0 && (
        <ul className="mt-2 pl-6 text-[11.5px] text-red-800 leading-relaxed list-disc space-y-1">
          {breakdown.critical_flags.map((flag, idx) => (
            <li key={idx}>
              <strong>[{flag.type || 'CRITICAL_FLAG'}]</strong> {flag.reason}
              {flag.excerpt && <span className="italic opacity-85"> &ldquo;{flag.excerpt}&rdquo;</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function ScoringCards({ breakdown }) {
  if (!breakdown) return null
  const populated = DIMENSIONS.filter((d) => breakdown[d.key] != null)
  if (populated.length === 0) return null

  return (
    <div className="grid grid-cols-1 gap-2 mb-3">
      {populated.map((d) => (
        <DimensionCard
          key={d.key}
          label={d.label}
          score={breakdown[d.key].score}
          reason={breakdown[d.key].reason}
        />
      ))}
    </div>
  )
}

export function StrengthsCard({ breakdown }) {
  if (!breakdown || !Array.isArray(breakdown.critique_strengths) || breakdown.critique_strengths.length === 0) return null
  return (
    <div className="rounded-xl bg-green-50/70 p-4 border border-green-100/50 mt-3">
      <div className="flex items-center gap-1.5 text-[10.5px] font-bold text-green-700 uppercase tracking-wide mb-1.5">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 6 9 17l-5-5"/>
        </svg>
        <span>Key Strengths</span>
      </div>
      <ul className="m-0 pl-6 text-[12px] text-green-900 leading-relaxed list-disc space-y-1.5">
        {breakdown.critique_strengths.map((str, idx) => (
          <li key={idx}>{str}</li>
        ))}
      </ul>
    </div>
  )
}

export function IssuesCard({ breakdown }) {
  if (!breakdown || !Array.isArray(breakdown.critique_issues) || breakdown.critique_issues.length === 0) return null
  return (
    <div className="rounded-xl bg-amber-50/70 p-4 border border-amber-100/50 mt-3">
      <div className="flex items-center gap-1.5 text-[10.5px] font-bold text-amber-700 uppercase tracking-wide mb-1.5">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>Identified Issues</span>
      </div>
      <ul className="m-0 pl-6 text-[12px] text-amber-900 leading-relaxed list-disc space-y-1.5">
        {breakdown.critique_issues.map((issue, idx) => (
          <li key={idx}>{issue}</li>
        ))}
      </ul>
    </div>
  )
}

export function SuggestionsCard({ breakdown }) {
  if (!breakdown || !Array.isArray(breakdown.critique_suggestions) || breakdown.critique_suggestions.length === 0) return null
  return (
    <div className="rounded-xl bg-blue-50/70 p-4 border border-blue-100/50 mt-3">
      <div className="flex items-center gap-1.5 text-[10.5px] font-bold text-blue-700 uppercase tracking-wide mb-1.5">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2v2"/>
          <path d="M12 20v2"/>
          <path d="m4.93 4.93 1.41 1.41"/>
          <path d="m17.66 17.66 1.41 1.41"/>
          <path d="M2 12h2"/>
          <path d="M20 12h2"/>
          <path d="m6.34 17.66-1.41 1.41"/>
          <path d="m19.07 4.93-1.41 1.41"/>
        </svg>
        <span>Suggested Improvements</span>
      </div>
      <ul className="m-0 pl-6 text-[12px] text-blue-900 leading-relaxed list-disc space-y-1.5">
        {breakdown.critique_suggestions.map((sug, idx) => (
          <li key={idx}>{sug}</li>
        ))}
      </ul>
    </div>
  )
}
