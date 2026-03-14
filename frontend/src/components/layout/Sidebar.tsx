import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Building2, Plane, Ship, DollarSign, Package,
  FileText, Settings, ChevronDown, ChevronRight, LogOut,
  Briefcase, Receipt, BookOpen, CreditCard, FileBarChart,
  Wrench, Users, Layers, Tag, Star, Anchor, ChevronLeft, ChevronRight as CR,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useUIStore } from '@/store/uiStore'
import apiClient from '@/api/client'
import clsx from 'clsx'

interface NavItem {
  label: string
  icon?: React.ElementType
  path?: string
  color?: string
  children?: NavItem[]
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/', color: 'bg-ios-blue' },
  {
    label: 'Administration', icon: Settings, color: 'bg-ios-indigo',
    children: [
      { label: 'Organizations',      icon: Building2,  path: '/administration/organizations',       color: 'bg-ios-blue' },
      { label: 'Org Groups',         icon: Users,      path: '/administration/org-groups',          color: 'bg-ios-indigo' },
      { label: 'Airlines',           icon: Plane,      path: '/administration/airlines',             color: 'bg-ios-teal' },
      { label: 'Shipping Lines',     icon: Ship,       path: '/administration/shipping-lines',       color: 'bg-ios-orange' },
      { label: 'Chart of Accounts',  icon: BookOpen,   path: '/administration/accounts',             color: 'bg-ios-green' },
      { label: 'Charge Master',      icon: Tag,        path: '/administration/charge-master',        color: 'bg-ios-purple' },
      { label: 'Default Charges',    icon: Star,       path: '/administration/default-charges',      color: 'bg-ios-yellow' },
      { label: 'Biz Dimensions',     icon: Layers,     path: '/administration/business-dimensions',  color: 'bg-ios-pink' },
      { label: 'Commodities',        icon: Package,    path: '/administration/commodities',           color: 'bg-ios-orange' },
      { label: 'Vendor Contracts',   icon: FileText,   path: '/administration/vendor-contracts',     color: 'bg-ios-teal' },
      { label: 'Custom Clearing',    icon: Anchor,     path: '/administration/custom-clearing',      color: 'bg-ios-red' },
      { label: 'System Settings',    icon: Settings,   path: '/administration/system-settings',      color: 'bg-ios-gray' },
    ],
  },
  {
    label: 'Transactions', icon: DollarSign, color: 'bg-ios-green',
    children: [
      { label: 'Import Jobs',        icon: Briefcase,   path: '/transactions/import-jobs',     color: 'bg-ios-blue' },
      { label: 'Bank Payments',      icon: CreditCard,  path: '/transactions/bank-payments',   color: 'bg-ios-red' },
      { label: 'Bank Receipts',      icon: Receipt,     path: '/transactions/bank-receipts',   color: 'bg-ios-green' },
      { label: 'Journal Entries',    icon: BookOpen,    path: '/transactions/journal-entries', color: 'bg-ios-indigo' },
      { label: 'Debit Notes',        icon: FileText,    path: '/transactions/debit-notes',     color: 'bg-ios-orange' },
      { label: 'Purchase Bills',     icon: FileText,    path: '/transactions/purchase-bills',  color: 'bg-ios-purple' },
      { label: 'Customs Export',     icon: Plane,       path: '/transactions/customs-export',  color: 'bg-ios-teal' },
    ],
  },
  { label: 'Reports', icon: FileBarChart, path: '/reports', color: 'bg-ios-pink' },
  { label: 'Tools',   icon: Wrench,       path: '/tools',   color: 'bg-ios-gray' },
]

