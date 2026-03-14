import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import apiClient from '@/api/client'
import DataTable from '@/components/common/DataTable/DataTable'
import PageHeader from '@/components/common/PageHeader'
import StatusBadge from '@/components/common/StatusBadge'

interface GenericListPageProps {
  module: string
  title: string
}

// Generic columns based on known data shapes
const getColumns = (module: string) => {
  const baseColumns: Record<string, unknown>[] = [
    { key: 'created_at', label: 'Created At', visible: false },
  ]

  const moduleColumns: Record<string, Record<string, unknown>[]> = {
    'org-groups': [
      { key: 'group_code', label: 'Code', sortable: true },
      { key: 'group_name', label: 'Name', sortable: true },
      { key: 'group_type', label: 'Type' },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
    'shipping-lines': [
      { key: 'line_code', label: 'Code', sortable: true },
      { key: 'scac_code', label: 'SCAC' },
      { key: 'line_name', label: 'Name', sortable: true },
      { key: 'country', label: 'Country' },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
    'accounts': [
      { key: 'account_code', label: 'Code', sortable: true },
      { key: 'account_name', label: 'Name', sortable: true },
      { key: 'account_type', label: 'Type' },
      { key: 'account_subtype', label: 'Sub-Type' },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
    'commodities': [
      { key: 'commodity_code', label: 'Code', sortable: true },
      { key: 'commodity_name', label: 'Name', sortable: true },
      { key: 'hs_code', label: 'HS Code' },
      { key: 'commodity_group', label: 'Group' },
      { key: 'is_dangerous', label: 'Dangerous', render: (v: unknown) => v ? <span className="badge badge-danger">Yes</span> : <span className="badge badge-gray">No</span> },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
    'business-dimensions': [
      { key: 'dim_code', label: 'Code', sortable: true },
      { key: 'dim_name', label: 'Name', sortable: true },
      { key: 'dim_type', label: 'Type' },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
    'vendor-contracts': [
      { key: 'contract_no', label: 'Contract No', sortable: true },
      { key: 'vendor_name', label: 'Vendor' },
      { key: 'contract_type', label: 'Type' },
      { key: 'transport_mode', label: 'Mode' },
      { key: 'start_date', label: 'Start' },
      { key: 'end_date', label: 'End' },
      { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
    ],
    'bank-receipts': [
      { key: 'receipt_no', label: 'Receipt No', sortable: true },
      { key: 'receipt_date', label: 'Date', sortable: true },
      { key: 'bank_name', label: 'Bank' },
      { key: 'payer_name', label: 'Payer' },
      { key: 'amount', label: 'Amount', render: (v: unknown, row: Record<string, unknown>) => `${row.currency} ${Number(v).toLocaleString()}` },
      { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
    ],
    'purchase-bills': [
      { key: 'bill_no', label: 'Bill No', sortable: true },
      { key: 'bill_date', label: 'Date', sortable: true },
      { key: 'vendor_name', label: 'Vendor' },
      { key: 'vendor_invoice_no', label: 'Vendor Invoice' },
      { key: 'total_amount', label: 'Total', render: (v: unknown, row: Record<string, unknown>) => `${row.currency} ${Number(v).toLocaleString()}` },
      { key: 'due_date', label: 'Due Date' },
      { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
    ],
    'debit-notes': [
      { key: 'dn_no', label: 'DN No', sortable: true },
      { key: 'dn_date', label: 'Date', sortable: true },
      { key: 'party_name', label: 'Party' },
      { key: 'amount', label: 'Amount', render: (v: unknown, row: Record<string, unknown>) => `${row.currency} ${Number(v).toLocaleString()}` },
      { key: 'reason', label: 'Reason' },
      { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
    ],
    'customs-export': [
      { key: 'export_no', label: 'Export No', sortable: true },
      { key: 'export_date', label: 'Date', sortable: true },
      { key: 'exporter_name', label: 'Exporter' },
      { key: 'consignee_name', label: 'Consignee' },
      { key: 'transport_mode', label: 'Mode' },
      { key: 'total_value', label: 'Value', render: (v: unknown, row: Record<string, unknown>) => `${row.currency} ${Number(v).toLocaleString()}` },
      { key: 'status', label: 'Status', render: (v: unknown) => <StatusBadge status={v as string} /> },
    ],
    'default-charges': [
      { key: 'charge_id', label: 'Charge ID' },
      { key: 'job_type', label: 'Job Type' },
      { key: 'transport_mode', label: 'Mode' },
      { key: 'amount', label: 'Amount' },
      { key: 'currency', label: 'Currency' },
    ],
    'system-settings': [
      { key: 'setting_key', label: 'Key' },
      { key: 'setting_group', label: 'Group' },
      { key: 'setting_value', label: 'Value', render: (v: unknown) => String(v) },
      { key: 'data_type', label: 'Type' },
      { key: 'description', label: 'Description' },
    ],
    'tools': [],
    'custom-clearing': [
      { key: 'clearing_type', label: 'Type' },
      { key: 'port_code', label: 'Port Code' },
      { key: 'port_name', label: 'Port Name' },
      { key: 'customs_authority', label: 'Authority' },
      { key: 'is_active', label: 'Status', render: (v: unknown) => <StatusBadge status={v ? 'ACTIVE' : 'INACTIVE'} /> },
    ],
  }

  return moduleColumns[module] || baseColumns
}

export default function GenericListPage({ module, title }: GenericListPageProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const queryClient = useQueryClient()

  const apiPath = `/api/${module}`

  const { data, isLoading, refetch } = useQuery({
    queryKey: [module, page, search],
    queryFn: async () => {
      try {
        const res = await apiClient.get(apiPath, {
          params: { page, limit: 20, search: search || undefined }
        })
        return res.data
      } catch {
        return { data: [], total: 0, page: 1, limit: 20, total_pages: 1 }
      }
    },
  })

  const columns = getColumns(module)

  if (module === 'tools') {
    return (
      <div className="flex flex-col h-full">
        <PageHeader title="Tools" subtitle="System utilities and maintenance tools" />
        <div className="flex-1 p-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              { label: 'Data Export', desc: 'Export master data to Excel/CSV' },
              { label: 'Data Import', desc: 'Bulk import records from templates' },
              { label: 'Audit Trail', desc: 'View system activity logs' },
              { label: 'Backup', desc: 'Backup system configuration' },
              { label: 'User Management', desc: 'Manage users and roles' },
              { label: 'Cache Clear', desc: 'Clear application cache' },
            ].map((tool) => (
              <div key={tool.label} className="card p-5 hover:shadow-md transition-shadow cursor-pointer">
                <h3 className="font-semibold text-gray-800">{tool.label}</h3>
                <p className="text-sm text-gray-500 mt-1">{tool.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <PageHeader title={title} />
      <div className="flex-1 p-6 overflow-hidden">
        <DataTable
          columns={columns as unknown as Parameters<typeof DataTable>[0]['columns']}
          data={Array.isArray(data) ? data : (data?.data || [])}
          total={data?.total || 0}
          page={page}
          limit={20}
          onPageChange={setPage}
          onSearch={columns.length > 0 ? setSearch : undefined}
          onRefresh={() => refetch()}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
