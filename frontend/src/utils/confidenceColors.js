// Raw hex values for contexts that need them directly (inline conic-gradient
// styles, SVG stroke) rather than a Tailwind utility class. Mirrors the
// --color-confidence-* tokens in src/index.css.
export const CONFIDENCE_COLOR_HEX = {
  HIGH: '#1a7f37',
  MEDIUM: '#b45309',
  LOW: '#c13515',
  NONE: '#c1c1c1',
}
