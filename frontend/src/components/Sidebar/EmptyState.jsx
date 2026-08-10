import Button from '../common/Button.jsx'

export default function EmptyState({
  onNewConversation,
  title = 'No conversations yet',
  description = 'Start your first BRD conversation and BRD-Agent will guide you section by section.',
  hideAction = false,
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-20 px-10 md:py-25">
      <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="#c1c1c1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <div className="text-[19px] font-bold mt-5">{title}</div>
      <div className="text-[15px] text-text-secondary mt-2 max-w-90 leading-relaxed">{description}</div>
      {!hideAction && (
        <Button variant="primary" className="mt-6" onClick={onNewConversation}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M12 5v14M5 12h14" />
          </svg>
          New Conversation
        </Button>
      )}
    </div>
  )
}
