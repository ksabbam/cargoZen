import { useLocation } from 'react-router-dom'
import { Search, Bell } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useUIStore } from '@/store/uiStore'

const routeTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/administration/organizations': 'Organizations',
  '/administration/org-groups': 'Organization Groups',
  '/administration/airlines': 'Airlines',
  '/administration/shipping-lines': 'Shipping Lines',
  '/administration/accounts': 'Chart of Accounts',
  '/administration/charge-master': 'Charge Master',
  '/administration/default-charges': 'Default Charges',
  '/administration/business-dimensions': 'Business Dimensions',
  '/administration/commodities': 'Commodities',
  '/administration/vendor-contracts': 'Vendor Contracts',
  '/administration/custom-clearing': 'Custom Clearing',
  '/administration/system-settings': 'System Settings',
  '/transactions/import-jobs': 'Import Jobs',
  '/transactions/bank-payments': 'Bank Payments',
  '/transactions/bank-receipts': 'Bank Receipts',
  '/transactions/journal-entries': 'Journal Entries',
  '/transactions/debit-notes': 'General Debit Notes',
  '/transactions/purchase-bills': 'Purchase Bills',
  '/transactions/customs-export': 'Customs Export',
  '/reports': 'Reports',
  '/tools': 'Tools',
}

const sectionMap: Record<string, string> = {
  '/administration': 'Administration',
  '/transactions': 'Transactions',
}

export default function TopBar() {
  const { pathname } = useLocation()
  const { user } = useAuthStore()
  const { sidebarCollapsed } = useUIStore()

  const pageTitle = routeTitles[pathname] || 'CargoZen'
  const section = Object.entries(sectionMap).find(([k]) => pathname.startsWith(k))?.[1]

  return (
    <header className="h-14 bg-white border-b border-ios-gray5 flex items-center px-6 gap-4 shrink-0 sticky top-0 z-20">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 flex-1 min-w-0">
        {section && (
          <>
            <span className="text-xs text-ios-gray2 font-medium">{section}</span>
            <span className="text-ios-gray4 text-xs">/</span>
          </>
        )}
        <h1 className="text-sm font-semibold text-[#1C1C1E] truncate">{pageTitle}</h1>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-2">
        <button className="p-2 rounded-lg text-ios-gray2 hover:text-[#1C1C1E] hover:bg-ios-gray6 transition-all">
          <Search size={16} />
        </button>
        <button className="p-2 rounded-lg text-ios-gray2 hover:text-[#1C1C1E] hover:bg-ios-gray6 transition-all relative">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-ios-red rounded-full" />
        </button>
        <div className="flex items-center gap-2 pl-2 border-l border-ios-gray5">
          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-ios-blue to-ios-indigo flex items-center justify-center text-white text-2xs font-bold">
            {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
          </div>
          <span className="text-xs font-medium text-[#1C1C1E] hidden md:block">
            {user?.full_name?.split(' ')[0] || user?.username}
          </span>
        </div>
      </div>
    </header>
  )
}
