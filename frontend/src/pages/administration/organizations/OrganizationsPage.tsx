import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Edit2, Trash2, CheckCircle, XCircle, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import Modal from '@/components/common/Modal'
import StatusBadge from '@/components/common/StatusBadge'
import type { Organization } from '@/types'
import { useForm } from 'react-hook-form'

const columns = [
  { key: 'org_code', label: 'Code', sortable: true, width: '100px' },
  { key: 'org_name', label: 'Name', sortable: true },
  { key: 'group_name', label: 'Group' },
  { key: 'org_type', label: 'Type' },
  { key: 'country', label: 'Country' },
  { key: 'phone', label: 'Phone' },
  {
    key: 'is_customer', label: 'Roles',
    render: (_: unknown, row: unknown) => {
      const org = row as Organization
      return (
        <div className="flex gap-1 flex-wrap">
          {org.is_customer && <span className="badge badge-info">Customer</span>}
          {org.is_vendor && <span className="badge badge-warning">Vendor</span>}
          {org.is_agent && <span className="badge badge-gray">Agent</span>}
          {org.is_carrier && <span className="badge badge-gray">Carrier</span>}
        </div>
      )
    }
  },
  {
    key: 'approval_status', label: 'Approval',
    render: (v: unknown) => <StatusBadge status={v as string} />
  },
  {
    key: 'is_active', label: 'Active',
    render: (v: unknown) => v
      ? <span className="badge badge-success">Active</span>
      : <span className="badge badge-gray">Inactive</span>
  },
]

const defaultForm = {
  org_code: '', org_name: '', org_short_name: '', org_type: '',
  is_customer: false, is_vendor: false, is_agent: false, is_carrier: false,
  country: '', phone: '', email: '', address_line1: '', city: '', state: '', postal_code: '',
  website: '', tax_id: '', currency: 'USD', credit_limit: '', credit_days: '',
}

