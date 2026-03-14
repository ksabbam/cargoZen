from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr


# ========================
# Common schemas
# ========================
class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ========================
# Auth schemas
# ========================
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    full_name: Optional[str]
    role_id: int
    role_name: Optional[str]
    is_active: bool


# ========================
# Organization schemas
# ========================
class OrganizationBase(BaseModel):
    org_code: str
    org_name: str
    org_short_name: Optional[str] = None
    group_id: Optional[int] = None
    org_type: Optional[str] = None
    is_customer: bool = False
    is_vendor: bool = False
    is_agent: bool = False
    is_carrier: bool = False
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    tax_id: Optional[str] = None
    credit_limit: Optional[float] = None
    credit_days: Optional[int] = None
    currency: str = "USD"


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    org_code: Optional[str] = None
    org_name: Optional[str] = None


class OrganizationResponse(OrganizationBase):
    org_id: int
    approval_status: str
    is_active: bool
    created_at: Optional[datetime] = None


# ========================
# Organization Group schemas
# ========================
class OrgGroupBase(BaseModel):
    group_code: str
    group_name: str
    group_type: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class OrgGroupCreate(OrgGroupBase):
    pass


class OrgGroupUpdate(OrgGroupBase):
    group_code: Optional[str] = None
    group_name: Optional[str] = None


class OrgGroupResponse(OrgGroupBase):
    group_id: int
    created_at: Optional[datetime] = None


# ========================
# Airline schemas
# ========================
class AirlineBase(BaseModel):
    airline_code: str
    iata_code: Optional[str] = None
    icao_code: Optional[str] = None
    airline_name: str
    country: Optional[str] = None
    headquarters: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    alliance: Optional[str] = None
    is_active: bool = True


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(AirlineBase):
    airline_code: Optional[str] = None
    airline_name: Optional[str] = None


class AirlineResponse(AirlineBase):
    airline_id: int
    created_at: Optional[datetime] = None


# ========================
# Shipping Line schemas
# ========================
class ShippingLineBase(BaseModel):
    line_code: str
    scac_code: Optional[str] = None
    line_name: str
    country: Optional[str] = None
    headquarters: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True


class ShippingLineCreate(ShippingLineBase):
    pass


class ShippingLineUpdate(ShippingLineBase):
    line_code: Optional[str] = None
    line_name: Optional[str] = None


class ShippingLineResponse(ShippingLineBase):
    line_id: int
    created_at: Optional[datetime] = None


# ========================
# Charge Master schemas
# ========================
class ChargeMasterBase(BaseModel):
    charge_code: str
    charge_name: str
    charge_type: Optional[str] = None
    charge_category: Optional[str] = None
    applicable_for: Optional[str] = None
    gl_account_id: Optional[int] = None
    tax_code: Optional[str] = None
    is_taxable: bool = False
    unit_type: Optional[str] = None
    is_active: bool = True


class ChargeMasterCreate(ChargeMasterBase):
    pass


class ChargeMasterUpdate(ChargeMasterBase):
    charge_code: Optional[str] = None
    charge_name: Optional[str] = None


class ChargeMasterResponse(ChargeMasterBase):
    charge_id: int
    created_at: Optional[datetime] = None


