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
  { key: 'line_code', label: 'Code', sortable: true, width: '100px' },
  { key: 'scac_code', label: 'SCAC', width: '80px' },
  { key: 'line_name', label: 'Line Name', sortable: true },
  { key: 'country', label: 'Country' },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email' },
  { key: 'website', label: 'Website' },
  { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
]

const defaultForm = {
  line_code: '', scac_code: '', line_name: '', country: '',
  headquarters: '', phone: '', email: '', website: '', is_active: true,
}

export default function ShippingLinesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['shipping-lines', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/shipping-lines', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/shipping-lines/${editingItem.line_id}`, payload)
        : apiClient.post('/api/shipping-lines', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Shipping line updated!' : 'Shipping line created!')
      queryClient.invalidateQueries({ queryKey: ['shipping-lines'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/shipping-lines/${id}`),
    onSuccess: () => { toast.success('Deactivated'); queryClient.invalidateQueries({ queryKey: ['shipping-lines'] }) },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Shipping Lines" subtitle="Ocean carrier master data" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Shipping Line" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by code or name..."
          getRowKey={(row) => (row as Record<string, unknown>).line_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1"><Edit2 size={15} /></button>
                <button onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.line_id as number) }} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={15} /></button>
              </>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Shipping Line' : 'New Shipping Line'}
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
          <div><label className="label">Line Code *</label><input className="input" {...register('line_code')} placeholder="MAERSK" /></div>
          <div><label className="label">Line Name *</label><input className="input" {...register('line_name')} placeholder="Maersk Line" /></div>
          <div><label className="label">SCAC Code</label><input className="input" {...register('scac_code')} placeholder="MAEU" /></div>
          <div><label className="label">Country</label><input className="input" {...register('country')} placeholder="Denmark" /></div>
          <div><label className="label">Headquarters</label><input className="input" {...register('headquarters')} /></div>
          <div><label className="label">Phone</label><input className="input" {...register('phone')} /></div>
          <div><label className="label">Email</label><input className="input" type="email" {...register('email')} /></div>
          <div><label className="label">Website</label><input className="input" {...register('website')} /></div>
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
