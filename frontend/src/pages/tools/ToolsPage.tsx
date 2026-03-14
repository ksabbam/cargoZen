import { useState } from 'react'
import {
  Download, Upload, History, Database, Users, Trash2,
  FileText, Shield, Globe, RefreshCw
} from 'lucide-react'
import PageHeader from '@/components/common/PageHeader'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'

interface ToolCard {
  label: string
  description: string
  icon: React.ElementType
  color: string
  action?: () => void
  disabled?: boolean
}

export default function ToolsPage() {
  const [processing, setProcessing] = useState<string | null>(null)

  const runDiagnostics = async () => {
    setProcessing('diagnostics')
    try {
      const res = await apiClient.get('/api/auth/health')
      const d = res.data
      const ok = d.snowflake_connection && d.database_exists && d.auth_schema && d.users_table
      toast.success(ok ? '✓ All systems healthy' : '⚠ Issues detected — check console', { duration: 5000 })
      console.table(d)
    } catch {
      toast.error('Cannot reach API server')
    } finally {
      setProcessing(null)
    }
  }

  const fixAdminPassword = async () => {
    setProcessing('fix-password')
    try {
      const res = await apiClient.post('/api/auth/fix-admin-password')
      toast.success(res.data.message || 'Admin password reset!')
    } catch {
      toast.error('Failed to reset admin password')
    } finally {
      setProcessing(null)
    }
  }

  const tools: ToolCard[][] = [
    [
      {
        label: 'Export Data',
        description: 'Download master data as JSON for backup or migration',
        icon: Download,
        color: 'bg-ios-blue',
        action: () => toast('Export feature coming soon', { icon: '📦' }),
      },
      {
        label: 'Import Data',
        description: 'Bulk import records from CSV or Excel templates',
        icon: Upload,
        color: 'bg-ios-green',
        action: () => toast('Import feature coming soon', { icon: '📥' }),
      },
      {
        label: 'Audit Trail',
        description: 'View system activity logs and change history',
        icon: History,
        color: 'bg-ios-indigo',
        action: () => toast('Audit trail feature coming soon', { icon: '📋' }),
      },
    ],
    [
      {
        label: 'System Health',
        description: 'Run diagnostics on Snowflake connection and schema',
        icon: Database,
        color: 'bg-ios-teal',
        action: runDiagnostics,
      },
      {
        label: 'User Management',
        description: 'Manage users, roles and permissions',
        icon: Users,
        color: 'bg-ios-purple',
        action: () => toast('User management feature coming soon', { icon: '👥' }),
      },
      {
        label: 'Reset Admin Password',
        description: "Reset the admin account password back to 'Admin@123'",
        icon: Shield,
        color: 'bg-ios-orange',
        action: fixAdminPassword,
      },
    ],
    [
      {
        label: 'Clear Cache',
        description: 'Clear application cache and refresh all data',
        icon: RefreshCw,
        color: 'bg-ios-red',
        action: () => {
          window.location.reload()
          toast.success('Cache cleared!')
        },
      },
      {
        label: 'API Documentation',
        description: 'View the interactive API docs (Swagger UI)',
        icon: FileText,
        color: 'bg-ios-gray',
        action: () => window.open('http://localhost:8000/api/docs', '_blank'),
      },
      {
        label: 'Environment Info',
        description: 'View current environment configuration',
        icon: Globe,
        color: 'bg-ios-pink',
        action: async () => {
          try {
            const res = await apiClient.get('/health')
            toast.success(`API Status: ${res.data.status}`, { duration: 3000 })
          } catch {
            toast.error('Cannot reach API')
          }
        },
      },
    ],
  ]

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Tools" subtitle="System utilities and maintenance tools" />
      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-5xl mx-auto space-y-6">
          {tools.map((row, ri) => (
            <div key={ri} className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {row.map((tool) => (
                <button
                  key={tool.label}
                  onClick={tool.action}
                  disabled={!!processing || tool.disabled}
                  className="card-hover p-6 text-left group cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className={`w-10 h-10 rounded-xl ${tool.color} flex items-center justify-center mb-4 shadow-sm`}>
                    <tool.icon
                      size={18}
                      className={`text-white ${processing === tool.label.toLowerCase().replace(/ /g, '-') ? 'spin' : ''}`}
                    />
                  </div>
                  <h3 className="font-semibold text-[#1C1C1E] mb-1 group-hover:text-ios-blue transition-colors">
                    {tool.label}
                  </h3>
                  <p className="text-xs text-ios-gray leading-relaxed">{tool.description}</p>
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
