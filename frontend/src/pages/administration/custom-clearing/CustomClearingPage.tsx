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
  { key: 'clearing_type', label: 'Type', width: '100px',
    render: (v: unknown) => (
      <span className={`badge ${v === 'IMPORT' ? 'badge-blue' : 'badge-orange'}`}>{v as string}</span>
    )
  },
  { key: 'port_code', label: 'Port Code', sortable: true, width: '100px' },
  { key: 'port_name', label: 'Port Name', sortable: true },
  { key: 'customs_authority', label: 'Customs Authority' },
  {
    key: 'is_active', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} />
  },
]

const defaultForm = {
  clearing_type: 'IMPORT', port_code: '', port_name: '',
  customs_authority: '', is_active: true,
}

export default function CustomClearingPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['custom-clearing', page, search, typeFilter],
    queryFn: async () => {
      const res = await apiClient.get('/api/custom-clearing', {
        params: { page, limit: 20, search: search || undefined, clearing_type: typeFilter || undefined }
      })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/custom-clearing/${editingItem.setup_id}`, payload)
        : apiClient.post('/api/custom-clearing', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Updated!' : 'Custom clearing setup created!')
      queryClient.invalidateQueries({ queryKey: ['custom-clearing'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/custom-clearing/${id}`),
    onSuccess: () => {
      toast.success('Deactivated')
      queryClient.invalidateQueries({ queryKey: ['custom-clearing'] })
    },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Custom Clearing Setup"
        subtitle="Configure import and export customs clearing procedures"
        onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }}
        newLabel="New Setup"
        actions={
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input py-1.5 text-sm w-32"
          >
            <option value="">All Types</option>
            <option value="IMPORT">Import</option>
            <option value="EXPORT">Export</option>
          </select>
        }
      />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns}
          data={data?.data || []}
          total={data?.total || 0}
          page={page}
          limit={20}
          onPageChange={setPage}
          onSearch={setSearch}
          onRefresh={() => refetch()}
          isLoading={isLoading}
          searchPlaceholder="Search by port code, name, authority..."
          getRowKey={(row) => (row as Record<string, unknown>).setup_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1">
                  <Edit2 size={15} />
                </button>
                <button
                  onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.setup_id as number) }}
                  className="text-red-400 hover:text-red-600 p-1"
                >
                  <Trash2 size={15} />
                </button>
              </>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Custom Clearing Setup' : 'New Custom Clearing Setup'}
        size="lg"
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
          <div>
            <label className="label">Clearing Type *</label>
            <select className="input" {...register('clearing_type')}>
              <option value="IMPORT">Import</option>
              <option value="EXPORT">Export</option>
            </select>
          </div>
          <div>
            <label className="label">Port Code *</label>
            <input className="input" {...register('port_code')} placeholder="AEDXB" />
          </div>
          <div>
            <label className="label">Port Name *</label>
            <input className="input" {...register('port_name')} placeholder="Jebel Ali, Dubai" />
          </div>
          <div>
            <label className="label">Customs Authority</label>
            <input className="input" {...register('customs_authority')} placeholder="Dubai Customs" />
          </div>
          <div className="col-span-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" {...register('is_active')} className="rounded text-blue-600" />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>
        </form>
      </Modal>
    </div>
  )
}
