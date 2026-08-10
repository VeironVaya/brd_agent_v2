import { useState } from 'react'

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')

  function handleSend() {
    const text = value.trim()
    if (!text || disabled) return
    onSend(text)
    setValue('')
  }

  return (
    <div className="px-10 pt-5 pb-7 flex items-center gap-3">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="Type your answer…"
        className="flex-1 h-14 bg-white rounded-btn px-4.5 text-base outline-none shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)] focus:shadow-[0_0_0_1.5px_#222222]"
      />
      <button
        type="button"
        aria-label="Send"
        onClick={handleSend}
        disabled={disabled}
        className="w-12 h-12 rounded-pill bg-accent border-none flex items-center justify-center cursor-pointer flex-shrink-0 disabled:opacity-50"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12h14" />
          <path d="m12 5 7 7-7 7" />
        </svg>
      </button>
    </div>
  )
}
