import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'group_code', label: 'Code', sortable: true, width: '100px' },
  { key: 'group_name', label: 'Group Name', sortable: true },
  { key: 'group_type', label: 'Type' },
  { key: 'description', label: 'Description' },
  { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
]

const defaultForm = { group_code: '', group_name: '', group_type: '', description: '', is_active: true }

export default function OrgGroupsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['org-groups', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/org-groups', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/org-groups/${editingItem.group_id}`, payload)
        : apiClient.post('/api/org-groups', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Group updated!' : 'Group created!')
      queryClient.invalidateQueries({ queryKey: ['org-groups'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/org-groups/${id}`),
    onSuccess: () => { toast.success('Deactivated'); queryClient.invalidateQueries({ queryKey: ['org-groups'] }) },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Organization Groups" subtitle="Group organizations by type" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Group" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by code or name..."
          getRowKey={(row) => (row as Record<string, unknown>).group_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1"><Edit2 size={15} /></button>
                <button onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.group_id as number) }} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={15} /></button>
              </>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Group' : 'New Organization Group'}
        size="md"
        footer={
          <>
            <button className="btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSubmit((d) => saveMutation.mutate(d))} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving...' : 'Save'}
            </button>
          </>
        }
      >
        <form className="grid grid-cols-2 gap-4">
          <div><label className="label">Group Code *</label><input className="input" {...register('group_code')} placeholder="LOCAL" /></div>
          <div><label className="label">Group Name *</label><input className="input" {...register('group_name')} placeholder="Local Companies" /></div>
          <div>
            <label className="label">Group Type</label>
            <select className="input" {...register('group_type')}>
              <option value="">Select type</option>
              <option>DOMESTIC</option><option>INTERNATIONAL</option>
              <option>AGENT</option><option>FINANCIAL</option><option>GOVERNMENT</option>
            </select>
          </div>
          <div className="flex items-end pb-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" {...register('is_active')} className="rounded text-blue-600" />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>
          <div className="col-span-2"><label className="label">Description</label><textarea className="input" rows={2} {...register('description')} /></div>
        </form>
      </Modal>
    </div>
  )
}