# ========================
# Account schemas
# ========================
class AccountBase(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    account_subtype: Optional[str] = None
    parent_account_id: Optional[int] = None
    description: Optional[str] = None
    is_control: bool = False
    opening_balance: float = 0
    currency: str = "USD"
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None


class AccountResponse(AccountBase):
    account_id: int
    created_at: Optional[datetime] = None


# ========================
# Commodity schemas
# ========================
class CommodityBase(BaseModel):
    commodity_code: str
    commodity_name: str
    hs_code: Optional[str] = None
    commodity_group: Optional[str] = None
    is_dangerous: bool = False
    dangerous_class: Optional[str] = None
    un_number: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class CommodityCreate(CommodityBase):
    pass


class CommodityUpdate(CommodityBase):
    commodity_code: Optional[str] = None
    commodity_name: Optional[str] = None


class CommodityResponse(CommodityBase):
    commodity_id: int
    created_at: Optional[datetime] = None


# ========================
# Business Dimension schemas
# ========================
class BusinessDimensionBase(BaseModel):
    dim_code: str
    dim_name: str
    dim_type: Optional[str] = None
    parent_dim_id: Optional[int] = None
    is_active: bool = True


class BusinessDimensionCreate(BusinessDimensionBase):
    pass


class BusinessDimensionUpdate(BusinessDimensionBase):
    dim_code: Optional[str] = None
    dim_name: Optional[str] = None


class BusinessDimensionResponse(BusinessDimensionBase):
    dim_id: int
    created_at: Optional[datetime] = None


# ========================
# Vendor Contract schemas
# ========================
class VendorContractBase(BaseModel):
    contract_no: str
    vendor_id: int
    contract_type: Optional[str] = None
    transport_mode: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    currency: str = "USD"
    remarks: Optional[str] = None
    status: str = "DRAFT"


class VendorContractCreate(VendorContractBase):
    pass


class VendorContractUpdate(VendorContractBase):
    contract_no: Optional[str] = None
    vendor_id: Optional[int] = None


class VendorContractResponse(VendorContractBase):
    contract_id: int
    created_at: Optional[datetime] = None


# ========================
# Import Job schemas
# ========================
class ImportJobBase(BaseModel):
    job_no: str
    job_date: str
    transport_mode: Optional[str] = None
    shipper_id: Optional[int] = None
    consignee_id: Optional[int] = None
    carrier_id: Optional[int] = None
    carrier_type: Optional[str] = None
    bl_no: Optional[str] = None
    flight_no: Optional[str] = None
    vessel_name: Optional[str] = None
    voyage_no: Optional[str] = None
    pol: Optional[str] = None
    pod: Optional[str] = None
    eta: Optional[str] = None
    ata: Optional[str] = None
    commodity_id: Optional[int] = None
    gross_weight: Optional[float] = None
    chargeable_weight: Optional[float] = None
    volume_cbm: Optional[float] = None
    packages: Optional[int] = None
    package_type: Optional[str] = None
    incoterms: Optional[str] = None
    freight_currency: Optional[str] = None
    freight_amount: Optional[float] = None
    status: str = "OPEN"
    remarks: Optional[str] = None


class ImportJobCreate(ImportJobBase):
    pass


class ImportJobUpdate(ImportJobBase):
    job_no: Optional[str] = None
    job_date: Optional[str] = None


class ImportJobResponse(ImportJobBase):
    job_id: int
    created_at: Optional[datetime] = None


# ========================
# Bank Payment schemas
# ========================
class BankPaymentBase(BaseModel):
    payment_no: str
    payment_date: str
    bank_account_id: Optional[int] = None
    bank_name: Optional[str] = None
    payee_id: Optional[int] = None
    payee_name: Optional[str] = None
    amount: float
    currency: str = "USD"
    exchange_rate: float = 1.0
    base_amount: Optional[float] = None
    payment_method: Optional[str] = None
    reference_no: Optional[str] = None
    narration: Optional[str] = None
    status: str = "DRAFT"


class BankPaymentCreate(BankPaymentBase):
    pass


class BankPaymentUpdate(BankPaymentBase):
    payment_no: Optional[str] = None
    payment_date: Optional[str] = None
    amount: Optional[float] = None


class BankPaymentResponse(BankPaymentBase):
    payment_id: int
    created_at: Optional[datetime] = None


# ========================
# Bank Receipt schemas
# ========================
class BankReceiptBase(BaseModel):
    receipt_no: str
    receipt_date: str
    bank_account_id: Optional[int] = None
    bank_name: Optional[str] = None
    payer_id: Optional[int] = None
    payer_name: Optional[str] = None
    amount: float
    currency: str = "USD"
    exchange_rate: float = 1.0
    base_amount: Optional[float] = None
    receipt_method: Optional[str] = None
    reference_no: Optional[str] = None
    narration: Optional[str] = None
    status: str = "DRAFT"


class BankReceiptCreate(BankReceiptBase):
    pass


class BankReceiptUpdate(BankReceiptBase):
    receipt_no: Optional[str] = None
    receipt_date: Optional[str] = None
    amount: Optional[float] = None


class BankReceiptResponse(BankReceiptBase):
    receipt_id: int
    created_at: Optional[datetime] = None


# ========================
# Journal Entry schemas
# ========================
class JournalLineCreate(BaseModel):
    line_no: Optional[int] = None
    account_id: int
    account_code: Optional[str] = None
    account_name: Optional[str] = None
    debit_amount: float = 0
    credit_amount: float = 0
    currency: str = "USD"
    narration: Optional[str] = None


class JournalEntryBase(BaseModel):
    entry_no: str
    entry_date: str
    entry_type: Optional[str] = "STANDARD"
    description: Optional[str] = None
    status: str = "DRAFT"


class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalLineCreate] = []


class JournalEntryUpdate(JournalEntryBase):
    entry_no: Optional[str] = None
    entry_date: Optional[str] = None
    lines: Optional[List[JournalLineCreate]] = None


class JournalEntryResponse(JournalEntryBase):
    entry_id: int
    total_debit: Optional[float] = None
    total_credit: Optional[float] = None
    lines: Optional[List[dict]] = None
    created_at: Optional[datetime] = None


# ========================
# Purchase Bill schemas
# ========================
class PurchaseBillLineCreate(BaseModel):
    charge_id: Optional[int] = None
    charge_name: Optional[str] = None
    quantity: float = 1
    unit_rate: float
    amount: float
    tax_amount: float = 0
    gl_account_id: Optional[int] = None


class PurchaseBillBase(BaseModel):
    bill_no: str
    bill_date: str
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    vendor_invoice_no: Optional[str] = None
    vendor_inv_date: Optional[str] = None
    amount: Optional[float] = None
    tax_amount: float = 0
    total_amount: Optional[float] = None
    currency: str = "USD"
    due_date: Optional[str] = None
    job_id: Optional[int] = None
    status: str = "DRAFT"
    remarks: Optional[str] = None


class PurchaseBillCreate(PurchaseBillBase):
    lines: List[PurchaseBillLineCreate] = []


class PurchaseBillUpdate(PurchaseBillBase):
    bill_no: Optional[str] = None
    bill_date: Optional[str] = None
    lines: Optional[List[PurchaseBillLineCreate]] = None


class PurchaseBillResponse(PurchaseBillBase):
    bill_id: int
    lines: Optional[List[dict]] = None
    created_at: Optional[datetime] = None


# ========================
# Advanced Filter schemas
# ========================
class FilterRule(BaseModel):
    field: str
    operator: str  # eq/ne/gt/lt/gte/lte/contains/in/between
    value: Any


class AdvancedFilterRequest(BaseModel):
    filters: List[FilterRule] = []
    page: int = 1
    limit: int = 20
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "ASC"


# ========================
# Column Preferences schemas
# ========================
class ColumnConfig(BaseModel):
    visible: List[str]
    order: List[str]


class ColumnPrefRequest(BaseModel):
    module_key: str
    column_config: ColumnConfig
