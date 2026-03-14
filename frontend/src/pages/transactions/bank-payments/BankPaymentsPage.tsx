import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { BankPayment } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'payment_no', label: 'Payment No', sortable: true },
  { key: 'payment_date', label: 'Date', sortable: true },
  { key: 'bank_name', label: 'Bank Name' },
  { key: 'payee_name', label: 'Payee' },
  {
    key: 'amount', label: 'Amount',
    render: (v: unknown, row: unknown) => {
      const r = row as BankPayment
      return `${r.currency} ${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
    }
  },
  { key: 'payment_method', label: 'Method' },
  { key: 'reference_no', label: 'Reference' },
  {
    key: 'status', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v as string} />
  },
]

const defaultForm = {
  payment_no: '', payment_date: new Date().toISOString().split('T')[0],
  bank_name: '', payee_name: '', amount: '',
  currency: 'USD', exchange_rate: '1', payment_method: 'WIRE',
  reference_no: '', narration: '', status: 'DRAFT',
}

export default function BankPaymentsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<BankPayment | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['bank-payments', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/bank-payments', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/bank-payments/${editingItem.payment_id}`, payload)
        : apiClient.post('/api/bank-payments', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Payment updated!' : 'Payment created!')
      queryClient.invalidateQueries({ queryKey: ['bank-payments'] })
      setModalOpen(false)
      reset(defaultForm)
      setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const openNew = () => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }
  const openEdit = (item: BankPayment) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Bank Payments" subtitle="Record outgoing bank payments" onNew={openNew} newLabel="New Payment" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by payment no, payee, bank..."
          getRowKey={(row) => (row as BankPayment).payment_id}
          rowActions={(row) => {
            const item = row as BankPayment
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
        title={editingItem ? 'Edit Payment' : 'New Bank Payment'}
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
            <label className="label">Payment Number *</label>
            <input className="input" {...register('payment_no')} placeholder="PAY-2026-0001" />
          </div>
          <div>
            <label className="label">Payment Date *</label>
            <input className="input" type="date" {...register('payment_date')} />
          </div>
          <div>
            <label className="label">Bank Name *</label>
            <input className="input" {...register('bank_name')} placeholder="Search bank..." />
          </div>
          <div>
            <label className="label">Payment Method</label>
            <select className="input" {...register('payment_method')}>
              <option value="WIRE">Wire Transfer</option>
              <option value="CHEQUE">Cheque</option>
              <option value="CASH">Cash</option>
              <option value="ONLINE">Online</option>
            </select>
          </div>
          <div className="col-span-2">
            <label className="label">Payee *</label>
            <input className="input" {...register('payee_name')} placeholder="Search payee..." />
          </div>
          <div>
            <label className="label">Amount *</label>
            <input className="input" type="number" step="0.01" {...register('amount')} />
          </div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
            </select>
          </div>
          <div>
            <label className="label">Exchange Rate</label>
            <input className="input" type="number" step="0.000001" {...register('exchange_rate')} />
          </div>
          <div>
            <label className="label">Reference No</label>
            <input className="input" {...register('reference_no')} />
          </div>
          <div className="col-span-2">
            <label className="label">Narration</label>
            <textarea className="input" rows={2} {...register('narration')} />
          </div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              <option value="DRAFT">Draft</option>
              <option value="POSTED">Posted</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </form>
      </Modal>
    </div>
  )
}
