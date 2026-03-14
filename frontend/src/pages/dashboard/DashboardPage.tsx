import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Briefcase, Building2, CreditCard, Receipt, Clock, TrendingUp, ArrowRight
} from 'lucide-react'
import apiClient from '@/api/client'
import { useAuthStore } from '@/store/authStore'
import StatusBadge from '@/components/common/StatusBadge'

interface DashboardData {
  active_import_jobs: number
  todays_payments: number
  todays_receipts: number
  pending_approvals: number
  total_organizations: number
  jobs_by_mode: Array<{ transport_mode: string; cnt: number }>
  recent_jobs: Array<{
    job_no: string
    job_date: string
    transport_mode: string
    status: string
    shipper_name: string
  }>
}

const kpiCards = [
  { key: 'active_import_jobs',  label: 'Active Jobs',         icon: Briefcase,  from: '#007AFF', to: '#0055D0', path: '/transactions/import-jobs',    format: 'number' },
  { key: 'todays_payments',     label: "Today's Payments",    icon: CreditCard, from: '#FF3B30', to: '#C0392B', path: '/transactions/bank-payments',   format: 'currency' },
  { key: 'todays_receipts',     label: "Today's Receipts",    icon: Receipt,    from: '#34C759', to: '#27AE60', path: '/transactions/bank-receipts',   format: 'currency' },
  { key: 'pending_approvals',   label: 'Pending Approvals',   icon: Clock,      from: '#FF9500', to: '#E67E22', path: '/administration/organizations', format: 'number' },
  { key: 'total_organizations', label: 'Organizations',       icon: Building2,  from: '#AF52DE', to: '#8E44AD', path: '/administration/organizations', format: 'number' },
]

const quickActions = [
  { label: 'New Import Job',   path: '/transactions/import-jobs',    from: '#007AFF', to: '#0055D0' },
  { label: 'Bank Payment',     path: '/transactions/bank-payments',  from: '#FF3B30', to: '#C0392B' },
  { label: 'Bank Receipt',     path: '/transactions/bank-receipts',  from: '#34C759', to: '#27AE60' },
  { label: 'Journal Entry',    path: '/transactions/journal-entries',from: '#5856D6', to: '#4A3FC7' },
  { label: 'Purchase Bill',    path: '/transactions/purchase-bills', from: '#AF52DE', to: '#8E44AD' },
  { label: 'Customs Export',   path: '/transactions/customs-export', from: '#30B0C7', to: '#1A8FA0' },
]

