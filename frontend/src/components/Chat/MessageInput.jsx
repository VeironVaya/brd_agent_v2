import { useState, useRef, useEffect } from 'react'

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '56px'
      const scrollHeight = textareaRef.current.scrollHeight
      textareaRef.current.style.height = Math.max(56, Math.min(scrollHeight, 200)) + 'px'
    }
  }, [value])

  function handleSend() {
    const text = value.trim()
    if (!text || disabled) return
    onSend(text)
    setValue('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="px-10 pt-5 pb-7 flex items-end gap-3">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your answer…"
        disabled={disabled}
        rows={1}
        className="flex-1 min-h-[56px] py-4 bg-white rounded-btn px-4.5 text-base outline-none shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)] focus:shadow-[0_0_0_1.5px_#222222] disabled:opacity-60 disabled:cursor-not-allowed resize-none overflow-y-auto block leading-normal"
      />
      <button
        type="button"
        aria-label="Send"
        onClick={handleSend}
        disabled={disabled}
        className="w-12 h-12 mb-1 rounded-pill bg-accent border-none flex items-center justify-center cursor-pointer flex-shrink-0 disabled:opacity-50"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12h14" />
          <path d="m12 5 7 7-7 7" />
        </svg>
      </button>
    </div>
  )
}
