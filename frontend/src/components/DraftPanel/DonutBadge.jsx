import { CONFIDENCE_COLOR_HEX } from '../../utils/confidenceColors.js'

/** Dual-ring donut: outer ring = completeness %, inner disc = confidence %. */
export default function DonutBadge({ completeness, confidence, tier, flagged }) {
  return (
    <div className="relative flex-shrink-0">
      <div
        className="relative w-5 h-5 rounded-full flex-shrink-0"
        style={{ background: `conic-gradient(#222222 0% ${completeness}%, #eeeeee ${completeness}% 100%)` }}
      >
        <div className="absolute inset-[3px] bg-white rounded-full">
          <div
            className="absolute inset-[3px] rounded-full"
            style={{
              background: `conic-gradient(${CONFIDENCE_COLOR_HEX[tier]} 0% ${confidence}%, #eeeeee ${confidence}% 100%)`,
            }}
          />
        </div>
      </div>
      {flagged && (
        <svg
          width="9"
          height="9"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#c13515"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="absolute -top-0.75 -right-1 bg-white rounded-full"
        >
          <path d="M4 22V4" />
          <path d="M4 4h13l-2.5 4L17 12H4" />
        </svg>
      )}
    </div>
  )
}
