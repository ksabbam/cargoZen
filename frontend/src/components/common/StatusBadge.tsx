import clsx from 'clsx'

const map: Record<string, string> = {
  PENDING:     'badge-orange',
  APPROVED:    'badge-green',
  REJECTED:    'badge-red',
  OPEN:        'badge-blue',
  DRAFT:       'badge-gray',
  POSTED:      'badge-green',
  IN_PROGRESS: 'badge-blue',
  COMPLETED:   'badge-green',
  CANCELLED:   'badge-red',
  ACTIVE:      'badge-green',
  INACTIVE:    'badge-gray',
  EXPIRED:     'badge-red',
  CLOSED:      'badge-gray',
  PAID:        'badge-green',
  SUBMITTED:   'badge-blue',
  CLEARED:     'badge-green',
}

export default function StatusBadge({ status }: { status: string }) {
  const cls = map[status?.toUpperCase()] || 'badge-gray'
  return <span className={clsx('badge', cls)}>{status}</span>
}