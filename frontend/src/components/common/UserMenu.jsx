import { useState } from 'react'

export default function UserMenu({ onLogout }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="relative flex-shrink-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Account menu"
        className="w-10 h-10 rounded-full bg-text-primary text-white flex items-center justify-center cursor-pointer border-none"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 21a8 8 0 0 0-16 0" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute top-12 right-0 bg-white border border-border rounded-btn shadow-dropdown z-20 overflow-hidden w-44">
            <button
              type="button"
              onClick={() => {
                setOpen(false)
                onLogout()
              }}
              className="flex items-center gap-2.5 w-full px-4 py-3 text-sm text-text-primary cursor-pointer bg-white hover:bg-bg-subtle text-left border-none"
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <path d="M16 17l5-5-5-5" />
                <path d="M21 12H9" />
              </svg>
              Log out
            </button>
          </div>
        </>
      )}
    </div>
  )
}
