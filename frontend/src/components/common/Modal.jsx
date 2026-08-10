export default function Modal({ open, onClose, maxWidth = 480, zIndex = 10, children }) {
  if (!open) return null
  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center p-6"
      style={{ zIndex }}
      onClick={onClose}
    >
      <div
        className="w-full bg-white rounded-modal p-7 shadow-modal max-h-[86vh] overflow-y-auto"
        style={{ maxWidth }}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  )
}

export function ModalHeader({ title, onClose, size = 'lg' }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className={size === 'lg' ? 'text-[19px] font-bold' : 'text-[17px] font-bold'}>
        {title}
      </span>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="p-1 text-text-secondary cursor-pointer flex-shrink-0"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M18 6 6 18" />
            <path d="m6 6 12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}
