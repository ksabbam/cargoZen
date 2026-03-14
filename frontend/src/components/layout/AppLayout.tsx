import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopBar from './TopBar'
import { useUIStore } from '@/store/uiStore'
import clsx from 'clsx'

export default function AppLayout() {
  const { sidebarCollapsed } = useUIStore()
  return (
    <div className="flex h-screen bg-ios-bg overflow-hidden">
      <Sidebar />
      <div
        className={clsx(
          'flex flex-col flex-1 overflow-hidden transition-all duration-300 ease-ios-ease',
          sidebarCollapsed ? 'ml-[68px]' : 'ml-[242px]'
        )}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          <div className="page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}