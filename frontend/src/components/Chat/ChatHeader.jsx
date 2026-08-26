import { useNavigate } from 'react-router-dom'
import Logo from '../common/Logo.jsx'
import UserMenu from '../common/UserMenu.jsx'
import RoleBadge from '../common/RoleBadge.jsx'

export default function ChatHeader({
  conversation,
  aiModel,
  onToggleModel,
  flaggedCount,
  onOpenReview,
  onOpenShare,
  onLogout,
}) {
  const navigate = useNavigate()
  const isCloud = aiModel === 'Cloud'
  const generateReady = flaggedCount === 0
  const isOwner = conversation.role === 'owner'

  return (
    <div className="flex items-center justify-between gap-4 px-10 py-5 border-b border-divider flex-wrap">
      <div className="flex items-center gap-4 min-w-0">
        <Logo size={30} />
        <span className="w-px h-6.5 bg-border flex-shrink-0" />
        <button
          type="button"
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 text-sm cursor-pointer flex-shrink-0 whitespace-nowrap"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5" />
            <path d="m12 19-7-7 7-7" />
          </svg>
          BRDs
        </button>
        <span className="w-px h-5.5 bg-border flex-shrink-0" />
        <div className="text-[21px] font-bold whitespace-nowrap overflow-hidden text-ellipsis min-w-0">
          {conversation.title}
        </div>
        {!isOwner && <RoleBadge role={conversation.role} className="flex-shrink-0" />}
      </div>

      <div className="flex items-center gap-2.5 flex-shrink-0">
        <div className="flex items-center bg-bg-subtlest rounded-pill p-1 gap-0.5">
          {['Local', 'Cloud'].map((label) => (
            <button
              key={label}
              type="button"
              onClick={onToggleModel}
              className={`px-4 py-1.75 rounded-pill text-sm cursor-pointer ${
                (label === 'Cloud') === isCloud
                  ? 'font-semibold text-white bg-text-primary'
                  : 'font-medium text-text-secondary'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={onOpenReview}
          className="flex items-center gap-2 bg-white text-text-primary border border-text-primary rounded-btn h-11 px-4.5 text-sm font-medium cursor-pointer whitespace-nowrap"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 22V4" />
            <path d="M4 4h13l-2.5 4L17 12H4" />
          </svg>
          Review flagged ({flaggedCount})
        </button>

        {isOwner && (
          <button
            type="button"
            onClick={onOpenShare}
            className="flex items-center gap-2 bg-white text-text-primary border border-text-primary rounded-btn h-11 px-4.5 text-sm font-medium cursor-pointer whitespace-nowrap"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <path d="M8.6 10.5l6.8-3.9M8.6 13.5l6.8 3.9" />
            </svg>
            Share
          </button>
        )}

        {generateReady ? (
          <button
            type="button"
            onClick={() => navigate(`/conversations/${conversation.id}/export`)}
            className="bg-accent text-white border-none rounded-btn h-12 px-6 text-base font-medium cursor-pointer whitespace-nowrap"
          >
            View Draft
          </button>
        ) : (
          <button
            type="button"
            disabled
            title={`Resolve ${flaggedCount} flagged answers to view the draft`}
            className="bg-accent-tint text-white border-none rounded-btn h-12 px-6 text-base font-medium cursor-not-allowed whitespace-nowrap"
          >
            View Draft ({flaggedCount} flagged)
          </button>
        )}

        <UserMenu onLogout={onLogout} />
      </div>
    </div>
  )
}
