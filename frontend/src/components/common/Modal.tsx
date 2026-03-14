import { useEffect, useRef } from 'react'
import { X } from 'lucide-react'
import clsx from 'clsx'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  subtitle?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  footer?: React.ReactNode
}

const sizes = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-2xl', xl: 'max-w-4xl', full: 'max-w-7xl' }

export default function Modal({ isOpen, onClose, title, subtitle, children, size = 'lg', footer }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isOpen])

  useEffect(() => {
    const fn = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    if (isOpen) document.addEventListener('keydown', fn)
    return () => document.removeEventListener('keydown', fn)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div
      ref={overlayRef}
      onClick={e => e.target === overlayRef.current && onClose()}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.35)', backdropFilter: 'blur(4px)' }}
    >
      <div className={clsx(
        'bg-white rounded-2xl shadow-xl flex flex-col w-full max-h-[90vh]',
        'animate-[modalIn_0.18s_ease-out]',
        sizes[size]
      )}
        style={{ animation: 'modalIn 0.18s cubic-bezier(0.34,1.56,0.64,1)' }}
      >
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-5 border-b border-ios-gray5 shrink-0">
          <div>
            <h2 className="text-base font-semibold text-[#1C1C1E]">{title}</h2>
            {subtitle && <p className="text-xs text-ios-gray mt-0.5">{subtitle}</p>}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-ios-gray2 hover:text-[#1C1C1E] hover:bg-ios-gray6 transition-all -mt-0.5"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="flex items-center gap-3 px-6 py-4 border-t border-ios-gray5 bg-[#FAFAFA] rounded-b-2xl shrink-0">
            {footer}
          </div>
        )}
      </div>

      <style>{`
        @keyframes modalIn {
          from { opacity:0; transform: scale(0.95) translateY(8px); }
          to   { opacity:1; transform: scale(1)    translateY(0); }
        }
      `}</style>
    </div>
  )
}