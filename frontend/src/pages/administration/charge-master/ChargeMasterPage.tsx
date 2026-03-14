import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { ChargeMaster } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'charge_code', label: 'Code', sortable: true, width: '100px' },
  { key: 'charge_name', label: 'Charge Name', sortable: true },
  { key: 'charge_type', label: 'Type' },
  { key: 'charge_category', label: 'Category' },
  { key: 'applicable_for', label: 'Applicable For' },
  { key: 'unit_type', label: 'Unit Type' },
  {
    key: 'is_taxable', label: 'Taxable',
    render: (v: unknown) => v ? <span className="badge badge-warning">Yes</span> : <span className="badge badge-gray">No</span>
  },
  {
    key: 'is_active', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} />
  },
]

const defaultForm = {
  charge_code: '', charge_name: '', charge_type: '', charge_category: '',
  applicable_for: '', unit_type: '', is_taxable: false, is_active: true,
}

export default function ChargeMasterPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<ChargeMaster | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['charge-master', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/charge-master', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/charge-master/${editingItem.charge_id}`, payload)
        : apiClient.post('/api/charge-master', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Charge updated!' : 'Charge created!')
      queryClient.invalidateQueries({ queryKey: ['charge-master'] })
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
    mutationFn: (id: number) => apiClient.delete(`/api/charge-master/${id}`),
    onSuccess: () => { toast.success('Charge deactivated'); queryClient.invalidateQueries({ queryKey: ['charge-master'] }) },
  })

  const openEdit = (item: ChargeMaster) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Charge Master" subtitle="Define freight charges and fees" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          getRowKey={(row) => (row as unknown as ChargeMaster).charge_id}
          rowActions={(row) => {
            const item = row as unknown as ChargeMaster
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1"><Edit2 size={15} /></button>
                <button onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.charge_id) }} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={15} /></button>
              </>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Charge' : 'New Charge'}
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
            <label className="label">Charge Code *</label>
            <input className="input" {...register('charge_code')} placeholder="FCH" />
          </div>
          <div>
            <label className="label">Charge Name *</label>
            <input className="input" {...register('charge_name')} placeholder="Freight Charges" />
          </div>
          <div>
            <label className="label">Charge Type</label>
            <select className="input" {...register('charge_type')}>
              <option value="">Select type</option>
              <option>FREIGHT</option>
              <option>CUSTOMS</option>
              <option>HANDLING</option>
              <option>LOCAL</option>
              <option>TAX</option>
              <option>MISC</option>
            </select>
          </div>
          <div>
            <label className="label">Charge Category</label>
            <select className="input" {...register('charge_category')}>
              <option value="">Select category</option>
              <option>ORIGIN</option>
              <option>MAIN</option>
              <option>DESTINATION</option>
              <option>LOCAL</option>
              <option>CUSTOMS</option>
              <option>DUTY</option>
              <option>TAX</option>
              <option>ADMIN</option>
            </select>
          </div>
          <div>
            <label className="label">Applicable For</label>
            <select className="input" {...register('applicable_for')}>
              <option value="">Both</option>
              <option value="IMPORT">Import</option>
              <option value="EXPORT">Export</option>
              <option value="BOTH">Both</option>
            </select>
          </div>
          <div>
            <label className="label">Unit Type</label>
            <select className="input" {...register('unit_type')}>
              <option value="">Select unit</option>
              <option value="LUMP">Lump Sum</option>
              <option value="PER_KG">Per KG</option>
              <option value="PER_CBM">Per CBM</option>
              <option value="PER_UNIT">Per Unit</option>
              <option value="PER_CONTAINER">Per Container</option>
            </select>
          </div>
          <div className="col-span-2 flex gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" {...register('is_taxable')} className="rounded text-blue-600" />
              <span className="text-sm text-gray-700">Taxable</span>
            </label>
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
