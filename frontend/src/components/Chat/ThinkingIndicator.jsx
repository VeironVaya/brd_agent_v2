export default function ThinkingIndicator() {
  return (
    <div className="flex flex-col gap-1.5 items-start">
      <span className="text-[11px] font-semibold text-text-tertiary pl-1">BRD-Agent</span>
      <div className="max-w-[74%] bg-white shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)] rounded-[20px] px-4.5 py-4 flex items-center gap-1.25">
        <span className="w-1.75 h-1.75 rounded-full bg-text-tertiary/60 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-1.75 h-1.75 rounded-full bg-text-tertiary/60 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-1.75 h-1.75 rounded-full bg-text-tertiary/60 animate-bounce" />
      </div>
    </div>
  )
}
