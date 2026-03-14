import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { JournalEntry, JournalLine } from '@/types'
import { useForm, useFieldArray } from 'react-hook-form'

const columns = [
  { key: 'entry_no', label: 'Entry No', sortable: true },
  { key: 'entry_date', label: 'Date', sortable: true },
  { key: 'entry_type', label: 'Type' },
  { key: 'description', label: 'Description' },
  {
    key: 'total_debit', label: 'Total Debit',
    render: (v: unknown) => v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '-'
  },
  {
    key: 'total_credit', label: 'Total Credit',
    render: (v: unknown) => v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '-'
  },
  {
    key: 'status', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v as string} />
  },
]

interface FormData {
  entry_no: string
  entry_date: string
  entry_type: string
  description: string
  status: string
  lines: Array<{
    account_id: string
    account_code: string
    account_name: string
    debit_amount: string
    credit_amount: string
    narration: string
  }>
}

const defaultLine = { account_id: '', account_code: '', account_name: '', debit_amount: '', credit_amount: '', narration: '' }
const defaultForm: FormData = {
  entry_no: '', entry_date: new Date().toISOString().split('T')[0],
  entry_type: 'STANDARD', description: '', status: 'DRAFT',
  lines: [{ ...defaultLine }, { ...defaultLine }],
}

export default function JournalEntriesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<JournalEntry | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, control, watch } = useForm<FormData>({ defaultValues: defaultForm })
  const { fields, append, remove } = useFieldArray({ control, name: 'lines' })

  const lines = watch('lines')
  const totalDebit = lines.reduce((sum, l) => sum + (parseFloat(l.debit_amount) || 0), 0)
  const totalCredit = lines.reduce((sum, l) => sum + (parseFloat(l.credit_amount) || 0), 0)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['journal-entries', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/journal-entries', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: FormData) =>
      editingItem
        ? apiClient.put(`/api/journal-entries/${editingItem.entry_id}`, payload)
        : apiClient.post('/api/journal-entries', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Entry updated!' : 'Journal entry created!')
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] })
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

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Journal Entries" subtitle="Double-entry bookkeeping" onNew={openNew} newLabel="New Journal Entry" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          getRowKey={(row) => (row as unknown as JournalEntry).entry_id}
          rowActions={(row) => {
            const item = row as unknown as JournalEntry
            return (
              <button onClick={() => { setEditingItem(item); setModalOpen(true) }} className="text-blue-500 hover:text-blue-700 p-1">
                <Edit2 size={15} />
              </button>
            )
          }}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingItem(null) }}
        title={editingItem ? 'Edit Journal Entry' : 'New Journal Entry'}
        size="xl"
        footer={
          <>
            <div className="flex-1 text-sm">
              <span className={`font-medium ${Math.abs(totalDebit - totalCredit) < 0.001 ? 'text-green-600' : 'text-red-500'}`}>
                Debit: {totalDebit.toFixed(2)} | Credit: {totalCredit.toFixed(2)}
                {Math.abs(totalDebit - totalCredit) >= 0.001 && ' ⚠ Unbalanced'}
              </span>
            </div>
            <button className="btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button
              className="btn-primary"
              onClick={handleSubmit((d) => saveMutation.mutate(d))}
              disabled={saveMutation.isPending || Math.abs(totalDebit - totalCredit) >= 0.001}
            >
              {saveMutation.isPending ? 'Saving...' : 'Post Entry'}
            </button>
          </>
        }
      >
        <form className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="label">Entry Number *</label>
              <input className="input" {...register('entry_no')} placeholder="JE-2026-0001" />
            </div>
            <div>
              <label className="label">Date *</label>
              <input className="input" type="date" {...register('entry_date')} />
            </div>
            <div>
              <label className="label">Entry Type</label>
              <select className="input" {...register('entry_type')}>
                <option value="STANDARD">Standard</option>
                <option value="ADJUSTING">Adjusting</option>
                <option value="REVERSING">Reversing</option>
                <option value="OPENING">Opening</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Description</label>
            <input className="input" {...register('description')} placeholder="Entry description..." />
          </div>

          {/* Journal Lines */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">Journal Lines</label>
              <button
                type="button"
                onClick={() => append({ ...defaultLine })}
                className="btn-secondary btn-sm"
              >
                <Plus size={12} /> Add Line
              </button>
            </div>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="table-header">Account Code</th>
                    <th className="table-header">Account Name</th>
                    <th className="table-header w-28">Debit</th>
                    <th className="table-header w-28">Credit</th>
                    <th className="table-header">Narration</th>
                    <th className="table-header w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {fields.map((field, idx) => (
                    <tr key={field.id}>
                      <td className="px-2 py-1.5">
                        <input className="input py-1 text-xs" {...register(`lines.${idx}.account_code`)} placeholder="1101" />
                      </td>
                      <td className="px-2 py-1.5">
                        <input className="input py-1 text-xs" {...register(`lines.${idx}.account_name`)} placeholder="Account name" />
                      </td>
                      <td className="px-2 py-1.5">
                        <input className="input py-1 text-xs text-right" type="number" step="0.01" {...register(`lines.${idx}.debit_amount`)} placeholder="0.00" />
                      </td>
                      <td className="px-2 py-1.5">
                        <input className="input py-1 text-xs text-right" type="number" step="0.01" {...register(`lines.${idx}.credit_amount`)} placeholder="0.00" />
                      </td>
                      <td className="px-2 py-1.5">
                        <input className="input py-1 text-xs" {...register(`lines.${idx}.narration`)} placeholder="Narration" />
                      </td>
                      <td className="px-2 py-1.5">
                        {fields.length > 2 && (
                          <button type="button" onClick={() => remove(idx)} className="text-red-400 hover:text-red-600">
                            <Trash2 size={13} />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-gray-50">
                  <tr>
                    <td colSpan={2} className="px-3 py-2 text-xs font-semibold text-right text-gray-600">Total</td>
                    <td className="px-3 py-2 text-xs font-bold text-right text-blue-700">{totalDebit.toFixed(2)}</td>
                    <td className="px-3 py-2 text-xs font-bold text-right text-blue-700">{totalCredit.toFixed(2)}</td>
                    <td colSpan={2}></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </form>
      </Modal>
    </div>
  )
}
