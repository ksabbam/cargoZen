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
  { key: 'charge_code', label: 'Charge Code', width: '120px' },
  { key: 'charge_name', label: 'Charge Name' },
  { key: 'job_type', label: 'Job Type' },
  { key: 'transport_mode', label: 'Mode' },
  {
    key: 'amount', label: 'Amount',
    render: (v: unknown, row: Record<string, unknown>) =>
      `${row.currency || 'USD'} ${Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
  },
  {
    key: 'is_active', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} />
  },
]

const defaultForm = {
  charge_id: '', job_type: '', transport_mode: '',
  amount: '0', currency: 'USD', is_active: true,
}

export default function DefaultChargesPage() {
  const [page, setPage] = useState(1)
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['default-charges', page],
    queryFn: async () => {
      const res = await apiClient.get('/api/default-charges', { params: { page, limit: 20 } })
      return res.data
    },
  })

  // Fetch charges for dropdown
  const { data: chargesData } = useQuery({
    queryKey: ['charge-master-lookup'],
    queryFn: async () => {
      const res = await apiClient.get('/api/charge-master', { params: { limit: 100 } })
      return res.data?.data || []
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/default-charges/${editingItem.default_id}`, payload)
        : apiClient.post('/api/default-charges', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Updated!' : 'Default charge created!')
      queryClient.invalidateQueries({ queryKey: ['default-charges'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/default-charges/${id}`),
    onSuccess: () => {
      toast.success('Deactivated')
      queryClient.invalidateQueries({ queryKey: ['default-charges'] })
    },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Default Charges"
        subtitle="Preset charge amounts by job type and transport mode"
        onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }}
        newLabel="New Default Charge"
      />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns}
          data={data?.data || []}
          total={data?.total || 0}
          page={page}
          limit={20}
          onPageChange={setPage}
          onRefresh={() => refetch()}
          isLoading={isLoading}
          getRowKey={(row) => (row as Record<string, unknown>).default_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1">
                  <Edit2 size={15} />
                </button>
                <button
                  onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.default_id as number) }}
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
        title={editingItem ? 'Edit Default Charge' : 'New Default Charge'}
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
          <div className="col-span-2">
            <label className="label">Charge *</label>
            <select className="input" {...register('charge_id')}>
              <option value="">Select a charge...</option>
              {(chargesData as Array<Record<string, unknown>> || []).map((c) => (
                <option key={c.charge_id as number} value={c.charge_id as number}>
                  {c.charge_code as string} — {c.charge_name as string}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Job Type</label>
            <select className="input" {...register('job_type')}>
              <option value="">All</option>
              <option value="IMPORT">Import</option>
              <option value="EXPORT">Export</option>
            </select>
          </div>
          <div>
            <label className="label">Transport Mode</label>
            <select className="input" {...register('transport_mode')}>
              <option value="">All</option>
              <option value="AIR">Air</option>
              <option value="SEA">Sea</option>
              <option value="ROAD">Road</option>
            </select>
          </div>
          <div>
            <label className="label">Default Amount</label>
            <input className="input" type="number" step="0.01" {...register('amount')} />
          </div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
        </form>
      </Modal>
    </div>
  )
}
