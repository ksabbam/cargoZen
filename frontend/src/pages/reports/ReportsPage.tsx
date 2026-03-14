import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart3, FileText, TrendingUp, DollarSign, Download } from 'lucide-react'
import apiClient from '@/api/client'
import StatusBadge from '@/components/common/StatusBadge'

type ReportType = 'import-jobs-report' | 'financial-report' | 'ar-aging'

interface ReportConfig {
  id: ReportType
  title: string
  description: string
  icon: React.ElementType
  color: string
}

const reports: ReportConfig[] = [
  {
    id: 'import-jobs-report',
    title: 'Import Jobs Report',
    description: 'View all import jobs with status and details',
    icon: FileText,
    color: 'bg-blue-50 border-blue-200 text-blue-700',
  },
  {
    id: 'financial-report',
    title: 'Financial Ledger',
    description: 'Summarized debit/credit by account',
    icon: TrendingUp,
    color: 'bg-green-50 border-green-200 text-green-700',
  },
  {
    id: 'ar-aging',
    title: 'AP Aging Report',
    description: 'Outstanding purchase bills by vendor',
    icon: DollarSign,
    color: 'bg-orange-50 border-orange-200 text-orange-700',
  },
]

export default function ReportsPage() {
  const [activeReport, setActiveReport] = useState<ReportType | null>(null)
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['report', activeReport, dateFrom, dateTo],
    queryFn: async () => {
      if (!activeReport) return null
      const params: Record<string, string> = {}
      if (dateFrom) params.date_from = dateFrom
      if (dateTo) params.date_to = dateTo
      const res = await apiClient.get(`/api/reports/${activeReport}`, { params })
      return res.data
    },
    enabled: !!activeReport,
  })

  const reportData = data?.data || []

  const getColumns = (reportId: ReportType) => {
    if (reportId === 'import-jobs-report') {
      return ['job_no', 'job_date', 'transport_mode', 'bl_no', 'shipper', 'consignee', 'pol', 'pod', 'eta', 'gross_weight', 'status']
    }
    if (reportId === 'financial-report') {
      return ['account_code', 'account_name', 'total_debit', 'total_credit']
    }
    if (reportId === 'ar-aging') {
      return ['org_code', 'customer', 'bill_count', 'total_amount']
    }
    return []
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-6 py-4 bg-white border-b border-gray-200">
        <BarChart3 size={20} className="text-blue-600" />
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Reports</h1>
          <p className="text-sm text-gray-500">Generate and export operational reports</p>
        </div>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        {/* Report Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {reports.map((r) => (
            <button
              key={r.id}
              onClick={() => setActiveReport(r.id)}
              className={`card p-5 text-left hover:shadow-md transition-all border-2 ${
                activeReport === r.id ? 'border-blue-500 bg-blue-50' : 'border-transparent hover:border-gray-300'
              }`}
            >
              <div className={`inline-flex items-center justify-center p-2 rounded-lg mb-3 ${r.color}`}>
                <r.icon size={20} />
              </div>
              <h3 className="font-semibold text-gray-800">{r.title}</h3>
              <p className="text-sm text-gray-500 mt-1">{r.description}</p>
            </button>
          ))}
        </div>

        {activeReport && (
          <div className="card">
            {/* Filters */}
            <div className="flex items-center gap-4 p-4 border-b border-gray-100 flex-wrap">
              <h3 className="font-semibold text-gray-800 flex-1">
                {reports.find((r) => r.id === activeReport)?.title}
              </h3>
              {activeReport !== 'ar-aging' && (
                <>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600">From:</label>
                    <input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="input py-1.5 text-sm" />
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-sm text-gray-600">To:</label>
                    <input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="input py-1.5 text-sm" />
                  </div>
                </>
              )}
              <button onClick={() => refetch()} className="btn-primary btn-sm">
                Generate
              </button>
              {reportData.length > 0 && (
                <button className="btn-secondary btn-sm">
                  <Download size={13} /> Export
                </button>
              )}
            </div>

            {/* Report Table */}
            <div className="overflow-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-12 text-gray-400">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Generating report...
                </div>
              ) : reportData.length === 0 ? (
                <div className="py-12 text-center text-gray-400">No data available. Select filters and click Generate.</div>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {getColumns(activeReport).map((col) => (
                        <th key={col} className="table-header capitalize">{col.replace(/_/g, ' ')}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {reportData.map((row: Record<string, unknown>, idx: number) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        {getColumns(activeReport).map((col) => (
                          <td key={col} className="table-cell">
                            {col === 'status' ? (
                              <StatusBadge status={row[col] as string} />
                            ) : typeof row[col] === 'number' ? (
                              Number(row[col]).toLocaleString('en-US', { minimumFractionDigits: 2 })
                            ) : (
                              String(row[col] ?? '-')
                            )}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
