const VARIANTS = {
  primary:
    'bg-accent text-white hover:bg-accent-hover disabled:bg-accent-tint disabled:cursor-not-allowed',
  secondary:
    'bg-white text-text-primary border border-border hover:bg-bg-subtle',
  ghost: 'bg-transparent text-text-primary hover:bg-bg-subtle',
}

const SIZES = {
  sm: 'h-10 px-3.5 text-sm',
  md: 'h-12 px-4 text-[15px]',
  lg: 'h-13 px-5 text-base',
}

export default function Button({
  as = 'button',
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}) {
  const Tag = as
  return (
    <Tag
      type={Tag === 'button' ? 'button' : undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-btn font-semibold cursor-pointer transition-colors ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...props}
    >
      {children}
    </Tag>
  )
}
