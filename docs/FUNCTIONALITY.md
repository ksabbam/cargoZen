# 🚢 CargoZen — Functional Specification Document

> **Freight & Logistics Management System**
> Version 1.0.0 | Date: March 22, 2026

---

## Table of Contents

1. [Document Purpose](#1-document-purpose)
2. [System Overview](#2-system-overview)
3. [User Roles & Permissions](#3-user-roles--permissions)
4. [Authentication Module](#4-authentication-module)
5. [Dashboard](#5-dashboard)
6. [Administration Modules](#6-administration-modules)
   - 6.1 [Organizations](#61-organizations)
   - 6.2 [Organization Groups](#62-organization-groups)
   - 6.3 [Airlines](#63-airlines)
   - 6.4 [Shipping Lines](#64-shipping-lines)
   - 6.5 [Chart of Accounts](#65-chart-of-accounts)
   - 6.6 [Charge Master](#66-charge-master)
   - 6.7 [Default Charges](#67-default-charges)
   - 6.8 [Business Dimensions](#68-business-dimensions)
   - 6.9 [Commodities](#69-commodities)
   - 6.10 [Vendor Contracts](#610-vendor-contracts)
   - 6.11 [Custom Clearing Setup](#611-custom-clearing-setup)
   - 6.12 [System Settings](#612-system-settings)
7. [Transaction Modules](#7-transaction-modules)
   - 7.1 [Import Jobs](#71-import-jobs)
   - 7.2 [Bank Payments](#72-bank-payments)
   - 7.3 [Bank Receipts](#73-bank-receipts)
   - 7.4 [Journal Entries](#74-journal-entries)
   - 7.5 [General Debit Notes](#75-general-debit-notes)
   - 7.6 [Purchase Bills](#76-purchase-bills)
   - 7.7 [Customs Export](#77-customs-export)
8. [Reports Module](#8-reports-module)
   - 8.1 [Import Jobs Report](#81-import-jobs-report)
   - 8.2 [Financial Ledger Report](#82-financial-ledger-report)
   - 8.3 [AP Aging Report](#83-ap-aging-report)
9. [Tools & Utilities](#9-tools--utilities)
10. [Common UI Functionality](#10-common-ui-functionality)
11. [Business Rules & Validations](#11-business-rules--validations)
12. [Glossary](#12-glossary)

---

## 1. Document Purpose

This document describes the **complete functional specification** of the CargoZen Freight & Logistics Management System. It covers every user-facing feature, business rule, data field, workflow, and user interaction across all modules.

**Audience:** Business analysts, QA engineers, developers, project stakeholders.

---

## 2. System Overview

CargoZen is an enterprise web application for freight forwarding companies to manage:

- **Master Data** — Organizations, carriers, charges, accounts, commodities
- **Freight Operations** — Import job creation, tracking, and charge management
- **Financial Transactions** — Payments, receipts, journal entries, purchase bills, debit notes
- **Customs Compliance** — Export declarations, clearing procedure setup
- **Reporting** — Operational and financial reporting with filters

### Navigation Structure

```
┌─────────────────────────────────────────────────┐
│  SIDEBAR NAVIGATION                              │
├─────────────────────────────────────────────────┤
│  📊 Dashboard                                    │
│                                                  │
│  ⚙️  Administration ▼                             │
│     ├── 🏢 Organizations                         │
│     ├── 👥 Org Groups                            │
│     ├── ✈️  Airlines                              │
│     ├── 🚢 Shipping Lines                        │
│     ├── 📖 Chart of Accounts                     │
│     ├── 🏷️  Charge Master                         │
│     ├── ⭐ Default Charges                       │
│     ├── 📐 Biz Dimensions                        │
│     ├── 📦 Commodities                           │
│     ├── 📄 Vendor Contracts                      │
│     ├── ⚓ Custom Clearing                       │
│     └── ⚙️  System Settings                       │
│                                                  │
│  💰 Transactions ▼                               │
│     ├── 💼 Import Jobs                           │
│     ├── 💳 Bank Payments                         │
│     ├── 🧾 Bank Receipts                         │
│     ├── 📖 Journal Entries                       │
│     ├── 📄 Debit Notes                           │
│     ├── 📄 Purchase Bills                        │
│     └── ✈️  Customs Export                        │
│                                                  │
│  📊 Reports                                      │
│  🔧 Tools                                        │
│                                                  │
│  🚪 Logout                                       │
└─────────────────────────────────────────────────┘
```

---

## 3. User Roles & Permissions

### 3.1 Role-Based Access Control (RBAC)

The system implements fine-grained, module-level permissions.

| Permission | Description |
|-----------|-------------|
| **can_view** | User can see the module's list page and records |
| **can_create** | User can create new records (shows "New" button) |
| **can_edit** | User can modify existing records (shows "Edit" action) |
| **can_delete** | User can soft-delete/deactivate records (shows "Delete" action) |
| **can_export** | User can download/export data from the module |
| **can_approve** | User can approve or reject records (e.g., Organization approval) |

### 3.2 Default Roles

| Role | Description | Typical Permissions |
|------|-------------|-------------------|
| **Admin** | System administrator | Full access to all modules |
| **Operator** | Day-to-day user | View/Create/Edit on transactions; View on admin |
| **Viewer** | Read-only user | View-only access across all modules |

### 3.3 Permission Matrix

Each role has permissions configured per module in the `ROLE_PERMISSIONS` table:

| Module | Admin | Operator | Viewer |
|--------|-------|----------|--------|
| Organizations | View/Create/Edit/Delete/Approve | View/Create/Edit | View |
| Import Jobs | View/Create/Edit/Delete | View/Create/Edit | View |
| Bank Payments | View/Create/Edit/Delete | View/Create/Edit | View |
| Reports | View/Export | View/Export | View |
| System Settings | View/Edit | — | — |

---

## 4. Authentication Module

### 4.1 Login

| Item | Detail |
|------|--------|
| **Screen** | `/login` |
| **Purpose** | Authenticate user and start a session |
| **Access** | Public (unauthenticated users only) |

**User Interface:**
- Username field (text input, required)
- Password field (password input, required)
- "Sign In" button
- Application logo and title displayed

**Functionality:**
1. User enters username and password
2. System validates credentials against the database
3. Password is verified against bcrypt hash (12 rounds)
4. On success:
   - Server generates JWT access token (60-minute expiry)
   - Server generates JWT refresh token (24-hour expiry)
   - Server updates `last_login` timestamp in database
   - Server stores refresh token in database
   - Client stores user profile and tokens in Zustand store
   - Client redirects to Dashboard (`/`)
5. On failure:
   - "Incorrect username or password" error displayed
   - Inactive accounts receive "Account is inactive" message

**Default Credentials:**
- Username: `admin` | Password: `Admin@123`

**Fields:**

| Field | Type | Required | Validation |
|-------|------|----------|-----------|
| Username | Text | Yes | Non-empty string |
| Password | Password | Yes | Non-empty string |

### 4.2 Session Management

| Feature | Detail |
|---------|--------|
| **Access Token** | JWT, HS256, 60-minute TTL, sent as `Bearer` header |
| **Refresh Token** | JWT, HS256, 24-hour TTL, stored in localStorage (persisted) |
| **Auto-Refresh** | When a 401 response is received, the client automatically calls `/api/auth/refresh` to obtain a new access token. Failed requests are queued and retried. |
| **Token Blacklist** | On logout, the token JTI is inserted into `TOKEN_BLACKLIST` table. All authenticated requests check against this list. |
| **Protected Routes** | All routes except `/login` require authentication. Unauthenticated users are redirected to `/login`. |

### 4.3 Logout

**Functionality:**
1. User clicks "Logout" in the sidebar
2. Client calls `POST /api/auth/logout`
3. Server adds current token JTI to the blacklist
4. Client clears all auth state from Zustand store
5. Client redirects to `/login`

### 4.4 User Profile

| Endpoint | `GET /api/auth/me` |
|----------|---------------------|
| **Returns** | user_id, username, email, full_name, role_name, is_active |

---

## 5. Dashboard

| Item | Detail |
|------|--------|
| **Screen** | `/` (root path) |
| **Purpose** | Overview of key business metrics and quick actions |
| **Access** | Authenticated users |
| **Auto-Refresh** | Data refreshes every 60 seconds |

### 5.1 KPI Cards

Five summary cards displayed at the top:

| KPI Card | Source | Format | Click Navigation |
|----------|--------|--------|-----------------|
| **Active Jobs** | Count of import jobs with status OPEN or IN_PROGRESS | Number | → `/transactions/import-jobs` |
| **Today's Payments** | Sum of bank payment amounts for current date | Currency (USD) | → `/transactions/bank-payments` |
| **Today's Receipts** | Sum of bank receipt amounts for current date | Currency (USD) | → `/transactions/bank-receipts` |
| **Pending Approvals** | Count of organizations with approval_status = PENDING | Number | → `/administration/organizations` |
| **Total Organizations** | Count of active organizations | Number | → `/administration/organizations` |

### 5.2 Quick Actions

Six shortcut buttons for rapid navigation:

| Action | Navigates To |
|--------|-------------|
| New Import Job | `/transactions/import-jobs` |
| Bank Payment | `/transactions/bank-payments` |
| Bank Receipt | `/transactions/bank-receipts` |
| Journal Entry | `/transactions/journal-entries` |
| Purchase Bill | `/transactions/purchase-bills` |
| Customs Export | `/transactions/customs-export` |

### 5.3 Jobs by Transport Mode

A horizontal bar chart showing count of import jobs per transport mode:

| Mode | Color |
|------|-------|
| SEA | Blue (#007AFF) |
| AIR | Teal (#30B0C7) |
| ROAD | Orange (#FF9500) |

### 5.4 Recent Jobs

A table showing the 5 most recently created import jobs:

| Column | Description |
|--------|-------------|
| Job No | Unique job reference number |
| Date | Job creation date |
| Mode | Transport mode (SEA/AIR/ROAD) |
| Shipper | Shipper organization name |
| Status | Job status badge (OPEN/IN_PROGRESS/COMPLETED/CANCELLED) |

---

## 6. Administration Modules

All administration modules share a common UI pattern (described in [§10 Common UI Functionality](#10-common-ui-functionality)). Each section below details the module-specific fields, business rules, and functionality.

---

### 6.1 Organizations

| Item | Detail |
|------|--------|
| **Screen** | `/administration/organizations` |
| **Purpose** | Manage business partners: customers, vendors, agents, and carriers |
| **API Endpoint** | `GET/POST /api/organizations`, `GET/PUT/DELETE /api/organizations/{id}` |
| **Special Feature** | Approval workflow (PENDING → APPROVED / REJECTED) |

#### 6.1.1 List View

| Feature | Detail |
|---------|--------|
| **Columns** | Org Code, Org Name, Short Name, Type, Group, Customer/Vendor/Agent/Carrier flags, Country, Approval Status, Active |
| **Search** | By org_code, org_name, or org_short_name (ILIKE) |
| **Filters** | Organization type (dropdown), Approval status (PENDING/APPROVED/REJECTED), Active status (Yes/No) |
| **Sorting** | By org_name (default ASC), sortable columns |
| **Pagination** | 20 records per page, page navigation |

#### 6.1.2 Create/Edit Form

| Field | Type | Required | Validation | Description |
|-------|------|----------|-----------|-------------|
| Org Code | Text | Yes (Create) | Unique, alphanumeric | Unique identifier for the organization |
| Org Name | Text | Yes | Non-empty | Full legal name |
| Short Name | Text | No | — | Abbreviated name for display |
| Group | Dropdown | No | Valid group_id | Link to Organization Group |
| Org Type | Dropdown | No | — | Classification type |
| Is Customer | Checkbox | No | — | Organization acts as a customer |
| Is Vendor | Checkbox | No | — | Organization acts as a vendor |
| Is Agent | Checkbox | No | — | Organization acts as a freight agent |
| Is Carrier | Checkbox | No | — | Organization acts as a carrier |
| Address Line 1 | Text | No | — | Street address |
| Address Line 2 | Text | No | — | Additional address |
| City | Text | No | — | City |
| State | Text | No | — | State/Province |
| Country | Text | No | — | Country |
| Postal Code | Text | No | — | ZIP/Postal code |
| Phone | Text | No | — | Contact phone number |
| Email | Text | No | Valid email format | Contact email |
| Website | Text | No | — | Organization website URL |
| Tax ID | Text | No | — | Tax identification number |
| Credit Limit | Number | No | ≥ 0 | Maximum credit allowed (USD) |
| Credit Days | Number | No | ≥ 0 | Payment terms in days |
| Currency | Dropdown | No | Default: USD | Base currency |

#### 6.1.3 Approval Workflow

| Action | Endpoint | Description |
|--------|----------|-------------|
| **Approve** | `PATCH /api/organizations/{id}/approval` | Sets `approval_status = 'APPROVED'`, records `approved_by` and `approval_date` |
| **Reject** | `PATCH /api/organizations/{id}/approval` | Sets `approval_status = 'REJECTED'`, records `approved_by` and `approval_date` |
| **Reset** | `PATCH /api/organizations/{id}/approval` | Sets `approval_status = 'PENDING'` |

**Business Rule:** Only users with `can_approve` permission on the Organizations module can approve/reject.

#### 6.1.4 Search-Select (Lookup)

| Endpoint | `GET /api/organizations/search-select?q=&type_filter=` |
|----------|-------------------------------------------------------|
| **Purpose** | Provides type-ahead search for organization dropdowns in other modules (Import Jobs, Payments, etc.) |
| **Filters** | Only returns active, approved organizations. Can filter by type (customer/vendor/agent). |
| **Returns** | id, code, name (max 50 results) |

#### 6.1.5 Delete (Soft)

Organizations are never physically deleted. The "Delete" action sets `is_active = FALSE`.

---

### 6.2 Organization Groups

| Item | Detail |
|------|--------|
| **Screen** | `/administration/org-groups` |
| **Purpose** | Group organizations by category for classification and reporting |
| **API Endpoint** | `GET/POST /api/org-groups`, `GET/PUT/DELETE /api/org-groups/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Group Code | Text | Yes | Unique identifier |
| Group Name | Text | Yes | Descriptive name |
| Group Type | Text | No | Category (e.g., "Customer Group", "Vendor Group") |
| Description | Text | No | Additional details |
| Is Active | Toggle | Yes | Active/Inactive status (default: Active) |

#### Functionality
- **List:** Paginated grid with search by code/name, filter by active status
- **Create:** Add new group with code, name, type, description
- **Edit:** Modify group name, type, description, active status
- **Delete:** Soft-delete (sets `is_active = FALSE`)

---

### 6.3 Airlines

| Item | Detail |
|------|--------|
| **Screen** | `/administration/airlines` |
| **Purpose** | Maintain airline carrier master data for air freight operations |
| **API Endpoint** | `GET/POST /api/airlines`, `GET/PUT/DELETE /api/airlines/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Airline Code | Text | Yes | Unique internal code |
| IATA Code | Text | No | 2-letter IATA designator (e.g., "EK", "QR") |
| ICAO Code | Text | No | 3-letter ICAO designator (e.g., "UAE", "QTR") |
| Airline Name | Text | Yes | Full airline name |
| Country | Text | No | Country of registration |
| Headquarters | Text | No | HQ city/location |
| Phone | Text | No | Contact phone |
| Email | Text | No | Contact email |
| Alliance | Text | No | Airline alliance (Star Alliance, oneworld, SkyTeam) |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **List:** Paginated grid with search by airline_code, airline_name, or iata_code
- **Search-Select:** `GET /api/airlines/search-select?q=` — Used as dropdown in Import Jobs when carrier_type = AIRLINE
- **Create/Edit/Delete:** Standard CRUD operations

#### Usage
Airlines are referenced in Import Jobs when `transport_mode = AIR` and `carrier_type = AIRLINE`.

---

### 6.4 Shipping Lines

| Item | Detail |
|------|--------|
| **Screen** | `/administration/shipping-lines` |
| **Purpose** | Maintain ocean carrier master data for sea freight operations |
| **API Endpoint** | `GET/POST /api/shipping-lines`, `GET/PUT/DELETE /api/shipping-lines/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Line Code | Text | Yes | Unique internal code |
| SCAC Code | Text | No | Standard Carrier Alpha Code (e.g., "MAEU" for Maersk) |
| Line Name | Text | Yes | Full shipping line name |
| Country | Text | No | Country of registration |
| Headquarters | Text | No | HQ location |
| Phone | Text | No | Contact phone |
| Email | Text | No | Contact email |
| Website | Text | No | Website URL |
| Is Active | Toggle | Yes | Default: Active |

#### Usage
Shipping Lines are referenced in Import Jobs when `transport_mode = SEA` and `carrier_type = SHIPPING_LINE`.

---

### 6.5 Chart of Accounts

| Item | Detail |
|------|--------|
| **Screen** | `/administration/accounts` |
| **Purpose** | Define the hierarchical General Ledger (GL) accounts for financial bookkeeping |
| **API Endpoint** | `GET/POST /api/accounts`, `GET/PUT /api/accounts/{id}` |
| **Special Feature** | Hierarchical structure (parent-child accounts) |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Account Code | Text | Yes | Unique GL account code (e.g., "1100", "2200") |
| Account Name | Text | Yes | Account description |
| Account Type | Dropdown | Yes | ASSET / LIABILITY / EQUITY / INCOME / EXPENSE |
| Account Subtype | Text | No | Further classification (e.g., "Current Asset", "Fixed Asset") |
| Parent Account | Dropdown | No | Parent account for hierarchy (self-referencing) |
| Description | Text | No | Detailed explanation |
| Opening Balance | Number | No | Starting balance (default: 0) |
| Currency | Dropdown | No | Account currency (default: USD) |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **Hierarchical Structure:** Accounts can have parent-child relationships forming a tree structure
- **Search:** By account_code or account_name
- **Filter:** By account_type (ASSET/LIABILITY/EQUITY/INCOME/EXPENSE)
- **Pagination:** 100 records per page (larger default than other modules)
- **Usage:** Linked to Charge Master (GL Account), Journal Lines, Purchase Bill Lines

---

### 6.6 Charge Master

| Item | Detail |
|------|--------|
| **Screen** | `/administration/charge-master` |
| **Purpose** | Define all freight-related charges that can be applied to jobs and invoices |
| **API Endpoint** | `GET/POST /api/charge-master`, `GET/PUT/DELETE /api/charge-master/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Charge Code | Text | Yes | Unique charge identifier (e.g., "FREIGHT", "THC", "DOC") |
| Charge Name | Text | Yes | Full charge description |
| Charge Type | Dropdown | No | FREIGHT / CUSTOMS / LOCAL / HANDLING / MISC |
| Charge Category | Text | No | Sub-category for grouping |
| Applicable For | Dropdown | No | IMPORT / EXPORT / BOTH |
| GL Account | Dropdown | No | Link to Chart of Accounts (for journal posting) |
| Tax Code | Text | No | Applicable tax code |
| Is Taxable | Checkbox | No | Whether tax applies (default: No) |
| Unit Type | Dropdown | No | LUMP / PER_KG / PER_CBM / PER_UNIT |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **Search:** By charge_code or charge_name
- **Filters:** By charge_type, applicable_for, active status
- **Filter Logic:** When filtering by applicable_for = "IMPORT", also returns charges with "BOTH"
- **Usage:** Referenced in Job Charges, Default Charges, Vendor Contract Rates, Purchase Bill Lines

---

### 6.7 Default Charges

| Item | Detail |
|------|--------|
| **Screen** | `/administration/default-charges` |
| **Purpose** | Pre-configure standard charges by job type and transport mode for auto-population |
| **API Endpoint** | `GET/POST /api/default-charges`, `GET/PUT/DELETE /api/default-charges/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Charge | Dropdown | Yes | Select from Charge Master (charge_id) |
| Job Type | Dropdown | No | IMPORT / EXPORT |
| Transport Mode | Dropdown | No | AIR / SEA / ROAD |
| Amount | Number | No | Default charge amount (default: 0) |
| Currency | Dropdown | No | Default: USD |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **List:** Shows charge_code and charge_name from the linked Charge Master
- **Filters:** By job_type, transport_mode
- **Business Rule:** When creating a new Import Job, the system can auto-populate charges based on matching default charges for the selected job type and transport mode

---

### 6.8 Business Dimensions

| Item | Detail |
|------|--------|
| **Screen** | `/administration/business-dimensions` |
| **Purpose** | Define cost tracking dimensions: departments, branches, cost centers, and projects |
| **API Endpoint** | `GET/POST /api/business-dimensions`, `GET/PUT/DELETE /api/business-dimensions/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Dim Code | Text | Yes | Unique dimension code |
| Dim Name | Text | Yes | Dimension description |
| Dim Type | Dropdown | No | DEPARTMENT / BRANCH / COST_CENTER / PROJECT |
| Parent Dimension | Dropdown | No | Parent dimension for hierarchy (self-referencing) |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **Hierarchical Structure:** Dimensions support parent-child relationships
- **Search:** By dim_code or dim_name
- **Filter:** By dim_type
- **Usage:** Referenced in Journal Lines for cost center/department allocation

---

### 6.9 Commodities

| Item | Detail |
|------|--------|
| **Screen** | `/administration/commodities` |
| **Purpose** | Maintain cargo/commodity types with HS codes and dangerous goods classification |
| **API Endpoint** | `GET/POST /api/commodities`, `GET/PUT/DELETE /api/commodities/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Commodity Code | Text | Yes | Unique commodity identifier |
| Commodity Name | Text | Yes | Full commodity description |
| HS Code | Text | No | Harmonized System tariff code (e.g., "8471.30") |
| Commodity Group | Text | No | Classification group |
| Is Dangerous | Checkbox | No | Flag for dangerous goods (default: No) |
| Dangerous Class | Text | No | IMDG class (e.g., "3", "6.1") — shown when Is Dangerous = Yes |
| UN Number | Text | No | UN identification number (e.g., "UN1203") — shown when Is Dangerous = Yes |
| Description | Text | No | Additional details |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **Search:** By commodity_code, commodity_name, or hs_code
- **Dangerous Goods Indicator:** The list view displays a colored badge ("Yes"=red, "No"=gray) for the Is Dangerous column
- **Usage:** Referenced in Import Jobs (commodity_id) and Customs Export

---

### 6.10 Vendor Contracts

| Item | Detail |
|------|--------|
| **Screen** | `/administration/vendor-contracts` |
| **Purpose** | Manage rate agreements with vendors for freight, trucking, customs services |
| **API Endpoint** | `GET/POST /api/vendor-contracts`, `GET/PUT /api/vendor-contracts/{id}` |

#### Fields — Contract Header

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Contract No | Text | Yes | Unique contract reference number |
| Vendor | Dropdown | Yes | Select from Organizations (vendor_id) |
| Contract Type | Dropdown | No | AIR_FREIGHT / SEA_FREIGHT / TRUCKING / CUSTOMS |
| Transport Mode | Dropdown | No | AIR / SEA / ROAD |
| Start Date | Date | No | Contract validity start |
| End Date | Date | No | Contract validity end |
| Currency | Dropdown | No | Default: USD |
| Remarks | Text | No | Additional notes |
| Status | Dropdown | No | DRAFT / ACTIVE / EXPIRED / CANCELLED (default: DRAFT) |

#### Fields — Contract Rates (Line Items)

| Field | Type | Description |
|-------|------|-------------|
| Charge | Dropdown | From Charge Master |
| Origin | Text | Origin port/city |
| Destination | Text | Destination port/city |
| Rate | Number | Unit rate |
| Unit | Text | Unit of measure |
| Min Charge | Number | Minimum charge amount |
| Valid From | Date | Rate validity start |
| Valid To | Date | Rate validity end |

#### Status Workflow
```
DRAFT → ACTIVE → EXPIRED
                → CANCELLED
```

---

### 6.11 Custom Clearing Setup

| Item | Detail |
|------|--------|
| **Screen** | `/administration/custom-clearing` |
| **Purpose** | Configure customs clearance procedures by port for import and export operations |
| **API Endpoint** | `GET/POST /api/custom-clearing`, `GET/PUT/DELETE /api/custom-clearing/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Clearing Type | Dropdown | Yes | IMPORT / EXPORT |
| Port Code | Text | No | Port code (e.g., "JNPT", "AEJEA") |
| Port Name | Text | No | Full port name |
| Customs Authority | Text | No | Name of customs authority |
| Broker | Dropdown | No | Select from Organizations (broker_org_id) |
| Procedures | JSON Array | No | Step-by-step customs procedure list |
| Required Documents | JSON Array | No | List of documents needed for clearance |
| Is Active | Toggle | Yes | Default: Active |

#### Functionality
- **Search:** By port_code, port_name, or customs_authority
- **Filter:** By clearing_type (IMPORT/EXPORT)
- **JSON Fields:** Procedures and Required Documents are stored as JSON arrays, allowing flexible configuration per port

---

### 6.12 System Settings

| Item | Detail |
|------|--------|
| **Screen** | `/administration/system-settings` |
| **Purpose** | Global application configuration (key-value pairs) |
| **API Endpoint** | `GET /api/system-settings`, `PUT /api/system-settings/{key}` |

#### Functionality
- **Read-Only List:** All settings displayed grouped by `setting_group`
- **Edit:** Individual settings can be updated by key
- **No Create/Delete:** Settings are pre-seeded; users can only modify values
- **Data Types:** STRING, NUMBER, BOOLEAN, JSON
- **Example Settings:** Company name, default currency, auto-numbering formats, date format preferences

#### Fields Per Setting

| Field | Type | Description |
|-------|------|-------------|
| Setting Key | Text (read-only) | Unique key identifier |
| Setting Value | Dynamic | Value (type depends on data_type) |
| Setting Group | Text (read-only) | Category grouping |
| Data Type | Text (read-only) | STRING / NUMBER / BOOLEAN / JSON |
| Description | Text (read-only) | Explanation of the setting |

---

## 7. Transaction Modules

---

### 7.1 Import Jobs

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/import-jobs` |
| **Purpose** | Create and manage freight import jobs (Sea, Air, Road) with charges |
| **API Endpoint** | `GET/POST /api/import-jobs`, `GET/PUT /api/import-jobs/{id}` |
| **Special Feature** | Master-detail: Job header + child charge lines |

#### 7.1.1 List View

| Column | Description |
|--------|-------------|
| Job No | Unique job reference |
| Job Date | Date of job creation |
| Transport Mode | SEA / AIR / ROAD |
| B/L No | Bill of Lading or Air Waybill number |
| Shipper | Shipper organization name |
| Consignee | Consignee organization name |
| POL | Port of Loading |
| POD | Port of Discharge |
| ETA | Estimated Time of Arrival |
| Status | OPEN / IN_PROGRESS / COMPLETED / CANCELLED |

**Search:** By job_no or bl_no
**Filters:** Status, Transport Mode, Date Range (from/to)
**Sorting:** By job_date DESC (most recent first)

#### 7.1.2 Create/Edit Form — Job Header

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Job No | Text | Yes | Unique reference (e.g., "IMP-2026-0001") |
| Job Date | Date | Yes | Date of the job |
| Transport Mode | Dropdown | No | SEA / AIR / ROAD |
| Shipper | Search-Select | No | From Organizations (type: customer/agent) |
| Consignee | Search-Select | No | From Organizations |
| Carrier ID | Search-Select | No | From Airlines or Shipping Lines |
| Carrier Type | Dropdown | No | AIRLINE / SHIPPING_LINE |
| B/L No | Text | No | Bill of Lading / Air Waybill number |
| Flight No | Text | No | Flight number (for AIR mode) |
| Vessel Name | Text | No | Ship name (for SEA mode) |
| Voyage No | Text | No | Voyage number (for SEA mode) |
| POL | Text | No | Port of Loading |
| POD | Text | No | Port of Discharge |
| ETA | Date | No | Estimated arrival date |
| ATA | Date | No | Actual arrival date |
| Commodity | Search-Select | No | From Commodities master |
| Gross Weight | Number | No | In kilograms |
| Chargeable Weight | Number | No | In kilograms |
| Volume (CBM) | Number | No | Cubic meters |
| Packages | Number | No | Number of packages |
| Package Type | Text | No | Carton, Pallet, Drum, etc. |
| Incoterms | Dropdown | No | FOB, CIF, EXW, DDP, etc. |
| Freight Currency | Dropdown | No | Currency for freight amount |
| Freight Amount | Number | No | Total freight value |
| Status | Dropdown | No | OPEN (default) / IN_PROGRESS / COMPLETED / CANCELLED |
| Remarks | Textarea | No | Free-text notes |

#### 7.1.3 Job Charges (Line Items)

Each import job can have multiple charge lines:

| Field | Type | Description |
|-------|------|-------------|
| Charge | Dropdown | From Charge Master |
| Charge Name | Text (auto-fill) | Name of the selected charge |
| Quantity | Number | Default: 1 |
| Unit Type | Text | LUMP / PER_KG / PER_CBM / PER_UNIT |
| Rate | Number | Unit rate |
| Currency | Dropdown | Default: USD |
| Amount | Number | quantity × rate |
| Tax Amount | Number | Tax on this charge (default: 0) |
| Total Amount | Number | amount + tax_amount |
| Vendor | Search-Select | Vendor responsible for this charge |

**Business Rules:**
- Charge lines are saved atomically with the job (single transaction)
- When fetching a job by ID, all associated charge lines are returned in a `charges` array

#### 7.1.4 Status Workflow

```
OPEN → IN_PROGRESS → COMPLETED
                   → CANCELLED
```

---

### 7.2 Bank Payments

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/bank-payments` |
| **Purpose** | Record outgoing payments to vendors, agents, and other parties |
| **API Endpoint** | `GET/POST /api/bank-payments`, `GET/PUT /api/bank-payments/{id}` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Payment No | Text | Yes | Unique payment reference |
| Payment Date | Date | Yes | Date of payment |
| Bank Account | Dropdown | No | From Chart of Accounts (bank accounts) |
| Bank Name | Text | No | Name of the bank |
| Payee | Search-Select | No | From Organizations (payee_id) |
| Payee Name | Text | No | Auto-filled or manual entry |
| Amount | Number | Yes | Payment amount |
| Currency | Dropdown | No | Default: USD |
| Exchange Rate | Number | No | Default: 1.0 |
| Base Amount | Number | No | Amount in base currency (= amount × exchange_rate) |
| Payment Method | Dropdown | No | WIRE / CHEQUE / CASH / ONLINE |
| Reference No | Text | No | Bank reference / cheque number |
| Narration | Textarea | No | Description of payment |
| Status | Dropdown | No | DRAFT (default) / POSTED / CANCELLED |

#### Payment Allocations

Payments can be allocated to specific jobs:

| Field | Type | Description |
|-------|------|-------------|
| Job | Dropdown | From Import Jobs |
| Invoice Ref | Text | Invoice reference number |
| Amount | Number | Amount allocated to this job |

#### Search & Filters
- **Search:** By payment_no, payee_name, or bank_name
- **Filters:** Status, Date Range (from/to)

#### Status Workflow
```
DRAFT → POSTED → CANCELLED
```

---

### 7.3 Bank Receipts

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/bank-receipts` |
| **Purpose** | Record incoming payments received from customers |
| **API Endpoint** | `GET/POST /api/bank-receipts` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Receipt No | Text | Yes | Unique receipt reference |
| Receipt Date | Date | Yes | Date of receipt |
| Bank Account | Dropdown | No | From Chart of Accounts |
| Bank Name | Text | No | Name of the bank |
| Payer | Search-Select | No | From Organizations (payer_id) |
| Payer Name | Text | No | Auto-filled or manual |
| Amount | Number | Yes | Receipt amount |
| Currency | Dropdown | No | Default: USD |
| Exchange Rate | Number | No | Default: 1.0 |
| Base Amount | Number | No | Amount in base currency |
| Receipt Method | Dropdown | No | WIRE / CHEQUE / CASH / ONLINE |
| Reference No | Text | No | Bank reference number |
| Narration | Textarea | No | Description |
| Status | Dropdown | No | DRAFT (default) / POSTED |

#### Search & Filters
- **Search:** By receipt_no or payer_name
- **Filters:** Status

---

### 7.4 Journal Entries

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/journal-entries` |
| **Purpose** | Double-entry bookkeeping — record debits and credits across GL accounts |
| **API Endpoint** | `GET/POST /api/journal-entries`, `GET /api/journal-entries/{id}` |
| **Special Feature** | Master-detail: Entry header + multiple debit/credit lines |

#### Fields — Entry Header

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Entry No | Text | Yes | Unique entry reference |
| Entry Date | Date | Yes | Date of the entry |
| Entry Type | Dropdown | No | STANDARD / ADJUSTING / REVERSING / OPENING |
| Description | Text | No | Purpose of the journal entry |
| Status | Dropdown | No | DRAFT (default) / POSTED / REVERSED |

#### Fields — Journal Lines

Each entry has multiple debit/credit lines:

| Field | Type | Description |
|-------|------|-------------|
| Line No | Number | Sequential line number (auto-generated) |
| Account | Dropdown | From Chart of Accounts |
| Account Code | Text (auto-fill) | GL account code |
| Account Name | Text (auto-fill) | GL account name |
| Debit Amount | Number | Debit value (default: 0) |
| Credit Amount | Number | Credit value (default: 0) |
| Currency | Dropdown | Default: USD |
| Exchange Rate | Number | Default: 1.0 |
| Dimension | Dropdown | From Business Dimensions (optional) |
| Narration | Text | Line-level description |

#### Business Rules
- **Balanced Entry:** `total_debit` must equal `total_credit` (auto-calculated from lines)
- **Auto-Totals:** Header's `total_debit` and `total_credit` are computed from the sum of all lines
- **Journal Lines** are saved atomically with the entry header
- Each line must have either a debit OR credit amount (not both)

#### Status Workflow
```
DRAFT → POSTED → REVERSED
```

#### Search & Filters
- **Search:** By entry_no or description
- **Filters:** Status

---

### 7.5 General Debit Notes

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/debit-notes` |
| **Purpose** | Issue debit notes to parties (customers or vendors) for charges or adjustments |
| **API Endpoint** | `GET/POST /api/debit-notes` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| DN No | Text | Yes | Unique debit note number |
| DN Date | Date | Yes | Date of the debit note |
| Party | Search-Select | No | From Organizations (party_id) |
| Party Name | Text | No | Auto-filled or manual |
| Amount | Number | Yes | Debit note amount |
| Currency | Dropdown | No | Default: USD |
| Reason | Textarea | No | Reason for the debit note |
| Job | Dropdown | No | Link to Import Job (job_id) |
| Status | Dropdown | No | DRAFT (default) / POSTED |

#### Search & Filters
- **Search:** By dn_no or party_name
- **Filters:** Status

---

### 7.6 Purchase Bills

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/purchase-bills` |
| **Purpose** | Record and manage vendor invoices with line items |
| **API Endpoint** | `GET/POST /api/purchase-bills` |

#### Fields — Bill Header

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Bill No | Text | Yes | Unique internal bill reference |
| Bill Date | Date | Yes | Date of bill entry |
| Vendor | Search-Select | No | From Organizations (vendor_id) |
| Vendor Name | Text | No | Auto-filled |
| Vendor Invoice No | Text | No | Vendor's original invoice number |
| Vendor Invoice Date | Date | No | Date on vendor's invoice |
| Amount | Number | No | Net amount before tax |
| Tax Amount | Number | No | Tax amount (default: 0) |
| Total Amount | Number | No | amount + tax_amount |
| Currency | Dropdown | No | Default: USD |
| Due Date | Date | No | Payment due date |
| Job | Dropdown | No | Link to Import Job (job_id) |
| Status | Dropdown | No | DRAFT / APPROVED / PAID / CANCELLED |
| Remarks | Textarea | No | Notes |

#### Fields — Bill Line Items

| Field | Type | Description |
|-------|------|-------------|
| Charge | Dropdown | From Charge Master |
| Charge Name | Text | Name of the charge |
| Quantity | Number | Default: 1 |
| Unit Rate | Number | Per-unit rate |
| Amount | Number | quantity × unit_rate |
| Tax Amount | Number | Tax on this line |
| GL Account | Dropdown | From Chart of Accounts |

#### Status Workflow
```
DRAFT → APPROVED → PAID
                 → CANCELLED
```

#### Search & Filters
- **Search:** By bill_no, vendor_name, or vendor_invoice_no
- **Filters:** Status

---

### 7.7 Customs Export

| Item | Detail |
|------|--------|
| **Screen** | `/transactions/customs-export` |
| **Purpose** | Record export customs declarations |
| **API Endpoint** | `GET/POST /api/customs-export` |

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Export No | Text | Yes | Unique export declaration number |
| Export Date | Date | Yes | Date of declaration |
| Exporter | Search-Select | No | From Organizations (exporter_id) |
| Exporter Name | Text | No | Auto-filled |
| Consignee | Search-Select | No | From Organizations (consignee_id) |
| Consignee Name | Text | No | Auto-filled |
| Commodity | Search-Select | No | From Commodities (commodity_id) |
| Commodity Description | Text | No | Free-text commodity description |
| HS Code | Text | No | Harmonized System code |
| Country of Origin | Text | No | Origin country |
| Destination Country | Text | No | Destination country |
| Transport Mode | Dropdown | No | AIR / SEA / ROAD |
| Incoterms | Dropdown | No | Trade terms |
| Total Value | Number | No | Declared value of goods |
| Currency | Dropdown | No | Default: USD |
| Gross Weight | Number | No | In kilograms |
| Net Weight | Number | No | In kilograms |
| Packages | Number | No | Number of packages |
| Customs Entry No | Text | No | Customs-assigned entry number |
| Customs Entry Date | Date | No | Date of customs entry |
| Status | Dropdown | No | DRAFT (default) / SUBMITTED / CLEARED |
| Remarks | Textarea | No | Additional notes |

#### Search & Filters
- **Search:** By export_no or exporter_name
- **Filters:** Status

---

## 8. Reports Module

| Screen | `/reports` |
|--------|-----------|
| **Purpose** | Generate and view operational and financial reports |

### Report Selection

Users select a report type from a card-based selector:

| Report | Icon | Description |
|--------|------|-------------|
| Import Jobs Report | 📄 | View all import jobs with status and details |
| Financial Ledger | 📈 | Summarized debit/credit by account |
| AP Aging Report | 💰 | Outstanding purchase bills by vendor |

After selecting a report, date filters appear and data is fetched.

---

### 8.1 Import Jobs Report

| Endpoint | `GET /api/reports/import-jobs-report` |
|----------|--------------------------------------|

#### Filters

| Filter | Type | Description |
|--------|------|-------------|
| Date From | Date picker | Start of date range |
| Date To | Date picker | End of date range |
| Transport Mode | Dropdown | SEA / AIR / ROAD |
| Status | Dropdown | OPEN / IN_PROGRESS / COMPLETED / CANCELLED |

#### Output Columns

| Column | Description |
|--------|-------------|
| Job No | Job reference number |
| Job Date | Date of the job |
| Transport Mode | SEA / AIR / ROAD |
| B/L No | Bill of Lading / AWB |
| Shipper | Shipper organization name |
| Consignee | Consignee organization name |
| POL | Port of Loading |
| POD | Port of Discharge |
| ETA | Estimated arrival |
| ATA | Actual arrival |
| Gross Weight | Weight in KG |
| Packages | Number of packages |
| Status | Job status |

---

### 8.2 Financial Ledger Report

| Endpoint | `GET /api/reports/financial-report` |
|----------|-------------------------------------|

#### Filters

| Filter | Type | Description |
|--------|------|-------------|
| Date From | Date picker | Start of period |
| Date To | Date picker | End of period |

#### Output Columns

| Column | Description |
|--------|-------------|
| Account Code | GL account code |
| Account Name | GL account description |
| Total Debit | Sum of debit amounts for the period |
| Total Credit | Sum of credit amounts for the period |

**Data Source:** Aggregated from `journal_lines` joined with `journal_entries` where status = 'POSTED'.

---

### 8.3 AP Aging Report

| Endpoint | `GET /api/reports/ar-aging` |
|----------|----------------------------|

#### Output Columns

| Column | Description |
|--------|-------------|
| Vendor Code | Organization code |
| Customer/Vendor | Organization name |
| Bill Count | Number of outstanding bills |
| Total Amount | Sum of outstanding total_amount |

**Data Source:** Purchase Bills where status is NOT 'PAID' or 'CANCELLED', grouped by vendor.

---

## 9. Tools & Utilities

| Screen | `/tools` |
|--------|---------|
| **Purpose** | System administration and maintenance utilities |

### Available Tools

| Tool | Icon | Description | Action |
|------|------|-------------|--------|
| **Export Data** | ⬇️ | Download master data as JSON for backup/migration | _Coming soon_ |
| **Import Data** | ⬆️ | Bulk import records from CSV/Excel templates | _Coming soon_ |
| **Audit Log** | 📋 | View history of data changes | _Coming soon_ |
| **System Diagnostics** | 🗄️ | Test database connection, verify tables and admin user | Calls `GET /api/auth/health` and displays results |
| **User Management** | 👥 | Add/edit system users | _Coming soon_ |
| **Purge Old Data** | 🗑️ | Clean up old/cancelled records | _Coming soon_ |
| **Export Templates** | 📝 | Download CSV/Excel templates for bulk import | _Coming soon_ |
| **Reset Admin Password** | 🔒 | Emergency password reset for admin user | Calls `POST /api/auth/fix-admin-password`, resets to 'Admin@123' |
| **Localization** | 🌐 | Language & region settings | _Coming soon_ |
| **Sync Settings** | 🔄 | Force-refresh cached settings | _Coming soon_ |

### System Diagnostics Detail

When "System Diagnostics" is clicked:
1. Calls `GET /api/auth/health`
2. Checks:
   - Database connection status
   - Users table existence
   - Admin user existence
   - Password hash validity
3. Displays success/failure toast and detailed results in browser console

---

## 10. Common UI Functionality

All list pages in CargoZen share a consistent pattern provided by the `GenericListPage` and shared components:

### 10.1 Page Header

Every page has a header containing:
- **Title** — Module name (e.g., "Organizations", "Import Jobs")
- **Subtitle** — Brief description (optional)
- **Action Buttons** — "New" button (for modules with create permission), "Refresh" button

### 10.2 Data Table

All list views use a shared `DataTable` component with:

| Feature | Description |
|---------|-------------|
| **Column Display** | Module-specific columns with custom renderers |
| **Sorting** | Click column header to sort ASC/DESC |
| **Search** | Text input for keyword search (ILIKE pattern) |
| **Filters** | Module-specific dropdown filters |
| **Pagination** | Page size (default: 20), page number navigation, total records count |
| **Status Badges** | Color-coded pills: ACTIVE=green, INACTIVE=gray, PENDING=yellow, APPROVED=green, REJECTED=red, DRAFT=gray, POSTED=blue, COMPLETED=green, CANCELLED=red |
| **Row Actions** | Edit (pencil icon), Delete (trash icon), View (eye icon) — based on permissions |
| **Loading State** | Spinner shown while data is being fetched |
| **Empty State** | "No records found" message when data is empty |
| **Refresh** | Manual refresh button to re-fetch data |

### 10.3 Modal Dialogs

Create and Edit operations use modal dialogs:

| Feature | Description |
|---------|-------------|
| **Overlay** | Dark background overlay |
| **Title** | "New [Module]" or "Edit [Module]" |
| **Form** | React Hook Form with Zod validation |
| **Save Button** | Submits the form, shows loading spinner |
| **Cancel Button** | Closes modal without saving |
| **Validation** | Real-time field validation with error messages |
| **Success Toast** | Green notification on successful save |
| **Error Toast** | Red notification on failure |

### 10.4 Search-Select (Lookups)

Dropdown fields that reference other entities use type-ahead search:

| Feature | Description |
|---------|-------------|
| **Type-Ahead** | User types 2+ characters, results appear |
| **API Call** | Hits `/search-select?q=` endpoint |
| **Results** | Shows code + name, max 50 results |
| **Selection** | Click to select, populates the ID and display name |
| **Filtering** | Can filter by type (e.g., customers only, vendors only) |

### 10.5 Soft Delete

All delete operations are **soft deletes**:
- Sets `is_active = FALSE` (not physical deletion)
- Record remains in database for audit/history
- Soft-deleted records can be filtered in/out on list views

### 10.6 Lazy Loading

All page components are loaded on-demand using React `lazy()` + `Suspense`:
- Initial bundle is small (only login page)
- Each module loads when the user first navigates to it
- Loading spinner shown during chunk download

---

## 11. Business Rules & Validations

### 11.1 General Rules

| Rule | Description |
|------|-------------|
| **Unique Codes** | All code fields (org_code, airline_code, charge_code, etc.) must be unique. Attempting to create a duplicate returns HTTP 400. |
| **Soft Delete** | No physical deletion. All "delete" operations set `is_active = FALSE`. |
| **Audit Fields** | All records automatically capture `created_by`, `created_at`, `updated_at`. |
| **Timestamps** | All timestamps stored without timezone (TIMESTAMP_NTZ). |
| **Default Currency** | USD is the system-wide default currency. |
| **Pagination** | Default page size: 20 (most modules), 100 (Accounts). Maximum: 100 (most), 500 (Accounts). |

### 11.2 Organization Rules

| Rule | Description |
|------|-------------|
| Org Code must be unique | Checked before INSERT; returns error on duplicate |
| New orgs start as PENDING | `approval_status` defaults to 'PENDING' |
| Approval requires permission | Only `can_approve` users can change approval status |
| Lookup returns only approved | Search-select only returns `is_active = TRUE AND approval_status = 'APPROVED'` |
| Multi-role support | An organization can simultaneously be a customer, vendor, agent, and/or carrier |

### 11.3 Import Job Rules

| Rule | Description |
|------|-------------|
| Job No must be unique | Enforced at database level |
| Charges saved with job | Charge lines are inserted in the same transaction as the job |
| Carrier type determines lookup | `carrier_type = AIRLINE` → Airlines table; `carrier_type = SHIPPING_LINE` → Shipping Lines table |
| Status progression | OPEN → IN_PROGRESS → COMPLETED or CANCELLED |

### 11.4 Journal Entry Rules

| Rule | Description |
|------|-------------|
| Must balance | `total_debit` must equal `total_credit` |
| Lines saved atomically | All journal lines are inserted with the entry header |
| Line numbering | Lines are auto-numbered sequentially starting from 1 |
| Each line: one side only | A line should have debit OR credit, not both |

### 11.5 Financial Transaction Rules

| Rule | Description |
|------|-------------|
| Multi-currency | All payment/receipt transactions support currency + exchange rate |
| Base amount | Calculated as `amount × exchange_rate` |
| Payment allocation | Payments can be allocated across multiple jobs |
| Status workflow | DRAFT → POSTED → CANCELLED (payments); DRAFT → POSTED (receipts, DN) |
| Purchase bill approval | DRAFT → APPROVED → PAID → CANCELLED |

### 11.6 Authentication Rules

| Rule | Description |
|------|-------------|
| Password hashing | bcrypt with 12 rounds |
| Access token expiry | 60 minutes |
| Refresh token expiry | 24 hours |
| Token blacklist | Logout adds JTI to blacklist; all requests check blacklist |
| Inactive accounts | Cannot log in (`is_active = FALSE` check) |
| Auto-repair | Admin password is auto-repaired if bcrypt hash is corrupted (login-time) |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **B/L** | Bill of Lading — a shipping document issued by a carrier |
| **AWB** | Air Waybill — a shipping document for air freight |
| **IATA** | International Air Transport Association |
| **ICAO** | International Civil Aviation Organization |
| **SCAC** | Standard Carrier Alpha Code — unique 2-4 letter code for carriers |
| **HS Code** | Harmonized System code — international tariff classification |
| **IMDG** | International Maritime Dangerous Goods code |
| **UN Number** | United Nations identification number for hazardous substances |
| **POL** | Port of Loading |
| **POD** | Port of Discharge |
| **ETA** | Estimated Time of Arrival |
| **ATA** | Actual Time of Arrival |
| **Incoterms** | International Commercial Terms (FOB, CIF, EXW, DDP, etc.) |
| **CBM** | Cubic Meters — standard unit of volume for freight |
| **GL** | General Ledger — the central accounting record |
| **AP** | Accounts Payable — money owed to vendors |
| **AR** | Accounts Receivable — money owed by customers |
| **DN** | Debit Note — a document requesting payment |
| **RBAC** | Role-Based Access Control |
| **JWT** | JSON Web Token — used for authentication |
| **CRUD** | Create, Read, Update, Delete — standard data operations |
| **Soft Delete** | Setting `is_active = FALSE` instead of physically removing a record |
| **KPI** | Key Performance Indicator |
| **CORS** | Cross-Origin Resource Sharing — browser security policy |
| **SPA** | Single-Page Application |

---

> **Document generated from CargoZen codebase analysis**
> **Total Modules:** 22 (12 Administration + 7 Transactions + 3 Reports)
> **Total API Endpoints:** 50+
> **Total Database Tables:** 29 (across 3 schemas)

