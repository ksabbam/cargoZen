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
  { key: 'dn_no', label: 'DN No', sortable: true },
  { key: 'dn_date', label: 'Date', sortable: true },
  { key: 'party_name', label: 'Party' },
  {
    key: 'amount', label: 'Amount',
    render: (v: unknown, row: Record<string, unknown>) =>
      `${row.currency} ${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
  },
  { key: 'reason', label: 'Reason' },
  { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
]

const defaultForm = {
  dn_no: '', dn_date: new Date().toISOString().split('T')[0],
  party_name: '', amount: '', currency: 'USD', reason: '', status: 'DRAFT',
}

export default function DebitNotesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['debit-notes', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/debit-notes', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/debit-notes/${editingItem.dn_id}`, payload)
        : apiClient.post('/api/debit-notes', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Updated!' : 'Debit note created!')
      queryClient.invalidateQueries({ queryKey: ['debit-notes'] })
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
      <PageHeader title="General Debit Notes" subtitle="Issue debit notes to parties" onNew={() => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }} newLabel="New Debit Note" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by DN no, party..."
          getRowKey={(row) => (row as Record<string, unknown>).dn_id as number}
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
        title={editingItem ? 'Edit Debit Note' : 'New General Debit Note'}
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
          <div><label className="label">DN Number *</label><input className="input" {...register('dn_no')} placeholder="DN-2026-0001" /></div>
          <div><label className="label">Date *</label><input className="input" type="date" {...register('dn_date')} /></div>
          <div className="col-span-2"><label className="label">Party *</label><input className="input" {...register('party_name')} placeholder="Search party..." /></div>
          <div><label className="label">Amount *</label><input className="input" type="number" step="0.01" {...register('amount')} /></div>
          <div>
            <label className="label">Currency</label>
            <select className="input" {...register('currency')}>
              <option value="USD">USD</option>
              <option value="AED">AED</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
          <div className="col-span-2"><label className="label">Reason *</label><textarea className="input" rows={3} {...register('reason')} placeholder="Reason for debit note..." /></div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              <option value="DRAFT">Draft</option>
              <option value="APPROVED">Approved</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </form>
      </Modal>
    </div>
  )
}
