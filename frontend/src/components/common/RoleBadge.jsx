export const ROLE_LABEL = {
  owner: 'Owner',
  editor: 'Editor',
  viewer: 'Viewer',
}

export default function RoleBadge({ role, className = '' }) {
  const isOwner = role === 'owner'
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.75 rounded-pill text-[11px] font-bold uppercase tracking-wide whitespace-nowrap ${
        isOwner ? 'bg-accent-tint text-accent-hover' : 'bg-bg-subtlest text-text-secondary'
      } ${className}`}
    >
      {ROLE_LABEL[role] || role}
    </span>
  )
}
