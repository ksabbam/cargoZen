import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { BankReceipt } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'receipt_no', label: 'Receipt No', sortable: true },
  { key: 'receipt_date', label: 'Date', sortable: true },
  { key: 'bank_name', label: 'Bank Name' },
  { key: 'payer_name', label: 'Payer' },
  {
    key: 'amount', label: 'Amount',
    render: (v: unknown, row: unknown) => {
      const r = row as BankReceipt
      return `${r.currency} ${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
    }
  },
  { key: 'receipt_method', label: 'Method' },
  { key: 'reference_no', label: 'Reference' },
  { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
]

const defaultForm = {
  receipt_no: '', receipt_date: new Date().toISOString().split('T')[0],
  bank_name: '', payer_name: '', amount: '',
  currency: 'USD', exchange_rate: '1', receipt_method: 'WIRE',
  reference_no: '', narration: '', status: 'DRAFT',
}

export default function BankReceiptsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<BankReceipt | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['bank-receipts', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/bank-receipts', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/bank-receipts/${editingItem.receipt_id}`, payload)
        : apiClient.post('/api/bank-receipts', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Receipt updated!' : 'Receipt created!')
      queryClient.invalidateQueries({ queryKey: ['bank-receipts'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const openNew = () => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }
  const openEdit = (item: BankReceipt) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Bank Receipts" subtitle="Record incoming bank receipts" onNew={openNew} newLabel="New Receipt" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by receipt no, payer..."
          getRowKey={(row) => (row as BankReceipt).receipt_id}
          rowActions={(row) => {
            const item = row as BankReceipt
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
        title={editingItem ? 'Edit Receipt' : 'New Bank Receipt'}
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
          <div><label className="label">Receipt Number *</label><input className="input" {...register('receipt_no')} placeholder="RCP-2026-0001" /></div>
          <div><label className="label">Receipt Date *</label><input className="input" type="date" {...register('receipt_date')} /></div>
          <div><label className="label">Bank Name *</label><input className="input" {...register('bank_name')} placeholder="Emirates NBD" /></div>
          <div>
            <label className="label">Receipt Method</label>
            <select className="input" {...register('receipt_method')}>
              <option value="WIRE">Wire Transfer</option>
              <option value="CHEQUE">Cheque</option>
              <option value="CASH">Cash</option>
              <option value="ONLINE">Online</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Payer *</label><input className="input" {...register('payer_name')} placeholder="Search payer..." /></div>
          <div><label className="label">Amount *</label><input className="input" type="number" step="0.01" {...register('amount')} /></div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
          <div><label className="label">Reference No</label><input className="input" {...register('reference_no')} /></div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              <option value="DRAFT">Draft</option>
              <option value="POSTED">Posted</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Narration</label><textarea className="input" rows={2} {...register('narration')} /></div>
        </form>
      </Modal>
    </div>
  )
}
