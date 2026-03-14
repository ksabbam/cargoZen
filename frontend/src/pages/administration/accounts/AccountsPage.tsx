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
  { key: 'account_code', label: 'Code', sortable: true, width: '100px' },
  { key: 'account_name', label: 'Account Name', sortable: true },
  { key: 'account_type', label: 'Type' },
  { key: 'account_subtype', label: 'Sub-Type' },
  { key: 'currency', label: 'Currency', width: '80px' },
  {
    key: 'opening_balance', label: 'Opening Balance',
    render: (v: unknown) => v ? Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 }) : '0.00'
  },
  {
    key: 'is_active', label: 'Status',
    render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} />
  },
]

const defaultForm = {
  account_code: '', account_name: '', account_type: 'ASSET',
  account_subtype: '', description: '', opening_balance: '0',
  currency: 'USD', is_active: true,
}

export default function AccountsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<Record<string, unknown> | null>(null)
  const queryClient = useQueryClient()
  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['accounts', page, search, typeFilter],
    queryFn: async () => {
      const res = await apiClient.get('/api/accounts', {
        params: { page, limit: 50, search: search || undefined, account_type: typeFilter || undefined }
      })
      return res.data
    },
  })

  const saveMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingItem
        ? apiClient.put(`/api/accounts/${editingItem.account_id}`, payload)
        : apiClient.post('/api/accounts', payload),
    onSuccess: () => {
      toast.success(editingItem ? 'Account updated!' : 'Account created!')
      queryClient.invalidateQueries({ queryKey: ['accounts'] })
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
  const openEdit = (item: Record<string, unknown>) => {
    setEditingItem(item)
    Object.entries(item).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, String(v ?? '')))
    setModalOpen(true)
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Chart of Accounts"
        subtitle="Manage the chart of accounts hierarchy"
        onNew={openNew}
        newLabel="New Account"
        actions={
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="input py-1.5 text-sm w-36"
          >
            <option value="">All Types</option>
            <option value="ASSET">Asset</option>
            <option value="LIABILITY">Liability</option>
            <option value="EQUITY">Equity</option>
            <option value="INCOME">Income</option>
            <option value="EXPENSE">Expense</option>
          </select>
        }
      />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns}
          data={data?.data || []}
          total={data?.total || 0}
          page={page}
          limit={50}
          onPageChange={setPage}
          onSearch={setSearch}
          onRefresh={() => refetch()}
          isLoading={isLoading}
          searchPlaceholder="Search by code or name..."
          getRowKey={(row) => (row as Record<string, unknown>).account_id as number}
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
        title={editingItem ? 'Edit Account' : 'New Account'}
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
            <label className="label">Account Code *</label>
            <input className="input" {...register('account_code')} placeholder="1101" />
          </div>
          <div>
            <label className="label">Account Name *</label>
            <input className="input" {...register('account_name')} placeholder="Petty Cash" />
          </div>
          <div>
            <label className="label">Account Type *</label>
            <select className="input" {...register('account_type')}>
              <option value="ASSET">Asset</option>
              <option value="LIABILITY">Liability</option>
              <option value="EQUITY">Equity</option>
              <option value="INCOME">Income</option>
              <option value="EXPENSE">Expense</option>
            </select>
          </div>
          <div>
            <label className="label">Sub-Type</label>
            <select className="input" {...register('account_subtype')}>
              <option value="">None</option>
              <option>CURRENT</option>
              <option>NON_CURRENT</option>
              <option>BANK</option>
              <option>RECEIVABLE</option>
              <option>PAYABLE</option>
              <option>CONTROL</option>
            </select>
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
            <label className="label">Opening Balance</label>
            <input className="input" type="number" step="0.01" {...register('opening_balance')} />
          </div>
          <div className="col-span-2">
            <label className="label">Description</label>
            <textarea className="input" rows={2} {...register('description')} />
          </div>
          <div className="col-span-2">
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