function NavLeaf({ item, depth = 0 }: { item: NavItem; depth?: number }) {
  const location = useLocation()
  const isActive = location.pathname === item.path
  const { sidebarCollapsed } = useUIStore()

  return (
    <Link
      to={item.path!}
      title={sidebarCollapsed ? item.label : undefined}
      className={clsx(
        'group flex items-center gap-3 rounded-lg transition-all duration-150 select-none',
        depth === 0 ? 'px-3 py-2.5' : 'px-3 py-2',
        isActive
          ? 'bg-ios-blue text-white shadow-sm'
          : 'text-[#1C1C1E] hover:bg-ios-gray6'
      )}
    >
      <span className={clsx(
        'flex items-center justify-center rounded-lg shrink-0 transition-all',
        depth === 0 ? 'w-7 h-7' : 'w-5 h-5',
        isActive ? 'bg-white/20' : item.color,
      )}>
        {item.icon && (
          <item.icon
            size={depth === 0 ? 15 : 11}
            className={isActive ? 'text-white' : 'text-white'}
          />
        )}
      </span>
      {!sidebarCollapsed && (
        <span className={clsx(
          'font-medium truncate',
          depth === 0 ? 'text-sm' : 'text-xs',
          isActive ? 'text-white' : 'text-[#1C1C1E]'
        )}>
          {item.label}
        </span>
      )}
    </Link>
  )
}

function NavGroup({ item }: { item: NavItem }) {
  const location = useLocation()
  const { sidebarCollapsed } = useUIStore()
  const isChildActive = item.children?.some(c => location.pathname.startsWith(c.path || '___'))
  const [open, setOpen] = useState(isChildActive || false)

  if (!item.children) return <NavLeaf item={item} />

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        title={sidebarCollapsed ? item.label : undefined}
        className={clsx(
          'w-full flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all duration-150 select-none',
          isChildActive ? 'bg-blue-50 text-ios-blue' : 'text-[#1C1C1E] hover:bg-ios-gray6'
        )}
      >
        <span className={clsx(
          'w-7 h-7 flex items-center justify-center rounded-lg shrink-0',
          item.color
        )}>
          {item.icon && <item.icon size={15} className="text-white" />}
        </span>
        {!sidebarCollapsed && (
          <>
            <span className={clsx(
              'flex-1 text-left text-sm font-medium truncate',
              isChildActive ? 'text-ios-blue' : ''
            )}>
              {item.label}
            </span>
            <span className="text-ios-gray3">
              {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </span>
          </>
        )}
      </button>

      {open && !sidebarCollapsed && (
        <div className="ml-5 pl-3 mt-1 border-l border-ios-gray5 space-y-0.5 pb-1">
          {item.children.map(child => (
            <NavLeaf key={child.label} item={child} depth={1} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const { user, logout, access_token } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try { await apiClient.post('/api/auth/logout', { access_token }) } catch (_) {}
    logout()
    navigate('/login')
  }

  return (
    <aside className={clsx(
      'fixed inset-y-0 left-0 flex flex-col bg-white border-r border-ios-gray5 z-30',
      'transition-all duration-300 ease-ios-ease',
      sidebarCollapsed ? 'w-[68px]' : 'w-[242px]'
    )}>
      {/* Logo */}
      <div className="flex items-center gap-3 h-14 px-4 border-b border-ios-gray5 shrink-0">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-ios-blue to-[#0055D0] flex items-center justify-center shadow-sm shrink-0">
          <Ship size={16} className="text-white" />
        </div>
        {!sidebarCollapsed && (
          <div className="min-w-0">
            <p className="text-sm font-bold text-[#1C1C1E] leading-tight">CargoZen</p>
            <p className="text-2xs text-ios-gray leading-tight">Freight Management</p>
          </div>
        )}
        <button
          onClick={toggleSidebar}
          className="ml-auto p-1 rounded-lg text-ios-gray2 hover:text-ios-gray hover:bg-ios-gray6 transition-colors"
        >
          {sidebarCollapsed ? <CR size={15} /> : <ChevronLeft size={15} />}
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        {navItems.map(item => (
          <NavGroup key={item.label} item={item} />
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-ios-gray5 p-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-ios-blue to-ios-indigo flex items-center justify-center text-white text-xs font-bold shrink-0">
            {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
          </div>
          {!sidebarCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-[#1C1C1E] truncate">
                {user?.full_name || user?.username}
              </p>
              <p className="text-2xs text-ios-gray truncate">{user?.role_name}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="p-1.5 rounded-lg text-ios-gray2 hover:text-ios-red hover:bg-red-50 transition-all"
            title="Sign out"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  )
}