export default function OrganizationsPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isModalOpen, setModalOpen] = useState(false)
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null)
  const queryClient = useQueryClient()

  const { register, handleSubmit, reset, setValue } = useForm({ defaultValues: defaultForm })

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['organizations', page, search],
    queryFn: async () => {
      const res = await apiClient.get('/api/organizations', {
        params: { page, limit: 20, search: search || undefined }
      })
      return res.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: typeof defaultForm) =>
      editingOrg
        ? apiClient.put(`/api/organizations/${editingOrg.org_id}`, payload)
        : apiClient.post('/api/organizations', payload),
    onSuccess: () => {
      toast.success(editingOrg ? 'Organization updated!' : 'Organization created!')
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      setModalOpen(false)
      reset(defaultForm)
      setEditingOrg(null)
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } }
      toast.error(e.response?.data?.detail || 'Operation failed')
    },
  })

  const approveMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      apiClient.patch(`/api/organizations/${id}/approval`, { approval_status: status }),
    onSuccess: () => {
      toast.success('Approval status updated!')
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => apiClient.delete(`/api/organizations/${id}`),
    onSuccess: () => {
      toast.success('Organization deactivated')
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
    },
  })

  const openNew = () => {
    reset(defaultForm)
    setEditingOrg(null)
    setModalOpen(true)
  }

  const openEdit = (org: Organization) => {
    setEditingOrg(org)
    Object.entries(org).forEach(([k, v]) => setValue(k as keyof typeof defaultForm, v as string))
    setModalOpen(true)
  }

  const onSubmit = (data: typeof defaultForm) => createMutation.mutate(data)

  return (
    <div className="flex flex-col h-full">
      <PageHeader
        title="Organizations"
        subtitle="Manage customers, vendors, agents and carriers"
        onNew={openNew}
        newLabel="New Organization"
      />

      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns}
          data={data?.data || []}
          total={data?.total || 0}
          page={page}
          limit={20}
          onPageChange={setPage}
          onSearch={setSearch}
          onRefresh={() => refetch()}
          isLoading={isLoading}
          searchPlaceholder="Search by code, name..."
          getRowKey={(row) => (row as Organization).org_id}
          rowActions={(row) => {
            const org = row as Organization
            return (
              <>
                {org.approval_status === 'PENDING' && (
                  <>
                    <button
                      onClick={() => approveMutation.mutate({ id: org.org_id, status: 'APPROVED' })}
                      className="text-green-500 hover:text-green-700 p-1"
                      title="Approve"
                    >
                      <CheckCircle size={15} />
                    </button>
                    <button
                      onClick={() => approveMutation.mutate({ id: org.org_id, status: 'REJECTED' })}
                      className="text-red-400 hover:text-red-600 p-1"
                      title="Reject"
                    >
                      <XCircle size={15} />
                    </button>
                  </>
                )}
                <button onClick={() => openEdit(org)} className="text-blue-500 hover:text-blue-700 p-1">
                  <Edit2 size={15} />
                </button>
                <button
                  onClick={() => { if (confirm('Deactivate this organization?')) deleteMutation.mutate(org.org_id) }}
                  className="text-red-400 hover:text-red-600 p-1"
                >
                  <Trash2 size={15} />
                </button>
              </>
            )
          }}
        />
      </div>

      {/* Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => { setModalOpen(false); setEditingOrg(null) }}
        title={editingOrg ? 'Edit Organization' : 'New Organization'}
        size="xl"
        footer={
          <>
            <button className="btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
            <button
              className="btn-primary"
              onClick={handleSubmit(onSubmit)}
              disabled={createMutation.isPending}
            >
              {createMutation.isPending ? 'Saving...' : 'Save'}
            </button>
          </>
        }
      >
        <form className="grid grid-cols-2 gap-4">
          {/* Basic Info */}
          <div className="col-span-2 text-xs font-semibold text-gray-400 uppercase tracking-wider pt-2">Basic Information</div>
          <div>
            <label className="label">Code *</label>
            <input className="input" {...register('org_code')} placeholder="ORG001" />
          </div>
          <div>
            <label className="label">Name *</label>
            <input className="input" {...register('org_name')} placeholder="Organization name" />
          </div>
          <div>
            <label className="label">Short Name</label>
            <input className="input" {...register('org_short_name')} placeholder="Short name" />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="input" {...register('org_type')}>
              <option value="">Select type</option>
              <option>COMPANY</option>
              <option>INDIVIDUAL</option>
              <option>GOVERNMENT</option>
              <option>NGO</option>
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
            <label className="label">Country</label>
            <input className="input" {...register('country')} placeholder="UAE" />
          </div>

          {/* Roles */}
          <div className="col-span-2 text-xs font-semibold text-gray-400 uppercase tracking-wider pt-2">Roles</div>
          <div className="col-span-2 flex gap-6">
            {(['is_customer', 'is_vendor', 'is_agent', 'is_carrier'] as const).map((role) => (
              <label key={role} className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" {...register(role)} className="rounded text-blue-600" />
                <span className="text-sm text-gray-700 capitalize">{role.replace('is_', '')}</span>
              </label>
            ))}
          </div>

          {/* Contact */}
          <div className="col-span-2 text-xs font-semibold text-gray-400 uppercase tracking-wider pt-2">Contact</div>
          <div>
            <label className="label">Phone</label>
            <input className="input" {...register('phone')} placeholder="+971 4 000 0000" />
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" {...register('email')} placeholder="contact@company.com" />
          </div>
          <div className="col-span-2">
            <label className="label">Address</label>
            <input className="input" {...register('address_line1')} placeholder="Street address" />
          </div>
          <div>
            <label className="label">City</label>
            <input className="input" {...register('city')} />
          </div>
          <div>
            <label className="label">State / Province</label>
            <input className="input" {...register('state')} />
          </div>
          <div>
            <label className="label">Tax ID / VAT</label>
            <input className="input" {...register('tax_id')} />
          </div>
          <div>
            <label className="label">Credit Limit</label>
            <input className="input" type="number" {...register('credit_limit')} />
          </div>
        </form>
      </Modal>
    </div>
  )
}
