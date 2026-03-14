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
  { key: 'commodity_code', label: 'Code', sortable: true, width: '110px' },
  { key: 'commodity_name', label: 'Commodity Name', sortable: true },
  { key: 'hs_code', label: 'HS Code' },
  { key: 'commodity_group', label: 'Group' },
  {
    key: 'is_dangerous', label: 'Dangerous Goods',
    render: (v: unknown) => v
      ? <span className="badge badge-danger">⚠ Dangerous</span>
      : <span className="badge badge-gray">Normal</span>
  },
  { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
]

const defaultForm = {
  commodity_code: '', commodity_name: '', hs_code: '', commodity_group: '',
  is_dangerous: false, dangerous_class: '', un_number: '', description: '', is_active: true,
}

export default function CommoditiesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue, watch } = useForm({ defaultValues: defaultForm })
  const isDangerous = watch('is_dangerous')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['commodities', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/commodities', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/commodities/${editingItem.commodity_id}`, payload)
        : apiClient.post('/api/commodities', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Commodity updated!' : 'Commodity created!')
      queryClient.invalidateQueries({ queryKey: ['commodities'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/commodities/${id}`),
    onSuccess: () => { toast.success('Deactivated'); queryClient.invalidateQueries({ queryKey: ['commodities'] }) },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string | boolean))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Commodities" subtitle="Cargo commodity types and HS codes" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Commodity" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by code, name, HS code..."
          getRowKey={(row) => (row as Record<string, unknown>).commodity_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <>
                <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1"><Edit2 size={15} /></button>
                <button onClick={() => { if (confirm('Deactivate?')) deleteMutation.mutate(item.commodity_id as number) }} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={15} /></button>
              </>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Commodity' : 'New Commodity'}
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
          <div><label className="label">Commodity Code *</label><input className="input" {...register('commodity_code')} placeholder="ELEC" /></div>
          <div><label className="label">Commodity Name *</label><input className="input" {...register('commodity_name')} placeholder="Electronics & Gadgets" /></div>
          <div><label className="label">HS Code</label><input className="input" {...register('hs_code')} placeholder="8471" /></div>
          <div>
            <label className="label">Commodity Group</label>
            <select className="input" {...register('commodity_group')}>
              <option value="">Select group</option>
              <option>TECHNOLOGY</option><option>TEXTILES</option><option>FOOD</option>
              <option>MACHINERY</option><option>AUTOMOTIVE</option><option>CHEMICALS</option>
              <option>PHARMA</option><option>FURNITURE</option><option>LUXURY</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="label">Description</label>
            <textarea className="input" rows={2} {...register('description')} />
          </div>
          <div className="col-span-2 flex gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" {...register('is_dangerous')} className="rounded text-red-600" />
              <span className="text-sm text-gray-700 font-medium">⚠ Dangerous Goods</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" {...register('is_active')} className="rounded text-blue-600" />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>
          {isDangerous && (
            <>
              <div>
                <label className="label">Dangerous Class</label>
                <select className="input" {...register('dangerous_class')}>
                  <option value="">Select class</option>
                  <option>Class 1 - Explosives</option><option>Class 2 - Gases</option>
                  <option>Class 3 - Flammable Liquids</option><option>Class 4 - Flammable Solids</option>
                  <option>Class 5 - Oxidizers</option><option>Class 6 - Toxic</option>
                  <option>Class 7 - Radioactive</option><option>Class 8 - Corrosives</option>
                  <option>Class 9 - Miscellaneous</option>
                </select>
              </div>
              <div><label className="label">UN Number</label><input className="input" {...register('un_number')} placeholder="UN1234" /></div>
            </>
          )}
        </form>
      </Modal>
    </div>
  )
}
