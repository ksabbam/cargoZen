import { Plus, ArrowLeft } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface PageHeaderProps {
  title?: string
  subtitle?: string
  onNew?: () => void
  newLabel?: string
  actions?: React.ReactNode
  backPath?: string
}

export default function PageHeader({
  title,
  subtitle,
  onNew,
  newLabel = 'New',
  actions,
  backPath,
}: PageHeaderProps) {
  const navigate = useNavigate()
  return (
    <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-ios-gray5 sticky top-14 z-10">
      <div className="flex items-center gap-3">
        {backPath && (
          <button
            onClick={() => navigate(backPath)}
            className="p-1.5 rounded-lg text-ios-gray2 hover:text-[#1C1C1E] hover:bg-ios-gray6 transition-all"
          >
            <ArrowLeft size={16} />
          </button>
        )}
        {(title || subtitle) && (
          <div>
            {title && <h2 className="text-sm font-semibold text-[#1C1C1E]">{title}</h2>}
            {subtitle && <p className="text-xs text-ios-gray mt-0.5">{subtitle}</p>}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2">
        {actions}
        {onNew && (
          <button onClick={onNew} className="btn-primary shadow-sm">
            <Plus size={15} /> {newLabel}
          </button>
        )}
      </div>
    </div>
  )
}