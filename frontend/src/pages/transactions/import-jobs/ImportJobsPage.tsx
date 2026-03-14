import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Eye, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { ImportJob } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'job_no', label: 'Job No', sortable: true, width: '120px' },
  { key: 'job_date', label: 'Date', sortable: true, width: '100px' },
  { key: 'transport_mode', label: 'Mode', width: '80px' },
  { key: 'shipper_name', label: 'Shipper' },
  { key: 'consignee_name', label: 'Consignee' },
  { key: 'bl_no', label: 'BL / AWB' },
  { key: 'pol', label: 'POL', width: '80px' },
  { key: 'pod', label: 'POD', width: '80px' },
  { key: 'eta', label: 'ETA', width: '100px' },
  {
    key: 'gross_weight', label: 'Weight (KG)',
    render: (v: unknown) => v ? Number(v).toLocaleString() : '-'
  },
  {
    key: 'status', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v as string} />
  },
]

const defaultForm = {
  job_no: '', job_date: new Date().toISOString().split('T')[0],
  transport_mode: 'SEA', bl_no: '', flight_no: '', vessel_name: '', voyage_no: '',
  pol: '', pod: '', eta: '', ata: '',
  gross_weight: '', chargeable_weight: '', volume_cbm: '', packages: '', package_type: '',
  incoterms: '', freight_currency: 'USD', freight_amount: '',
  status: 'OPEN', remarks: '',
}

export default function ImportJobsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<ImportJob | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue, watch } = useForm({ defaultValues: defaultForm })
  const transportMode = watch('transport_mode')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['import-jobs', page, search, statusFilter],
    queryFn: async () => {
      const res = await apiClient.get('/api/import-jobs', {
        params: { page, limit: 20, search: search || undefined, status: statusFilter || undefined }
      })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/import-jobs/${editingItem.job_id}`, payload)
        : apiClient.post('/api/import-jobs', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Job updated!' : 'Import job created!')
      queryClient.invalidateQueries({ queryKey: ['import-jobs'] })
      setModalOpen(false)
      reset(defaultForm)
      setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const openEdit = (item: ImportJob) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Import Jobs"
        subtitle="Manage freight import job orders"
        onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }}
        newLabel="New Import Job"
        actions={
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input py-1.5 text-sm w-36"
          >
            <option value="">All Status</option>
            <option value="OPEN">Open</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        }
      />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by job no, BL/AWB..."
          getRowKey={(row) => (row as unknown as ImportJob).job_id}
          rowActions={(row) => {
            const item = row as unknown as ImportJob
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
        title={editingItem ? `Edit Job - ${editingItem.job_no}` : 'New Import Job'}
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
        <form className="space-y-4">
          {/* Header */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Job Number *</label>
              <input className="input" {...register('job_no')} placeholder="IMP-2026-0001" />
            </div>
            <div>
              <label className="label">Job Date *</label>
              <input className="input" type="date" {...register('job_date')} />
            </div>
            <div>
              <label className="label">Transport Mode *</label>
              <select className="input" {...register('transport_mode')}>
                <option value="SEA">Sea Freight</option>
                <option value="AIR">Air Freight</option>
                <option value="ROAD">Road Freight</option>
              </select>
            </div>
          </div>

          {/* Parties */}
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider pt-1">Parties</div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Shipper</label>
              <input className="input" {...register('vessel_name')} placeholder="Search shipper..." />
            </div>
            <div>
              <label className="label">Consignee</label>
              <input className="input" placeholder="Search consignee..." />
            </div>
          </div>

          {/* Transport Details */}
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider pt-1">Transport Details</div>
          <div className="grid grid-cols-3 gap-4">
            {transportMode === 'AIR' ? (
              <>
                <div>
                  <label className="label">AWB Number</label>
                  <input className="input" {...register('bl_no')} placeholder="123-45678901" />
                </div>
                <div>
                  <label className="label">Flight No</label>
                  <input className="input" {...register('flight_no')} placeholder="EK 201" />
                </div>
              </>
            ) : (
              <>
                <div>
                  <label className="label">BL Number</label>
                  <input className="input" {...register('bl_no')} placeholder="MAEU123456789" />
                </div>
                <div>
                  <label className="label">Vessel Name</label>
                  <input className="input" {...register('vessel_name')} placeholder="MSC Gülsün" />
                </div>
                <div>
                  <label className="label">Voyage No</label>
                  <input className="input" {...register('voyage_no')} placeholder="0VT5SE1MA" />
                </div>
              </>
            )}
            <div>
              <label className="label">Port of Loading</label>
              <input className="input" {...register('pol')} placeholder="CNSHA" />
            </div>
            <div>
              <label className="label">Port of Discharge</label>
              <input className="input" {...register('pod')} placeholder="AEDXB" />
            </div>
            <div>
              <label className="label">ETA</label>
              <input className="input" type="date" {...register('eta')} />
            </div>
            <div>
              <label className="label">ATA</label>
              <input className="input" type="date" {...register('ata')} />
            </div>
          </div>

          {/* Cargo Details */}
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider pt-1">Cargo Details</div>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="label">Gross Weight (KG)</label>
              <input className="input" type="number" step="0.001" {...register('gross_weight')} />
            </div>
            <div>
              <label className="label">Chargeable Weight</label>
              <input className="input" type="number" step="0.001" {...register('chargeable_weight')} />
            </div>
            <div>
              <label className="label">Volume (CBM)</label>
              <input className="input" type="number" step="0.001" {...register('volume_cbm')} />
            </div>
            <div>
              <label className="label">Packages</label>
              <input className="input" type="number" {...register('packages')} />
            </div>
            <div>
              <label className="label">Package Type</label>
              <select className="input" {...register('package_type')}>
                <option value="">Select</option>
                <option>CARTON</option>
                <option>PALLET</option>
                <option>CONTAINER</option>
                <option>BAG</option>
                <option>DRUM</option>
              </select>
            </div>
            <div>
              <label className="label">Incoterms</label>
              <select className="input" {...register('incoterms')}>
                <option value="">Select</option>
                <option>EXW</option>
                <option>FOB</option>
                <option>CIF</option>
                <option>CFR</option>
                <option>DDP</option>
                <option>DAP</option>
              </select>
            </div>
            <div>
              <label className="label">Freight Currency</label>
              <select className="input" {...register('freight_currency')}>
                <option>USD</option>
                <option>AED</option>
                <option>EUR</option>
              </select>
            </div>
            <div>
              <label className="label">Freight Amount</label>
              <input className="input" type="number" step="0.01" {...register('freight_amount')} />
            </div>
          </div>

          <div>
            <label className="label">Status</label>
            <select className="input w-48" {...register('status')}>
              <option value="OPEN">Open</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          <div>
            <label className="label">Remarks</label>
            <textarea className="input" rows={2} {...register('remarks')} />
          </div>
        </form>
      </Modal>
    </div>
  )
}
