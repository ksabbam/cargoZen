// ========================
// Auth Types
// ========================
export interface User {
  user_id: number
  username: string
  email: string
  full_name: string | null
  role_name: string
  is_active: boolean
}

export interface AuthState {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  isAuthenticated: boolean
}

// ========================
// Common Types
// ========================
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface MessageResponse {
  message: string
  success: boolean
}

export interface SelectOption {
  id: number
  code: string
  name: string
  [key: string]: unknown
}

export interface FilterRule {
  field: string
  operator: 'eq' | 'ne' | 'gt' | 'lt' | 'gte' | 'lte' | 'contains' | 'in'
  value: string | number | boolean
}

export interface ColumnDef {
  key: string
  label: string
  visible: boolean
  sortable?: boolean
  width?: string
  render?: (value: unknown, row: Record<string, unknown>) => React.ReactNode
}

// ========================
// Administration Types
// ========================
export interface Organization {
  org_id: number
  org_code: string
  org_name: string
  org_short_name?: string
  group_id?: number
  group_name?: string
  org_type?: string
  is_customer: boolean
  is_vendor: boolean
  is_agent: boolean
  is_carrier: boolean
  country?: string
  phone?: string
  email?: string
  approval_status: 'PENDING' | 'APPROVED' | 'REJECTED'
  is_active: boolean
  created_at?: string
}

export interface OrgGroup {
  group_id: number
  group_code: string
  group_name: string
  group_type?: string
  description?: string
  is_active: boolean
}

export interface Airline {
  airline_id: number
  airline_code: string
  iata_code?: string
  airline_name: string
  country?: string
  is_active: boolean
}

export interface ShippingLine {
  line_id: number
  line_code: string
  scac_code?: string
  line_name: string
  country?: string
  is_active: boolean
}

export interface ChargeMaster {
  charge_id: number
  charge_code: string
  charge_name: string
  charge_type?: string
  charge_category?: string
  applicable_for?: string
  is_active: boolean
}

export interface Account {
  account_id: number
  account_code: string
  account_name: string
  account_type: string
  account_subtype?: string
  parent_account_id?: number
  is_active: boolean
}

export interface Commodity {
  commodity_id: number
  commodity_code: string
  commodity_name: string
  hs_code?: string
  commodity_group?: string
  is_dangerous: boolean
  is_active: boolean
}

export interface BusinessDimension {
  dim_id: number
  dim_code: string
  dim_name: string
  dim_type?: string
  is_active: boolean
}

export interface VendorContract {
  contract_id: number
  contract_no: string
  vendor_id: number
  vendor_name?: string
  contract_type?: string
  transport_mode?: string
  start_date?: string
  end_date?: string
  status: string
}

// ========================
// Transaction Types
// ========================
export interface ImportJob {
  job_id: number
  job_no: string
  job_date: string
  transport_mode?: string
  shipper_name?: string
  consignee_name?: string
  bl_no?: string
  flight_no?: string
  vessel_name?: string
  pol?: string
  pod?: string
  eta?: string
  ata?: string
  gross_weight?: number
  packages?: number
  status: string
}

export interface BankPayment {
  payment_id: number
  payment_no: string
  payment_date: string
  bank_name?: string
  payee_name?: string
  amount: number
  currency: string
  payment_method?: string
  status: string
}

export interface BankReceipt {
  receipt_id: number
  receipt_no: string
  receipt_date: string
  bank_name?: string
  payer_name?: string
  amount: number
  currency: string
  status: string
}

export interface JournalEntry {
  entry_id: number
  entry_no: string
  entry_date: string
  entry_type?: string
  description?: string
  total_debit?: number
  total_credit?: number
  status: string
  lines?: JournalLine[]
}

export interface JournalLine {
  line_id: number
  entry_id: number
  line_no: number
  account_code: string
  account_name: string
  debit_amount: number
  credit_amount: number
  currency: string
  narration?: string
}

export interface PurchaseBill {
  bill_id: number
  bill_no: string
  bill_date: string
  vendor_name?: string
  vendor_invoice_no?: string
  total_amount?: number
  currency: string
  due_date?: string
  status: string
}