const modeColors: Record<string, string> = {
  SEA: '#007AFF', AIR: '#30B0C7', ROAD: '#FF9500',
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard-summary'],
    queryFn: async () => {
      const res = await apiClient.get('/api/reports/dashboard-summary')
      return res.data
    },
    refetchInterval: 60_000,
  })

  const fmt = (v: number, f: string) =>
    f === 'currency'
      ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v)
      : v.toLocaleString()

  const maxCnt = Math.max(...(data?.jobs_by_mode?.map(j => j.cnt) || [1]))

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">

      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-[#1C1C1E]">
          {new Date().getHours() < 12 ? 'Good morning' : 'Good afternoon'},{' '}
          <span style={{ backgroundImage: 'linear-gradient(90deg,#007AFF,#5856D6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            {user?.full_name?.split(' ')[0] || user?.username}
          </span>
        </h1>
        <p className="text-sm text-ios-gray mt-1">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {kpiCards.map(card => {
          const val = isLoading ? null : (data as unknown as Record<string, unknown>)?.[card.key] as number ?? 0
          return (
            <button
              key={card.key}
              onClick={() => navigate(card.path)}
              className="card-hover p-5 text-left group cursor-pointer"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-sm"
                     style={{ background: `linear-gradient(135deg,${card.from},${card.to})` }}>
                  <card.icon size={18} className="text-white" />
                </div>
                <ArrowRight size={14} className="text-ios-gray4 group-hover:text-ios-blue group-hover:translate-x-0.5 transition-all mt-1" />
              </div>
              <p className="text-2xs text-ios-gray font-semibold uppercase tracking-wide mb-1">{card.label}</p>
              {isLoading ? (
                <div className="h-7 w-20 bg-ios-gray6 rounded animate-pulse" />
              ) : (
                <p className="text-2xl font-bold text-[#1C1C1E]">{fmt(val!, card.format)}</p>
              )}
            </button>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Recent Jobs */}
        <div className="card p-0 lg:col-span-2 overflow-hidden">
          <div className="flex items-center justify-between px-5 py-4 border-b border-ios-gray5">
            <div className="flex items-center gap-2">
              <TrendingUp size={16} className="text-ios-blue" />
              <h3 className="font-semibold text-sm text-[#1C1C1E]">Recent Import Jobs</h3>
            </div>
            <button onClick={() => navigate('/transactions/import-jobs')}
                    className="text-xs text-ios-blue font-medium hover:underline flex items-center gap-1">
              View all <ArrowRight size={12} />
            </button>
          </div>
          <div className="divide-y divide-ios-gray5">
            {isLoading ? (
              Array(5).fill(0).map((_, i) => (
                <div key={i} className="flex items-center gap-4 px-5 py-3">
                  <div className="h-4 bg-ios-gray6 rounded w-24 animate-pulse" />
                  <div className="h-4 bg-ios-gray6 rounded flex-1 animate-pulse" />
                  <div className="h-5 bg-ios-gray6 rounded w-16 animate-pulse" />
                </div>
              ))
            ) : data?.recent_jobs?.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-ios-gray2">
                <Briefcase size={32} className="mb-2 opacity-30" />
                <p className="text-sm">No import jobs yet</p>
              </div>
            ) : (
              data?.recent_jobs?.map(job => (
                <div key={job.job_no} className="flex items-center gap-4 px-5 py-3 hover:bg-ios-gray6 transition-colors cursor-pointer"
                     onClick={() => navigate('/transactions/import-jobs')}>
                  <div className="w-2 h-2 rounded-full shrink-0" style={{ background: modeColors[job.transport_mode] || '#8E8E93' }} />
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-semibold text-[#1C1C1E]">{job.job_no}</span>
                    <span className="text-xs text-ios-gray ml-2 truncate">{job.shipper_name}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-2xs text-ios-gray2">{job.job_date}</span>
                    <span className="text-2xs font-medium px-1.5 py-0.5 rounded-md"
                          style={{ background: `${modeColors[job.transport_mode] || '#8E8E93'}18`,
                                   color: modeColors[job.transport_mode] || '#8E8E93' }}>
                      {job.transport_mode}
                    </span>
                    <StatusBadge status={job.status} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-4">
          {/* Jobs by Mode */}
          <div className="card p-5">
            <h3 className="font-semibold text-sm text-[#1C1C1E] mb-4">Jobs by Mode</h3>
            {isLoading ? (
              <div className="space-y-3">{Array(3).fill(0).map((_, i) => (
                <div key={i} className="h-6 bg-ios-gray6 rounded animate-pulse" />
              ))}</div>
            ) : data?.jobs_by_mode?.length === 0 ? (
              <p className="text-xs text-ios-gray2 text-center py-4">No data</p>
            ) : (
              <div className="space-y-3">
                {data?.jobs_by_mode?.map(item => (
                  <div key={item.transport_mode}>
                    <div className="flex justify-between mb-1">
                      <span className="text-xs font-medium text-[#1C1C1E]">{item.transport_mode || 'N/A'}</span>
                      <span className="text-xs text-ios-gray">{item.cnt}</span>
                    </div>
                    <div className="h-1.5 rounded-full bg-ios-gray6 overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-500"
                           style={{ width: `${(item.cnt / maxCnt) * 100}%`, background: modeColors[item.transport_mode] || '#8E8E93' }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="card p-5">
            <h3 className="font-semibold text-sm text-[#1C1C1E] mb-3">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-2">
              {quickActions.map(a => (
                <button key={a.label} onClick={() => navigate(a.path)}
                        className="flex items-center gap-2 p-2.5 rounded-xl hover:opacity-90 active:scale-95 transition-all text-left"
                        style={{ background: `linear-gradient(135deg,${a.from}15,${a.to}10)` }}>
                  <div className="w-5 h-5 rounded-lg shrink-0"
                       style={{ background: `linear-gradient(135deg,${a.from},${a.to})` }} />
                  <span className="text-2xs font-semibold text-[#1C1C1E] leading-tight">{a.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}