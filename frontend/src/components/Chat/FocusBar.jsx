export default function FocusBar({ focusedLabel, roomTab, onChangeRoomTab, onOpenChoices }) {
  return (
    <div className="px-10 py-5 flex items-center justify-between gap-4 flex-wrap border-b border-divider">
      <span className="inline-flex items-center gap-2 bg-white rounded-pill py-2 pl-3 pr-4 text-[13px] font-semibold shadow-[0_0_0_1px_rgba(0,0,0,.02),0_2px_6px_rgba(0,0,0,.04),0_4px_8px_rgba(0,0,0,.1)]">
        <span className="w-2 h-2 rounded-full bg-accent inline-block flex-shrink-0" />
        Currently discussing: {focusedLabel}
      </span>
      <div className="flex items-center gap-2">
        {onOpenChoices && (
          <button
            type="button"
            onClick={onOpenChoices}
            className="px-3.5 py-2 rounded-btn text-[13px] font-semibold cursor-pointer text-white bg-accent hover:bg-accent-hover"
          >
            Choose options
          </button>
        )}
        <div className="flex items-center bg-white rounded-pill p-1 gap-0.5 shadow-[0_1px_2px_rgba(0,0,0,.05),0_1px_1px_rgba(0,0,0,.03)]">
        {[
          ['question', 'This question'],
          ['general', 'General chat'],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => onChangeRoomTab(value)}
            className={`px-3.5 py-1.5 rounded-pill text-[13px] cursor-pointer ${
              roomTab === value
                ? 'font-semibold text-white bg-text-primary'
                : 'font-medium text-text-secondary'
            }`}
          >
            {label}
          </button>
        ))}
        </div>
      </div>
    </div>
  )
}
