import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'export_no', label: 'Export No', sortable: true },
  { key: 'export_date', label: 'Date', sortable: true },
  { key: 'exporter_name', label: 'Exporter' },
  { key: 'consignee_name', label: 'Consignee' },
  { key: 'transport_mode', label: 'Mode' },
  { key: 'hs_code', label: 'HS Code' },
  { key: 'destination_country', label: 'Destination' },
  {
    key: 'total_value', label: 'Value',
    render: (v: unknown, row: Record<string, unknown>) =>
      `${row.currency} ${Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
  },
  { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
]

const defaultForm = {
  export_no: '', export_date: new Date().toISOString().split('T')[0],
  exporter_name: '', consignee_name: '', commodity_desc: '',
  hs_code: '', country_of_origin: '', destination_country: '',
  transport_mode: 'SEA', incoterms: '', total_value: '',
  currency: 'USD', gross_weight: '', packages: '',
  customs_entry_no: '', customs_entry_date: '',
  status: 'DRAFT', remarks: '',
}

export default function CustomsExportPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['customs-export', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/customs-export', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/customs-export/${editingItem.export_id}`, payload)
        : apiClient.post('/api/customs-export', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Updated!' : 'Customs export created!')
      queryClient.invalidateQueries({ queryKey: ['customs-export'] })
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
      <PageHeader title="Customs Export" subtitle="Export customs declarations" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Export" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by export no, exporter..."
          getRowKey={(row) => (row as Record<string, unknown>).export_id as number}
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
        title={editingItem ? 'Edit Customs Export' : 'New Customs Export'}
        size="xl"
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
          <div><label className="label">Export Number *</label><input className="input" {...register('export_no')} placeholder="EXP-2026-0001" /></div>
          <div><label className="label">Export Date *</label><input className="input" type="date" {...register('export_date')} /></div>
          <div className="col-span-2"><label className="label">Exporter</label><input className="input" {...register('exporter_name')} placeholder="Exporter name..." /></div>
          <div className="col-span-2"><label className="label">Consignee</label><input className="input" {...register('consignee_name')} placeholder="Consignee name..." /></div>
          <div className="col-span-2"><label className="label">Commodity Description</label><textarea className="input" rows={2} {...register('commodity_desc')} /></div>
          <div><label className="label">HS Code</label><input className="input" {...register('hs_code')} placeholder="8471" /></div>
          <div><label className="label">Country of Origin</label><input className="input" {...register('country_of_origin')} /></div>
          <div><label className="label">Destination Country</label><input className="input" {...register('destination_country')} /></div>
          <div>
            <label className="label">Transport Mode</label>
            <select className="input" {...register('transport_mode')}>
              <option value="SEA">Sea</option>
              <option value="AIR">Air</option>
              <option value="ROAD">Road</option>
            </select>
          </div>
          <div>
            <label className="label">Incoterms</label>
            <select className="input" {...register('incoterms')}>
              <option value="">Select</option>
              <option>FOB</option><option>EXW</option><option>CIF</option>
              <option>CFR</option><option>DDP</option><option>DAP</option>
            </select>
          </div>
          <div><label className="label">Total Value</label><input className="input" type="number" step="0.01" {...register('total_value')} /></div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          <div><label className="label">Gross Weight (KG)</label><input className="input" type="number" step="0.001" {...register('gross_weight')} /></div>
          <div><label className="label">Packages</label><input className="input" type="number" {...register('packages')} /></div>
          <div><label className="label">Customs Entry No</label><input className="input" {...register('customs_entry_no')} /></div>
          <div><label className="label">Customs Entry Date</label><input className="input" type="date" {...register('customs_entry_date')} /></div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              <option value="DRAFT">Draft</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="CLEARED">Cleared</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Remarks</label><textarea className="input" rows={2} {...register('remarks')} /></div>
        </form>
      </Modal>
    </div>
  )
}
