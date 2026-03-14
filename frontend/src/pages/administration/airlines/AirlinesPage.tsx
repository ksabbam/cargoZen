import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { Airline } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'airline_code', label: 'Code', sortable: true, width: '80px' },
  { key: 'iata_code', label: 'IATA', width: '70px' },
  { key: 'airline_name', label: 'Name', sortable: true },
  { key: 'country', label: 'Country' },
  { key: 'alliance', label: 'Alliance' },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email' },
  {
    key: 'is_active', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} />
  },
]

const defaultForm = {
  airline_code: '', iata_code: '', icao_code: '', airline_name: '',
  country: '', headquarters: '', phone: '', email: '', alliance: '', is_active: true,
}

export default function AirlinesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Airline | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['airlines', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/airlines', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/airlines/${editingItem.airline_id}`, payload)
        : apiClient.post('/api/airlines', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Airline updated!' : 'Airline created!')
      queryClient.invalidateQueries({ queryKey: ['airlines'] })
      setModalOpen(false)
      reset(defaultForm)
      setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/airlines/${id}`),
    onSuccess: () => { toast.success('Airline deactivated'); queryClient.invalidateQueries({ queryKey: ['airlines'] }) },
  })

  const openNew = () => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }
  const openEdit = (item: Airline) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Airlines" subtitle="Manage airline master data" onNew={openNew} newLabel="New Airline" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          getRowKey={(row) => (row as unknown as Airline).airline_id}
          rowActions={(row) => {
            const item = row as unknown as Airline
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1">
                  <Edit2 size={15} />
                </button>
                <button
                  onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.airline_id) }}
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
        title={editingItem ? 'Edit Airline' : 'New Airline'}
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
            <label className="label">Airline Code *</label>
            <input className="input" {...register('airline_code')} placeholder="EK" />
          </div>
          <div>
            <label className="label">Airline Name *</label>
            <input className="input" {...register('airline_name')} placeholder="Emirates" />
          </div>
          <div>
            <label className="label">IATA Code</label>
            <input className="input" {...register('iata_code')} placeholder="EK" />
          </div>
          <div>
            <label className="label">ICAO Code</label>
            <input className="input" {...register('icao_code')} placeholder="UAE" />
          </div>
          <div>
            <label className="label">Country</label>
            <input className="input" {...register('country')} placeholder="UAE" />
          </div>
          <div>
            <label className="label">Alliance</label>
            <select className="input" {...register('alliance')}>
              <option value="">None</option>
              <option>Star Alliance</option>
              <option>SkyTeam</option>
              <option>Oneworld</option>
            </select>
          </div>
          <div>
            <label className="label">Phone</label>
            <input className="input" {...register('phone')} />
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" {...register('email')} />
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
