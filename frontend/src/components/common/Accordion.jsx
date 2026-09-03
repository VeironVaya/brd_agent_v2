import React, { useState, useRef, useEffect } from 'react'

export default function Accordion({ title, icon, defaultOpen = false, children, badge }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const contentRef = useRef(null)
  const [height, setHeight] = useState(defaultOpen ? 'auto' : 0)

  useEffect(() => {
    if (isOpen) {
      setHeight(contentRef.current.scrollHeight)
    } else {
      setHeight(0)
    }
  }, [isOpen, children])

  return (
    <div className="border border-border-light/60 rounded-xl overflow-hidden bg-white mb-4 shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-bg-subtle/30 hover:bg-bg-subtle transition-colors"
      >
        <div className="flex items-center gap-2.5">
          {icon}
          <span className="text-[11px] font-bold text-text-primary uppercase tracking-wide">{title}</span>
          {badge && (
            <span className="ml-2 px-2 py-0.5 text-[9px] font-bold bg-text-primary text-white rounded-full">
              {badge}
            </span>
          )}
        </div>
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={`text-text-tertiary transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      
      <div
        style={{ height }}
        className="transition-[height] duration-300 ease-in-out overflow-hidden"
      >
        <div ref={contentRef} className="p-4 pt-2 border-t border-border-light/40">
          {children}
        </div>
      </div>
    </div>
  )
}
