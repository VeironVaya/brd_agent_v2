export default function Logo({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="10" fill="#222222" />
      <path
        d="M9 12.5a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-5.5L11 23v-3.2A3 3 0 0 1 9 17V12.5Z"
        fill="none"
        stroke="#ffffff"
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <circle cx="20" cy="14.5" r="1.6" fill="#ff385c" />
    </svg>
  )
}
