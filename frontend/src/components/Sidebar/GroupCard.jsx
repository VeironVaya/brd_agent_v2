export default function GroupCard({ group, onClick }) {
  const isShared = group.role !== 'owner'
  
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex flex-col bg-white border border-border rounded-xl p-5 text-left transition-all hover:border-text-primary hover:shadow-[0_4px_12px_rgba(0,0,0,0.05)] cursor-pointer w-full group relative overflow-hidden"
    >
      <div className="flex items-start justify-between mb-3 w-full gap-3">
        <div className="w-10 h-10 rounded-lg bg-bg-subtlest flex items-center justify-center flex-shrink-0 group-hover:bg-accent/10 group-hover:text-accent transition-colors text-text-secondary">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          </svg>
        </div>
        
        {isShared && (
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-accent/10 text-accent text-[11px] font-semibold flex-shrink-0">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <path d="M8.6 10.5l6.8-3.9M8.6 13.5l6.8 3.9" />
            </svg>
            {group.role === 'editor' ? 'Editor' : 'Viewer'}
          </div>
        )}
      </div>

      <div className="text-[15px] font-bold text-text-primary truncate w-full mb-1">
        {group.title}
      </div>
      
      {group.description && (
        <div className="text-[13px] text-text-secondary line-clamp-2 leading-relaxed mb-4 flex-grow">
          {group.description}
        </div>
      )}

      <div className="mt-auto pt-4 flex items-center gap-3 text-[12px] font-medium text-text-tertiary">
        <div className="flex items-center gap-1.5">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <path d="M14 2v6h6" />
            <path d="M16 13H8" />
            <path d="M16 17H8" />
            <path d="M10 9H8" />
          </svg>
          {group.brdCount ?? 0} BRD{(group.brdCount ?? 0) !== 1 ? 's' : ''}
        </div>
        
        {/* We can show member count if the group has collaborators, but we'll keep it simple for now */}
      </div>
    </button>
  )
}
