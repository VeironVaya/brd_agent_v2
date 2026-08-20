import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext.jsx'

/** Derive up-to-two-letter initials from a display name. */
function initials(name) {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length === 1) return parts[0][0].toUpperCase()
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
}

export default function UserMenu({ onLogout }) {
  const [open, setOpen] = useState(false)
  const { user } = useAuth()

  return (
    <div className="relative flex-shrink-0">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label="Account menu"
        title={user?.name || 'Account'}
        className="w-10 h-10 rounded-full bg-text-primary text-white flex items-center justify-center cursor-pointer border-none text-sm font-semibold tracking-wide select-none"
      >
        {user ? initials(user.name) : '?'}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute top-12 right-0 bg-white border border-border rounded-btn shadow-dropdown z-20 overflow-hidden w-52">
            {/* User identity block */}
            {user && (
              <div className="px-4 py-3 border-b border-border">
                <div className="text-sm font-semibold text-text-primary truncate">{user.name}</div>
                <div className="text-xs text-text-tertiary truncate mt-0.5">{user.email}</div>
              </div>
            )}
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

