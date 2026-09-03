/**
 * ConfidenceBreakdown - displays the 5-dimension AI confidence analysis,
 * critical issue flags, dependency status, and Senior BA critique.
 *
 * Props:
 *   breakdown: ConfidenceBreakdownDto | null | undefined
 */

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

const TIER_COLORS = {
  high:   { bar: '#1a7f37', text: '#1a7f37', bg: 'rgba(26,127,55,0.08)' },
  medium: { bar: '#b45309', text: '#b45309', bg: 'rgba(180,83,9,0.08)' },
  low:    { bar: '#c13515', text: '#c13515', bg: 'rgba(193,53,21,0.08)' },
  na:     { bar: '#9ca3af', text: '#6b7280', bg: 'rgba(107,114,128,0.1)' },
}

const DEP_STATUS_STYLES = {
  CONSISTENT:          { text: '#166534', bg: '#dcfce7', border: '#bbf7d0', label: 'Dependencies Consistent' },
  CONFLICT:            { text: '#991b1b', bg: '#fee2e2', border: '#fca5a5', label: 'Dependency Conflict' },
  NOT_YET_VERIFIABLE:  { text: '#475569', bg: '#f1f5f9', border: '#cbd5e1', label: 'Prerequisites Pending' },
}

function DimensionCard({ label, score, reason }) {
  const tier = scoreTier(score)
  const colors = TIER_COLORS[tier]
  const isNA = score == null

  return (
    <div
      style={{
        borderRadius: '8px',
        border: '1px solid var(--color-border-light, #e5e5e5)',
        padding: '10px 12px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        background: 'var(--color-bg-subtle, #fafafa)',
      }}
    >
      {/* Header row: label + score badge */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        <span style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-primary, #111)', lineHeight: 1.3 }}>
          {label}
        </span>
        <span
          style={{
            fontSize: '11px',
            fontWeight: 700,
            color: colors.text,
            background: colors.bg,
            borderRadius: '4px',
            padding: '1px 6px',
            flexShrink: 0,
            letterSpacing: '0.02em',
          }}
        >
          {isNA ? 'N/A' : score + '%'}
        </span>
      </div>

      {/* Progress bar - Never 0% bar for N/A */}
      <div
        style={{
          height: '4px',
          borderRadius: '2px',
          background: 'var(--color-border-light, #e5e5e5)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: isNA ? '0%' : score + '%',
            background: colors.bar,
            borderRadius: '2px',
            transition: 'width 0.4s ease',
          }}
        />
      </div>

      {/* Reason text */}
      <p
        style={{
          margin: 0,
          fontSize: '11.5px',
          color: 'var(--color-text-secondary, #555)',
          lineHeight: 1.55,
        }}
      >
        {reason || (isNA ? 'Not applicable for this section.' : '')}
      </p>
    </div>
  )
}

export default function ConfidenceBreakdown({ breakdown }) {
  if (!breakdown) return null

  // Only render dimensions that actually have data
  const populated = DIMENSIONS.filter((d) => breakdown[d.key] != null)
  if (populated.length === 0) return null

  const isReviewRequired = breakdown.review_status === 'REVIEW_REQUIRED' || (breakdown.critical_flags && breakdown.critical_flags.length > 0)
  const depStyle = breakdown.dependency_status ? DEP_STATUS_STYLES[breakdown.dependency_status] : null

  const hasStrengths = Array.isArray(breakdown.critique_strengths) && breakdown.critique_strengths.length > 0
  const hasIssues = Array.isArray(breakdown.critique_issues) && breakdown.critique_issues.length > 0
  const hasSuggestions = Array.isArray(breakdown.critique_suggestions) && breakdown.critique_suggestions.length > 0

  return (
    <div style={{ marginTop: '20px' }}>
      {/* Critical issue warning banner */}
      {isReviewRequired && (
        <div
          style={{
            borderRadius: '8px',
            border: '1px solid #fca5a5',
            background: '#fef2f2',
            padding: '10px 12px',
            marginBottom: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#991b1b', fontWeight: 700, fontSize: '11.5px' }}>
            <span>⚠️ REVIEW REQUIRED: Critical Issues Detected</span>
          </div>
          {breakdown.critical_flags && breakdown.critical_flags.length > 0 && (
            <ul style={{ margin: '6px 0 0 16px', padding: 0, fontSize: '11px', color: '#7f1d1d', lineHeight: 1.5 }}>
              {breakdown.critical_flags.map((flag, idx) => (
                <li key={idx}>
                  <strong>[{flag.type || 'CRITICAL_FLAG'}]</strong> {flag.reason}
                  {flag.excerpt && <span style={{ fontStyle: 'italic', opacity: 0.85 }}> &ldquo;{flag.excerpt}&rdquo;</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Section header + Dependency badge */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '8px',
          marginBottom: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1 }}>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: 'var(--color-text-primary, #111)',
            }}
          >
            Confidence Breakdown
          </span>
          <span
            style={{
              flex: 1,
              height: '1px',
              background: 'var(--color-border-light, #e5e5e5)',
            }}
          />
        </div>

        {depStyle && (
          <span
            style={{
              fontSize: '10.5px',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '9999px',
              background: depStyle.bg,
              color: depStyle.text,
              border: '1px solid ' + depStyle.border,
              whiteSpace: 'nowrap',
            }}
          >
            {depStyle.label}
          </span>
        )}
      </div>

      {/* 5 Dimension cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {populated.map((d) => (
          <DimensionCard
            key={d.key}
            label={d.label}
            score={breakdown[d.key].score}
            reason={breakdown[d.key].reason}
          />
        ))}
      </div>

      {/* Senior BA Critique (Strengths, Issues, Suggestions) */}
      {(hasStrengths || hasIssues || hasSuggestions) && (
        <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {/* Strengths */}
          {hasStrengths && (
            <div
              style={{
                borderRadius: '8px',
                border: '1px solid #bbf7d0',
                background: '#f0fdf4',
                padding: '9px 12px',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#166534', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                ✓ Key Strengths
              </div>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '11.5px', color: '#14532d', lineHeight: 1.5 }}>
                {breakdown.critique_strengths.map((str, idx) => (
                  <li key={idx}>{str}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Issues */}
          {hasIssues && (
            <div
              style={{
                borderRadius: '8px',
                border: '1px solid #fed7aa',
                background: '#fffbeb',
                padding: '9px 12px',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#9a3412', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                ! Identified Issues
              </div>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '11.5px', color: '#7c2d12', lineHeight: 1.5 }}>
                {breakdown.critique_issues.map((issue, idx) => (
                  <li key={idx}>{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggestions */}
          {hasSuggestions && (
            <div
              style={{
                borderRadius: '8px',
                border: '1px solid #bfdbfe',
                background: '#eff6ff',
                padding: '9px 12px',
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 700, color: '#1e40af', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                💡 Suggested Improvements
              </div>
              <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '11.5px', color: '#1e3a8a', lineHeight: 1.5 }}>
                {breakdown.critique_suggestions.map((sug, idx) => (
                  <li key={idx}>{sug}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
