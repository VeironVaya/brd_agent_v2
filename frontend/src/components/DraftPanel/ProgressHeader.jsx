export default function ProgressHeader({ percent, buckets }) {
  return (
    <div className="px-7 pt-7 pb-5 border-b border-divider">
      <div className="flex items-baseline justify-between">
        <span className="text-base font-semibold">Progress</span>
        <span className="text-4xl font-bold tracking-tight">{percent}%</span>
      </div>
      <div className="text-[13px] text-text-secondary mt-0.5">
        {buckets.answered} answered · {buckets.ready} ready · {buckets.locked} locked ·{' '}
        {buckets.needs_review} need review
      </div>
      <div className="text-[11.5px] text-text-tertiary mt-1.5 leading-snug">
        Completeness = required fields captured for that item · Confidence = the model's
        certainty in the answer given
      </div>
      <div className="h-1.5 rounded-pill bg-bg-subtlest mt-3.5 overflow-hidden">
        <div className="h-full bg-text-primary" style={{ width: `${percent}%` }} />
      </div>
      <div className="flex flex-wrap gap-3 mt-3.5">
        <span className="flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <span
            className="w-3 h-3 rounded-full inline-block relative"
            style={{ background: 'conic-gradient(#222222 0% 60%, #eeeeee 60% 100%)' }}
          >
            <span className="absolute inset-[2px] bg-white rounded-full">
              <span
                className="absolute inset-[1.5px] rounded-full"
                style={{ background: 'conic-gradient(#1a7f37 0% 70%, #eeeeee 70% 100%)' }}
              />
            </span>
          </span>
          Completeness · Confidence
        </span>
        <span className="flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#c13515" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 22V4" />
            <path d="M4 4h13l-2.5 4L17 12H4" />
          </svg>
          Flagged
        </span>
        <span className="flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#c1c1c1" strokeWidth="2.2">
            <rect x="5.5" y="10.5" width="13" height="9" rx="2" />
            <path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5" />
          </svg>
          Locked (tap disabled until deps are met)
        </span>
        <span className="flex items-center gap-1.5 text-[11px] text-text-tertiary">
          <span className="w-3 h-3 bg-bg-subtler border-l-2 border-text-primary inline-block" />
          Focused (tapped)
        </span>
      </div>
    </div>
  )
}
