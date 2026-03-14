import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { PurchaseBill } from '@/types'
import { useForm, useFieldArray } from 'react-hook-form'

const columns = [
  { key: 'bill_no', label: 'Bill No', sortable: true },
  { key: 'bill_date', label: 'Date', sortable: true },
  { key: 'vendor_name', label: 'Vendor' },
  { key: 'vendor_invoice_no', label: 'Vendor Invoice' },
  {
    key: 'total_amount', label: 'Total Amount',
    render: (v: unknown, row: unknown) => {
      const r = row as PurchaseBill
      return `${r.currency} ${Number(v || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`
    }
  },
  { key: 'due_date', label: 'Due Date' },
  { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
]

interface BillLine { charge_name: string; quantity: string; unit_rate: string; amount: string; tax_amount: string }
interface FormData {
  bill_no: string; bill_date: string; vendor_name: string;
  vendor_invoice_no: string; vendor_inv_date: string;
  currency: string; due_date: string; job_id: string; status: string; remarks: string;
  lines: BillLine[]
}
const defaultLine: BillLine = { charge_name: '', quantity: '1', unit_rate: '', amount: '', tax_amount: '0' }
const defaultForm: FormData = {
  bill_no: '', bill_date: new Date().toISOString().split('T')[0],
  vendor_name: '', vendor_invoice_no: '', vendor_inv_date: '',
  currency: 'USD', due_date: '', job_id: '', status: 'DRAFT', remarks: '',
  lines: [{ ...defaultLine }],
}

export default function PurchaseBillsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<PurchaseBill | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, control, watch } = useForm<FormData>({ defaultValues: defaultForm })
  const { fields, append, remove } = useFieldArray({ control, name: 'lines' })
  const lines = watch('lines')
  const subtotal = lines.reduce((sum, l) => sum + (parseFloat(l.amount) || 0), 0)
  const taxTotal = lines.reduce((sum, l) => sum + (parseFloat(l.tax_amount) || 0), 0)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['purchase-bills', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/purchase-bills', { params: { page, limit: 20, search: search || undefined } })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: FormData) => {
      const p = { ...payload, amount: subtotal, tax_amount: taxTotal, total_amount: subtotal + taxTotal }
      return editingItem
        ? apiClient.put(`/api/purchase-bills/${editingItem.bill_id}`, p)
        : apiClient.post('/api/purchase-bills', p)
    },
    onSuccess: () => {
      toast.success(editingItem ? 'Bill updated!' : 'Purchase bill created!')
      queryClient.invalidateQueries({ queryKey: ['purchase-bills'] })
      setModalOpen(false); reset(defaultForm); setEditingItem(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const openNew = () => { reset(defaultForm); setEditingItem(null); setModalOpen(true) }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Purchase Bills" subtitle="Vendor invoices and purchase bills" onNew={openNew} newLabel="New Purchase Bill" />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns} data={data?.data || []} total={data?.total || 0}
          page={page} limit={20} onPageChange={setPage} onSearch={setSearch}
          onRefresh={() => refetch()} isLoading={isLoading}
          searchPlaceholder="Search by bill no, vendor..."
          getRowKey={(row) => (row as PurchaseBill).bill_id}
          rowActions={(row) => {
            const item = row as PurchaseBill
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
        title={editingItem ? 'Edit Purchase Bill' : 'New Purchase Bill'}
        size="xl"
        footer={
          <>
            <div className="flex-1 text-sm text-gray-600">
              Sub-total: <strong>{subtotal.toFixed(2)}</strong> | Tax: <strong>{taxTotal.toFixed(2)}</strong> | Total: <strong className="text-blue-700">{(subtotal + taxTotal).toFixed(2)}</strong>
            </div>
            <button className="btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSubmit((d) => saveMutation.mutate(d))} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving...' : 'Save'}
            </button>
          </>
        }
      >
        <form className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div><label className="label">Bill Number *</label><input className="input" {...register('bill_no')} placeholder="BILL-2026-001" /></div>
            <div><label className="label">Bill Date *</label><input className="input" type="date" {...register('bill_date')} /></div>
            <div>
              <label className="label">Status</label>
              <select className="input" {...register('status')}>
                <option value="DRAFT">Draft</option>
                <option value="APPROVED">Approved</option>
                <option value="PAID">Paid</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2"><label className="label">Vendor *</label><input className="input" {...register('vendor_name')} placeholder="Vendor name..." /></div>
            <div>
              <label className="label">Currency</label>
              <select className="input" {...register('currency')}>
                <option value="USD">USD</option>
                <option value="AED">AED</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div><label className="label">Vendor Invoice No</label><input className="input" {...register('vendor_invoice_no')} /></div>
            <div><label className="label">Vendor Invoice Date</label><input className="input" type="date" {...register('vendor_inv_date')} /></div>
            <div><label className="label">Due Date</label><input className="input" type="date" {...register('due_date')} /></div>
          </div>

          {/* Bill Lines */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="label mb-0">Bill Lines</label>
              <button type="button" onClick={() => append({ ...defaultLine })} className="btn-secondary btn-sm"><Plus size={12} /> Add Line</button>
            </div>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="table-header">Description / Charge</th>
                    <th className="table-header w-20">Qty</th>
                    <th className="table-header w-28">Unit Rate</th>
                    <th className="table-header w-28">Amount</th>
                    <th className="table-header w-24">Tax</th>
                    <th className="table-header w-10"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {fields.map((field, idx) => (
                    <tr key={field.id}>
                      <td className="px-2 py-1.5"><input className="input py-1 text-xs" {...register(`lines.${idx}.charge_name`)} placeholder="Freight charges..." /></td>
                      <td className="px-2 py-1.5"><input className="input py-1 text-xs text-right" type="number" step="0.001" {...register(`lines.${idx}.quantity`)} /></td>
                      <td className="px-2 py-1.5"><input className="input py-1 text-xs text-right" type="number" step="0.01" {...register(`lines.${idx}.unit_rate`)} /></td>
                      <td className="px-2 py-1.5"><input className="input py-1 text-xs text-right" type="number" step="0.01" {...register(`lines.${idx}.amount`)} /></td>
                      <td className="px-2 py-1.5"><input className="input py-1 text-xs text-right" type="number" step="0.01" {...register(`lines.${idx}.tax_amount`)} /></td>
                      <td className="px-2 py-1.5">
                        {fields.length > 1 && (
                          <button type="button" onClick={() => remove(idx)} className="text-red-400 hover:text-red-600"><Trash2 size={13} /></button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div><label className="label">Remarks</label><textarea className="input" rows={2} {...register('remarks')} /></div>
        </form>
      </Modal>
    </div>
  )
}
