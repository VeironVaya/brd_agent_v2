const inputBase =
  'bg-white font-[inherit] rounded-btn px-4 text-[15px] text-text-primary outline-none border'

export function TextField({ label, hint, error, className = '', ...props }) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label className="text-[13px] font-semibold">
          {label}
          {hint && <span className="text-text-tertiary font-normal"> {hint}</span>}
        </label>
      )}
      <input
        {...props}
        className={`h-12 ${inputBase} ${
          error ? 'border-[1.5px] border-confidence-low' : 'border-border focus:border-text-primary'
        }`}
      />
      {error && <div className="text-[12.5px] text-confidence-low leading-snug">{error}</div>}
    </div>
  )
}

export function TextAreaField({ label, hint, rows = 3, className = '', ...props }) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label className="text-[13px] font-semibold">
          {label}
          {hint && <span className="text-text-tertiary font-normal"> {hint}</span>}
        </label>
      )}
      <textarea
        rows={rows}
        {...props}
        className={`${inputBase} border-border focus:border-text-primary py-3 resize-none`}
      />
    </div>
  )
}
