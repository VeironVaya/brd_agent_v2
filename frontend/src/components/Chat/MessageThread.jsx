import { useEffect, useRef } from 'react'
import Message from './Message.jsx'
import ThinkingIndicator from './ThinkingIndicator.jsx'

const NEAR_BOTTOM_THRESHOLD_PX = 80

export default function MessageThread({ messages, placeholderText, thinking }) {
  const containerRef = useRef(null)
  const wasNearBottomRef = useRef(true) // true on first mount — start scrolled to latest

  function handleScroll() {
    const el = containerRef.current
    if (!el) return
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    wasNearBottomRef.current = distanceFromBottom < NEAR_BOTTOM_THRESHOLD_PX
  }

  useEffect(() => {
    const el = containerRef.current
    // Only follow new content if the user was already at (or near) the
    // bottom — if they've scrolled up to read earlier answers, a new
    // message/thinking-indicator shouldn't yank them back down.
    if (el && wasNearBottomRef.current) {
      el.scrollTop = el.scrollHeight
    }
  }, [messages.length, thinking])

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 min-h-0 px-10 py-7 flex flex-col gap-4 overflow-y-auto"
    >
      {messages.length > 0 ? (
        <>
          {messages.map((m) => (
            <Message key={m.id} message={m} />
          ))}
          {thinking && <ThinkingIndicator />}
        </>
      ) : thinking ? (
        <ThinkingIndicator />
      ) : (
        <div className="flex flex-col gap-1.5 items-start">
          <span className="text-[11px] font-semibold text-text-tertiary pl-1">BRD-Agent</span>
          <div className="max-w-[74%] bg-white shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)] rounded-[20px] px-4.5 py-3.5 text-base leading-relaxed">
            {placeholderText}
          </div>
        </div>
      )}
    </div>
  )
}
