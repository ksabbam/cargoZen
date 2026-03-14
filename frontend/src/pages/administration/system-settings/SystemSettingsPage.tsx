import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, Settings } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import PageHeader from '@/components/common/PageHeader'

interface Setting {
  setting_id: number
  setting_key: string
  setting_value: unknown
  setting_group: string
  data_type: string
  description: string
  is_editable: boolean
}

const groupLabels: Record<string, { label: string; color: string }> = {
  GENERAL:      { label: 'General',       color: 'bg-ios-blue' },
  FINANCE:      { label: 'Finance',       color: 'bg-ios-green' },
  ADMIN:        { label: 'Administration',color: 'bg-ios-indigo' },
  SECURITY:     { label: 'Security',      color: 'bg-ios-red' },
  TRANSACTIONS: { label: 'Transactions',  color: 'bg-ios-orange' },
}

export default function SystemSettingsPage() {
  const [editValues, setEditValues] = useState<Record<string, string>>({})
  const queryClient = useQueryClient()

  const { data: settings, isLoading } = useQuery<Setting[]>({
    queryKey: ['system-settings'],
    queryFn: async () => {
      const res = await apiClient.get('/api/system-settings')
      return res.data
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: unknown }) =>
      apiClient.put(`/api/system-settings/${key}`, { value }),
    onSuccess: (_, vars) => {
      toast.success(`Setting "${vars.key}" saved!`)
      queryClient.invalidateQueries({ queryKey: ['system-settings'] })
      setEditValues((prev) => { const next = { ...prev }; delete next[vars.key]; return next })
    },
    onError: () => toast.error('Failed to update setting'),
  })

  const grouped = (settings || []).reduce<Record<string, Setting[]>>((acc, s) => {
    const group = s.setting_group || 'OTHER'
    if (!acc[group]) acc[group] = []
    acc[group].push(s)
    return acc
  }, {})

  const displayValue = (s: Setting) => {
    const v = s.setting_value
    if (v === null || v === undefined) return ''
    if (typeof v === 'object') return JSON.stringify(v)
    return String(v).replace(/^"|"$/g, '')
  }

  const handleChange = (key: string, value: string) => {
    setEditValues((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = (s: Setting) => {
    const raw = editValues[s.setting_key]
    let parsed: unknown = raw
    if (s.data_type === 'NUMBER') parsed = Number(raw)
    else if (s.data_type === 'BOOLEAN') parsed = raw === 'true'
    else if (s.data_type === 'JSON') { try { parsed = JSON.parse(raw) } catch {} }
    updateMutation.mutate({ key: s.setting_key, value: parsed })
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="System Settings" subtitle="Configure global application settings" />
      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-4xl mx-auto space-y-6">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card p-6 animate-pulse">
                  <div className="h-5 w-32 bg-ios-gray6 rounded mb-4" />
                  <div className="space-y-3">
                    <div className="h-10 bg-ios-gray6 rounded" />
                    <div className="h-10 bg-ios-gray6 rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            Object.entries(grouped).map(([group, items]) => {
              const meta = groupLabels[group] || { label: group, color: 'bg-ios-gray' }
              return (
                <div key={group} className="card overflow-hidden">
                  <div className="flex items-center gap-3 px-6 py-4 bg-[#FAFAFA] border-b border-ios-gray5">
                    <div className={`w-7 h-7 rounded-lg ${meta.color} flex items-center justify-center`}>
                      <Settings size={13} className="text-white" />
                    </div>
                    <h3 className="text-sm font-semibold text-[#1C1C1E]">{meta.label}</h3>
                    <span className="badge badge-gray ml-auto">{items.length}</span>
                  </div>
                  <div className="divide-y divide-ios-gray5">
                    {items.map((s) => {
                      const currentValue = editValues[s.setting_key] ?? displayValue(s)
                      const isDirty = s.setting_key in editValues
                      return (
                        <div key={s.setting_key} className="flex items-center gap-4 px-6 py-4">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-[#1C1C1E]">{s.setting_key}</p>
                            <p className="text-xs text-ios-gray mt-0.5">{s.description}</p>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            {s.data_type === 'BOOLEAN' ? (
                              <select
                                value={currentValue}
                                onChange={(e) => handleChange(s.setting_key, e.target.value)}
                                className="input py-1.5 text-sm w-24"
                                disabled={!s.is_editable}
                              >
                                <option value="true">Yes</option>
                                <option value="false">No</option>
                              </select>
                            ) : (
                              <input
                                value={currentValue}
                                onChange={(e) => handleChange(s.setting_key, e.target.value)}
                                className="input py-1.5 text-sm w-48"
                                type={s.data_type === 'NUMBER' ? 'number' : 'text'}
                                disabled={!s.is_editable}
                              />
                            )}
                            {isDirty && (
                              <button
                                onClick={() => handleSave(s)}
                                disabled={updateMutation.isPending}
                                className="btn-primary btn-sm"
                              >
                                <Save size={12} />
                              </button>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
