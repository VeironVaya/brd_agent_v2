/**
 * ConfidenceBreakdown – displays the 5-dimension AI confidence analysis.
 *
 * Props:
 *   breakdown: ConfidenceBreakdownDto | null | undefined
 *     {
 *       grounding:          { score: number, reason: string } | null
 *       reference_context:  { score: number, reason: string } | null
 *       section_compliance: { score: number, reason: string } | null
 *       testability:        { score: number, reason: string } | null
 *       consistency:        { score: number, reason: string } | null
 *     }
 *
 * If breakdown is null/undefined the component renders nothing — safe for
 * old answer rows that were saved before this feature shipped.
 */

const DIMENSIONS = [
  { key: 'grounding',          label: 'Grounding / Factual Support' },
  { key: 'reference_context',  label: 'Reference & Context Alignment' },
  { key: 'section_compliance', label: 'Section-Specific Compliance' },
  { key: 'testability',        label: 'Testability & Actionability' },
  { key: 'consistency',        label: 'Consistency & Logical Coherence' },
]

function scoreTier(score) {
  if (score >= 70) return 'high'
  if (score >= 40) return 'medium'
  return 'low'
}

const TIER_COLORS = {
  high:   { bar: '#1a7f37', text: '#1a7f37', bg: 'rgba(26,127,55,0.08)' },
  medium: { bar: '#b45309', text: '#b45309', bg: 'rgba(180,83,9,0.08)' },
  low:    { bar: '#c13515', text: '#c13515', bg: 'rgba(193,53,21,0.08)' },
}

function DimensionCard({ label, score, reason }) {
  const tier = scoreTier(score)
  const colors = TIER_COLORS[tier]

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
          {score}%
        </span>
      </div>

      {/* Progress bar */}
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
            width: `${score}%`,
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
        {reason}
      </p>
    </div>
  )
}

export default function ConfidenceBreakdown({ breakdown }) {
  if (!breakdown) return null

  // Only render dimensions that actually have data
  const populated = DIMENSIONS.filter((d) => breakdown[d.key] != null)
  if (populated.length === 0) return null

  return (
    <div style={{ marginTop: '20px' }}>
      {/* Section header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          marginBottom: '10px',
        }}
      >
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

      {/* Dimension cards */}
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
    </div>
  )
}
