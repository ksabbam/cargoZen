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
  { key: 'contract_no', label: 'Contract No', sortable: true },
  { key: 'vendor_name', label: 'Vendor', sortable: true },
  { key: 'contract_type', label: 'Type' },
  { key: 'transport_mode', label: 'Mode' },
  { key: 'start_date', label: 'Start Date' },
  { key: 'end_date', label: 'End Date' },
  { key: 'currency', label: 'Currency', width: '80px' },
  { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
]

const defaultForm = {
  contract_no: '', vendor_id: '', contract_type: '', transport_mode: '',
  start_date: '', end_date: '', currency: 'USD', remarks: '', status: 'DRAFT',
}

export default function VendorContractsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['vendor-contracts', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/vendor-contracts', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/vendor-contracts/${editingItem.contract_id}`, payload)
        : apiClient.post('/api/vendor-contracts', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Contract updated!' : 'Contract created!')
      queryClient.invalidateQueries({ queryKey: ['vendor-contracts'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Vendor Contracts" subtitle="Manage vendor pricing agreements" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Contract" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by contract number..."
          getRowKey={(row) => (row as Record<string, unknown>).contract_id as number}
          rowActions={(row) => {
            const item = row as Record<string, unknown>
            return (
              <button onClick={() => openEdit(item)} className="text-blue-500 hover:text-blue-700 p-1">
                <Edit2 size={15} />
              </button>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Contract' : 'New Vendor Contract'}
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
          <div><label className="label">Contract Number *</label><input className="input" {...register('contract_no')} placeholder="VCT-2026-001" /></div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              <option value="DRAFT">Draft</option>
              <option value="ACTIVE">Active</option>
              <option value="EXPIRED">Expired</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Vendor *</label><input className="input" {...register('vendor_id')} placeholder="Vendor ID or search..." /></div>
          <div>
            <label className="label">Contract Type</label>
            <select className="input" {...register('contract_type')}>
              <option value="">Select type</option>
              <option value="AIR_FREIGHT">Air Freight</option>
              <option value="SEA_FREIGHT">Sea Freight</option>
              <option value="TRUCKING">Trucking</option>
              <option value="CUSTOMS">Customs</option>
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
          <div><label className="label">Start Date *</label><input className="input" type="date" {...register('start_date')} /></div>
          <div><label className="label">End Date</label><input className="input" type="date" {...register('end_date')} /></div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Remarks</label><textarea className="input" rows={2} {...register('remarks')} /></div>
        </form>
      </Modal>
    </div>
  )
}
