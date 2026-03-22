# 🚢 CargoZen — Full Architecture Document

> **Freight & Logistics Management System**
> Version 1.0.0 | Last Updated: March 2026

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Technology Stack Summary](#3-technology-stack-summary)
4. [Presentation Layer (Frontend)](#4-presentation-layer-frontend)
5. [Middleware / API Layer (Backend)](#5-middleware--api-layer-backend)
6. [Data Layer (Database)](#6-data-layer-database)
7. [Authentication & Security Architecture](#7-authentication--security-architecture)
8. [Deployment Architecture (Docker)](#8-deployment-architecture-docker)
9. [Module-Level Architecture](#9-module-level-architecture)
10. [Data Flow Diagrams](#10-data-flow-diagrams)
11. [Database Schema Diagram](#11-database-schema-diagram)
12. [API Endpoint Map](#12-api-endpoint-map)
13. [Frontend Component Architecture](#13-frontend-component-architecture)
14. [Non-Functional Requirements](#14-non-functional-requirements)

---

## 1. System Overview

**CargoZen** is a full-stack enterprise freight and logistics management system designed for freight forwarding companies. It manages the complete lifecycle of import/export operations including job management, financial transactions, customs clearance, master data administration, and reporting.

### Key Business Capabilities

| Domain | Capability |
|--------|-----------|
| **Freight Operations** | Import job management (Sea/Air/Road), shipment tracking, customs declarations |
| **Financial Management** | Bank payments/receipts, journal entries, purchase bills, debit notes |
| **Master Data** | Organizations, airlines, shipping lines, commodities, charge master |
| **Compliance** | Custom clearing setup, HS code management, dangerous goods classification |
| **Reporting** | Import jobs reports, financial ledger, AP aging |

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CARGOZEN SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
  │   Browser    │       │   Browser    │       │   Browser    │
  │  (User 1)   │       │  (User 2)   │       │  (Admin)     │
  └──────┬───────┘       └──────┬───────┘       └──────┬───────┘
         │                      │                      │
         │         HTTPS / Port 5173                   │
         └──────────────────────┼──────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER (Frontend)                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    React 18 + TypeScript + Vite                        │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐  │  │
│  │  │  Router   │ │  State   │ │   API    │ │    UI     │ │   Forms   │  │  │
│  │  │ React     │ │ Zustand  │ │  Axios + │ │ Tailwind  │ │ React     │  │  │
│  │  │ Router v6 │ │          │ │ TanStack │ │ CSS +     │ │ Hook Form │  │  │
│  │  │          │ │          │ │  Query   │ │ Lucide    │ │ + Zod     │  │  │
│  │  └──────────┘ └──────────┘ └────┬─────┘ └───────────┘ └───────────┘  │  │
│  └──────────────────────────────────┼────────────────────────────────────┘  │
│                Docker Container: node:20-alpine → nginx:alpine (prod)       │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
                          REST API / JSON / Port 8000
                          Authorization: Bearer <JWT>
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     MIDDLEWARE LAYER (Backend API)                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                   FastAPI + Python 3.11 + Pydantic v2                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐  │  │
│  │  │   Auth   │ │  Admin   │ │   TXN    │ │  Reports  │ │   Core    │  │  │
│  │  │ Routes   │ │ Routes   │ │ Routes   │ │  Routes   │ │ Security  │  │  │
│  │  │ ────────── │ ────────── │ ────────── │ ─────────── │ ─────────── │  │
│  │  │ Login    │ │ Orgs     │ │ Import   │ │ Import    │ │ JWT       │  │  │
│  │  │ Refresh  │ │ Airlines │ │ Jobs     │ │ Jobs Rpt  │ │ bcrypt    │  │  │
│  │  │ Logout   │ │ Ships    │ │ Bank Pay │ │ Ledger    │ │ CORS      │  │  │
│  │  │ Me       │ │ Charges  │ │ Bank Rcp │ │ AP Aging  │ │ Config    │  │  │
│  │  │ Perms    │ │ Accounts │ │ Journals │ │           │ │ Database  │  │  │
│  │  │          │ │ Commods  │ │ Purch.   │ │           │ │ Pool      │  │  │
│  │  │          │ │ Vendors  │ │ DN / Exp │ │           │ │           │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └───────────┘ └───────────┘  │  │
│  └──────────────────────────────────┼────────────────────────────────────┘  │
│                Docker Container: python:3.11-slim + Uvicorn                  │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
                       SQL (psycopg2 connection pool)
                       DSN via DATABASE_URL env variable
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                        DATA LAYER (Database)                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL (Supabase-hosted) / Snowflake SQL              │  │
│  │                                                                        │  │
│  │  ┌─── AUTH Schema ───┐  ┌─── ADMIN Schema ──┐  ┌─── TXN Schema ───┐  │  │
│  │  │ ROLES             │  │ ORGANIZATIONS      │  │ IMPORT_JOBS      │  │  │
│  │  │ USERS             │  │ ORGANIZATION_GRPS  │  │ JOB_CHARGES      │  │  │
│  │  │ ROLE_PERMISSIONS  │  │ AIRLINES           │  │ BANK_PAYMENTS    │  │  │
│  │  │ USER_COLUMN_PREFS │  │ SHIPPING_LINES     │  │ PAYMENT_ALLOCS   │  │  │
│  │  │ TOKEN_BLACKLIST   │  │ ACCOUNTS           │  │ BANK_RECEIPTS    │  │  │
│  │  │                   │  │ CHARGE_MASTER      │  │ JOURNAL_ENTRIES  │  │  │
│  │  │                   │  │ DEFAULT_CHARGES    │  │ JOURNAL_LINES    │  │  │
│  │  │                   │  │ BUSINESS_DIMS      │  │ GENERAL_DN       │  │  │
│  │  │                   │  │ COMMODITIES        │  │ PURCHASE_BILLS   │  │  │
│  │  │                   │  │ SYSTEM_SETTINGS    │  │ PURCHASE_LINES   │  │  │
│  │  │                   │  │ VENDOR_CONTRACTS   │  │ CUSTOMS_EXPORT   │  │  │
│  │  │                   │  │ VENDOR_RATES       │  │                  │  │  │
│  │  │                   │  │ CUSTOM_CLEARING    │  │                  │  │  │
│  │  └───────────────────┘  └────────────────────┘  └──────────────────┘  │  │
│  │                                                                        │  │
│  │  ┌──── VIEWS ──────────────────────────────────────────────────────┐   │  │
│  │  │ V_ORGANIZATION_LOOKUP  V_AIRLINE_LOOKUP  V_SHIPPING_LINE_LOOKUP│   │  │
│  │  │ V_ACCOUNT_LOOKUP       V_CHARGE_LOOKUP                         │   │  │
│  │  └────────────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                        Managed Cloud Database (Supabase)                      │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack Summary

### Complete Technology Matrix

| Layer | Technology | Version | Purpose / Functionality |
|-------|-----------|---------|------------------------|
| **Frontend — Framework** | React | 18.2 | Component-based UI rendering |
| **Frontend — Language** | TypeScript | 5.4 | Type-safe JavaScript superset |
| **Frontend — Build Tool** | Vite | 5.2 | Lightning-fast HMR, ES module bundler |
| **Frontend — Styling** | Tailwind CSS | 3.4 | Utility-first CSS framework |
| **Frontend — Routing** | React Router DOM | 6.22 | Client-side SPA routing with lazy loading |
| **Frontend — State Mgmt** | Zustand | 4.5 | Lightweight global state (auth, UI) |
| **Frontend — Server State** | TanStack React Query | 5.28 | Data fetching, caching, sync |
| **Frontend — HTTP Client** | Axios | 1.6 | HTTP requests with interceptors |
| **Frontend — Forms** | React Hook Form | 7.51 | Performant form management |
| **Frontend — Validation** | Zod | 3.22 | Schema-based form validation |
| **Frontend — Icons** | Lucide React | 0.368 | Modern icon library |
| **Frontend — Toasts** | React Hot Toast | 2.4 | Notification popups |
| **Frontend — Dates** | date-fns | 3.6 | Date formatting / manipulation |
| **Frontend — CSS Utilities** | clsx + tailwind-merge | 2.1 / 2.2 | Conditional class merging |
| **Backend — Framework** | FastAPI | latest | High-performance async Python API |
| **Backend — Runtime** | Python | 3.11 | Backend programming language |
| **Backend — Server** | Uvicorn | latest | ASGI server for FastAPI |
| **Backend — Validation** | Pydantic v2 | latest | Data model validation & serialization |
| **Backend — Settings** | pydantic-settings | latest | Environment-based configuration |
| **Backend — Auth (JWT)** | python-jose | latest | JWT token creation & verification |
| **Backend — Auth (Hash)** | bcrypt | latest | Password hashing (12 rounds) |
| **Backend — Database Driver** | psycopg2-binary | latest | PostgreSQL connection & queries |
| **Backend — File Upload** | python-multipart | latest | Multipart form data parsing |
| **Backend — Env Config** | python-dotenv | latest | `.env` file loading |
| **Backend — Timezone** | pytz | latest | Timezone-aware datetime handling |
| **Database** | PostgreSQL (Supabase) | 15+ | Relational database (cloud-managed) |
| **Database (alt)** | Snowflake SQL | — | Cloud data warehouse (schema design) |
| **DevOps — Containers** | Docker | latest | Application containerization |
| **DevOps — Orchestration** | Docker Compose | 3.9 | Multi-container orchestration |
| **DevOps — Web Server** | Nginx | alpine | Production static file serving & reverse proxy |
| **Deployment** | Render | — | Cloud deployment platform |

---

## 4. Presentation Layer (Frontend)

### 4.1 Architecture Overview

```
frontend/src/
├── main.tsx                  ← App entry point (ReactDOM.createRoot)
├── App.tsx                   ← Root component → <AppRouter />
├── index.css                 ← Tailwind CSS imports
├── vite-env.d.ts             ← Vite type declarations
│
├── router/                   ← Routing Layer
│   ├── index.tsx             ← createBrowserRouter (all routes)
│   └── ProtectedRoute.tsx    ← Auth guard wrapper
│
├── store/                    ← Global State (Zustand)
│   ├── authStore.ts          ← User session, tokens, login/logout
│   └── uiStore.ts            ← UI state (sidebar collapsed, etc.)
│
├── api/                      ← API Communication Layer
│   ├── client.ts             ← Axios instance + interceptors
│   └── hooks/                ← TanStack Query hooks (per module)
│
├── types/                    ← TypeScript Type Definitions
│   └── index.ts              ← All interfaces (User, Org, Job, etc.)
│
├── components/               ← Shared UI Components
│   ├── layout/
│   │   ├── AppLayout.tsx     ← Main layout (sidebar + topbar + content)
│   │   ├── Sidebar.tsx       ← Navigation sidebar with collapsible groups
│   │   └── TopBar.tsx        ← Top header bar
│   └── common/
│       ├── DataTable/        ← Reusable data grid component
│       ├── Modal.tsx         ← Reusable modal dialog
│       ├── PageHeader.tsx    ← Page title + action buttons
│       └── StatusBadge.tsx   ← Status indicator badges
│
└── pages/                    ← Page-Level Components
    ├── auth/                 ← Login page
    ├── dashboard/            ← Dashboard overview
    ├── administration/       ← 12 admin modules (see §9)
    ├── transactions/         ← 7 transaction modules (see §9)
    ├── reports/              ← Report pages
    ├── tools/                ← Utility tools
    └── GenericListPage.tsx   ← Reusable CRUD list page pattern
```

### 4.2 Technology Functionality

| Technology | Functionality in CargoZen |
|-----------|--------------------------|
| **React 18** | Component rendering, Suspense for lazy-loaded routes, concurrent features |
| **TypeScript** | Strict type checking across 238+ type definitions (User, Organization, ImportJob, etc.) |
| **Vite** | Dev server with HMR on port 5173, production build, path aliasing (`@/`) |
| **React Router v6** | 24 routes with lazy loading, `ProtectedRoute` auth guard, nested layouts |
| **Zustand** | `authStore` — persisted user session (refresh token in localStorage); `uiStore` — sidebar state |
| **TanStack Query** | Server-state caching, auto-refetch, pagination support for all list views |
| **Axios** | Central `apiClient` with Bearer token injection, 401 auto-refresh interceptor, retry queue |
| **React Hook Form** | Form state management for all create/edit dialogs (Organizations, Jobs, Payments, etc.) |
| **Zod** | Schema validation for form inputs with `@hookform/resolvers` integration |
| **Tailwind CSS** | Responsive design, iOS-style color palette (`bg-ios-blue`, etc.), dark/light variants |
| **Lucide React** | 20+ icons used in sidebar navigation and UI elements |
| **React Hot Toast** | Success/error notification toasts on CRUD operations |
| **date-fns** | Date formatting for job dates, payment dates, report ranges |

### 4.3 Key Frontend Patterns

```
┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND DATA FLOW                         │
│                                                              │
│  User Action                                                 │
│       │                                                      │
│       ▼                                                      │
│  React Hook Form  ──(validate)──▶  Zod Schema               │
│       │                                                      │
│       ▼                                                      │
│  TanStack Query Mutation  ──(POST/PUT)──▶  Axios Client      │
│       │                                                      │
│       ▼                                                      │
│  Axios Interceptor  ──(inject Bearer JWT)──▶  FastAPI        │
│       │                                                      │
│       ▼                                                      │
│  On Success:  Invalidate Query Cache → Refetch List          │
│  On Error:    React Hot Toast notification                   │
│                                                              │
│  ─────────────────────────────────────────────               │
│                                                              │
│  On 401:  Interceptor auto-refreshes token via /auth/refresh │
│           Queues failed requests, retries after new token    │
│           If refresh fails → logout + redirect to /login     │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Middleware / API Layer (Backend)

### 5.1 Architecture Overview

```
backend/app/
├── main.py                   ← FastAPI app, CORS, router mounting, startup checks
│
├── core/                     ← Cross-Cutting Infrastructure
│   ├── config.py             ← Settings (env vars: DATABASE_URL, JWT_*, CORS)
│   ├── database.py           ← psycopg2 connection pool, query helpers
│   └── security.py           ← JWT create/decode, bcrypt hash/verify
│
├── models/                   ← Data Models
│   └── schemas.py            ← Pydantic request/response schemas
│
├── api/routes/               ← API Route Handlers
│   ├── auth.py               ← /api/auth/* (login, refresh, logout, me, permissions)
│   ├── organizations.py      ← /api/organizations/* (CRUD + approve/reject)
│   ├── administration.py     ← /api/admin/* (11 sub-routers)
│   ├── transactions.py       ← /api/txn/* (7 sub-routers)
│   └── reports.py            ← /api/reports/* (import jobs, ledger, AP aging)
│
└── services/                 ← Business Logic Layer (service classes)
```

### 5.2 Technology Functionality

| Technology | Functionality in CargoZen |
|-----------|--------------------------|
| **FastAPI** | Auto-generated OpenAPI docs (`/api/docs`), async request handling, dependency injection, CORS middleware |
| **Python 3.11** | Backend runtime with modern syntax (match-case, type hints, f-strings) |
| **Uvicorn** | ASGI server running on port 8000, hot-reload in development |
| **Pydantic v2** | Request body validation, response serialization, settings management |
| **pydantic-settings** | Type-safe `.env` config loading (`DATABASE_URL`, `JWT_SECRET_KEY`, etc.) |
| **python-jose** | JWT access token (60 min TTL) and refresh token (24 hr TTL) with HS256 algorithm |
| **bcrypt** | Password hashing with 12 salt rounds, constant-time verification |
| **psycopg2** | PostgreSQL connection pooling (1–10 connections), `RealDictCursor` for dict results |
| **python-multipart** | File upload support for document attachments |
| **python-dotenv** | Loads `.env` file variables into process environment |

### 5.3 Backend Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND REQUEST FLOW                       │
│                                                             │
│  HTTP Request                                               │
│       │                                                     │
│       ▼                                                     │
│  CORS Middleware  ──(check origin)──▶  Allow/Reject         │
│       │                                                     │
│       ▼                                                     │
│  FastAPI Router  ──(match route)──▶  Route Handler          │
│       │                                                     │
│       ▼                                                     │
│  Auth Dependency  ──(decode JWT)──▶  Verify Token           │
│       │                             Check Blacklist         │
│       ▼                             Extract User            │
│  Pydantic Validation  ──(parse body)──▶  Schema Model       │
│       │                                                     │
│       ▼                                                     │
│  Database Layer                                             │
│       │  ┌──────────────────────────────────┐               │
│       ├─▶│ execute_query()   → SELECT rows  │               │
│       ├─▶│ execute_one()     → SELECT one   │               │
│       ├─▶│ execute_write()   → INSERT/UPDATE│               │
│       └─▶│ execute_insert_returning_id()    │               │
│          └──────────────────────────────────┘               │
│       │                                                     │
│       ▼                                                     │
│  JSONResponse  ──(serialize)──▶  HTTP Response               │
└─────────────────────────────────────────────────────────────┘
```

### 5.4 Connection Pool Architecture

```
┌────────────────────────────────────┐
│     psycopg2 SimpleConnectionPool  │
│                                    │
│  ┌──────┐ ┌──────┐     ┌──────┐   │
│  │Conn 1│ │Conn 2│ ... │Conn10│   │  minconn=1, maxconn=10
│  └──┬───┘ └──┬───┘     └──┬───┘   │
│     │        │             │       │
│     └────────┼─────────────┘       │
│              │                     │
│       get_cursor() context mgr     │
│       ┌─────────────────────┐      │
│       │ getconn()           │      │
│       │ yield RealDictCursor│      │
│       │ commit / rollback   │      │
│       │ putconn()           │      │
│       └─────────────────────┘      │
└────────────────────────────────────┘
         │
         ▼
  PostgreSQL (Supabase)
  DATABASE_URL = postgresql://...
```

---

## 6. Data Layer (Database)

### 6.1 Schema Organization

The database is organized into **3 schemas** with clear separation of concerns:

```
CARGOZEN_DB
├── AUTH Schema      ← Authentication & Authorization (5 tables)
├── ADMIN Schema     ← Master Data & Configuration (13 tables + 5 views)
└── TXN Schema       ← Business Transactions (11 tables)
```

### 6.2 AUTH Schema — Tables & Functionality

| Table | Columns | Functionality |
|-------|---------|--------------|
| **ROLES** | role_id, role_name, description, is_active | Define user roles (Admin, Operator, Viewer) |
| **USERS** | user_id, username, email, password_hash, role_id, refresh_token | User accounts with bcrypt hashed passwords |
| **ROLE_PERMISSIONS** | perm_id, role_id, module, can_view/create/edit/delete/export/approve | Fine-grained RBAC per module |
| **USER_COLUMN_PREFS** | pref_id, user_id, module_key, column_config (JSON) | Per-user data table column visibility & ordering |
| **TOKEN_BLACKLIST** | id, token_jti, expires_at | Revoked JWT tokens (for logout) |

### 6.3 ADMIN Schema — Tables & Functionality

| Table | Key Columns | Functionality |
|-------|------------|--------------|
| **ORGANIZATIONS** | org_code, org_name, org_type, is_customer/vendor/agent/carrier, approval_status, credit_limit | Master record for all business partners with approval workflow |
| **ORGANIZATION_GROUPS** | group_code, group_name, group_type | Categorize organizations (Customer Group, Vendor Group, etc.) |
| **AIRLINES** | airline_code, iata_code, icao_code, airline_name, alliance | Airline carrier master for air freight |
| **SHIPPING_LINES** | line_code, scac_code, line_name | Ocean carrier master for sea freight |
| **ACCOUNTS** | account_code, account_type (ASSET/LIABILITY/EQUITY/INCOME/EXPENSE), parent_account_id | Hierarchical chart of accounts for double-entry bookkeeping |
| **CHARGE_MASTER** | charge_code, charge_type (FREIGHT/CUSTOMS/LOCAL/HANDLING), applicable_for, gl_account_id | Freight charge definitions linked to GL accounts |
| **DEFAULT_CHARGES** | charge_id, job_type, transport_mode, amount | Pre-assigned charges by job type and transport mode |
| **BUSINESS_DIMENSIONS** | dim_code, dim_type (DEPARTMENT/BRANCH/COST_CENTER/PROJECT), parent_dim_id | Hierarchical business dimensions for cost tracking |
| **COMMODITIES** | commodity_code, hs_code, is_dangerous, dangerous_class, un_number | Cargo types with HS codes and IMDG dangerous goods classification |
| **SYSTEM_SETTINGS** | setting_key, setting_value (JSON), data_type | Global configuration key-value pairs |
| **VENDOR_CONTRACTS** | contract_no, vendor_id, contract_type, start_date, end_date, status | Rate agreements with vendors |
| **VENDOR_CONTRACT_RATES** | contract_id, charge_id, origin, destination, rate, min_charge | Individual rate lines within contracts |
| **CUSTOM_CLEARING_SETUP** | clearing_type, port_code, customs_authority, procedures (JSON), required_docs (JSON) | Import/export customs procedure configuration |

### 6.4 TXN Schema — Tables & Functionality

| Table | Key Columns | Functionality |
|-------|------------|--------------|
| **IMPORT_JOBS** | job_no, transport_mode (AIR/SEA/ROAD), shipper_id, consignee_id, bl_no, pol, pod, eta, status | Core freight import job with shipment details |
| **JOB_CHARGES** | job_id, charge_id, quantity, rate, amount, vendor_id | Charge line items allocated to import jobs |
| **BANK_PAYMENTS** | payment_no, bank_account_id, payee_id, amount, payment_method, status | Outgoing payments (WIRE/CHEQUE/CASH/ONLINE) |
| **PAYMENT_ALLOCATIONS** | payment_id, job_id, invoice_ref, amount | Links payments to specific jobs/invoices |
| **BANK_RECEIPTS** | receipt_no, bank_account_id, payer_id, amount, receipt_method, status | Incoming receipts from customers |
| **JOURNAL_ENTRIES** | entry_no, entry_type (STANDARD/ADJUSTING/REVERSING), total_debit, total_credit, status | Double-entry bookkeeping header |
| **JOURNAL_LINES** | entry_id, account_id, debit_amount, credit_amount, dim_id | Individual debit/credit lines per journal entry |
| **GENERAL_DEBIT_NOTES** | dn_no, party_id, amount, reason, job_id, status | Debit notes issued to parties |
| **PURCHASE_BILLS** | bill_no, vendor_id, vendor_invoice_no, amount, tax_amount, due_date, status | Vendor invoices with approval workflow |
| **PURCHASE_BILL_LINES** | bill_id, charge_id, quantity, unit_rate, amount, gl_account_id | Line items within purchase bills |
| **CUSTOMS_EXPORT** | export_no, exporter_id, consignee_id, hs_code, customs_entry_no, status | Export customs declaration records |

### 6.5 Database Views

| View | Functionality |
|------|--------------|
| **V_ORGANIZATION_LOOKUP** | Active, approved organizations for dropdowns (id, code, name, type, flags) |
| **V_AIRLINE_LOOKUP** | Active airlines for selection (id, code, name, IATA) |
| **V_SHIPPING_LINE_LOOKUP** | Active shipping lines for selection (id, code, name, SCAC) |
| **V_ACCOUNT_LOOKUP** | Active accounts for selection (id, code, name, type) |
| **V_CHARGE_LOOKUP** | Active charges for selection (id, code, name, type, category) |

---

## 7. Authentication & Security Architecture

### 7.1 Authentication Flow

```
┌──────────┐                    ┌──────────┐                    ┌──────────┐
│  Browser  │                    │  FastAPI  │                    │   DB     │
└─────┬────┘                    └─────┬────┘                    └─────┬────┘
      │                               │                               │
      │  POST /api/auth/login         │                               │
      │  {username, password}         │                               │
      ├──────────────────────────────▶│                               │
      │                               │  SELECT * FROM users          │
      │                               │  WHERE username = ?           │
      │                               ├──────────────────────────────▶│
      │                               │◀──────────────────────────────┤
      │                               │                               │
      │                               │  bcrypt.checkpw(password,     │
      │                               │                password_hash) │
      │                               │                               │
      │                               │  create_access_token()  (60m) │
      │                               │  create_refresh_token() (24h) │
      │                               │                               │
      │  {access_token, refresh_token,│                               │
      │   user: {...}}                │                               │
      │◀──────────────────────────────┤                               │
      │                               │                               │
      │  ──── Subsequent Requests ──── │                               │
      │  Authorization: Bearer <AT>   │                               │
      ├──────────────────────────────▶│                               │
      │                               │  decode_token(AT)             │
      │                               │  Check TOKEN_BLACKLIST        │
      │                               │                               │
      │  ──── Token Expired (401) ──── │                               │
      │◀──────────────────────────────┤                               │
      │                               │                               │
      │  POST /api/auth/refresh       │                               │
      │  {refresh_token}              │                               │
      ├──────────────────────────────▶│                               │
      │                               │  decode_token(RT)             │
      │                               │  create_access_token() (new)  │
      │  {access_token}               │                               │
      │◀──────────────────────────────┤                               │
      │                               │                               │
      │  ──── Logout ──────────────── │                               │
      │  POST /api/auth/logout        │                               │
      ├──────────────────────────────▶│                               │
      │                               │  INSERT INTO TOKEN_BLACKLIST  │
      │                               ├──────────────────────────────▶│
      │  {message: "Logged out"}      │                               │
      │◀──────────────────────────────┤                               │
```

### 7.2 Security Components

| Component | Technology | Detail |
|-----------|-----------|--------|
| **Password Hashing** | bcrypt (12 rounds) | One-way hash, constant-time comparison |
| **Access Token** | JWT (HS256) | 60-minute expiry, contains user_id, username, role |
| **Refresh Token** | JWT (HS256) | 24-hour expiry, stored in Zustand (persisted) |
| **Token Blacklist** | PostgreSQL table | Revoked JTIs checked on every authenticated request |
| **CORS** | FastAPI middleware | Allowed origins: `localhost:5173`, `localhost:3000` |
| **RBAC** | ROLE_PERMISSIONS table | Module-level: can_view, can_create, can_edit, can_delete, can_export, can_approve |
| **Client Auto-Refresh** | Axios interceptor | Queues failed requests, refreshes token, retries all queued |

---

## 8. Deployment Architecture (Docker)

### 8.1 Container Architecture

```
┌─────────────────────── Docker Compose ───────────────────────┐
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Frontend Container                       │    │
│  │  Image: node:20-alpine → nginx:alpine (production)   │    │
│  │  Port:  5173 (dev) / 80 (prod)                       │    │
│  │                                                       │    │
│  │  Development:  Vite dev server with HMR              │    │
│  │  Production:   nginx serves /usr/share/nginx/html    │    │
│  │                nginx proxies /api/* → backend:8000   │    │
│  │                                                       │    │
│  │  Volumes:  ./frontend:/app (dev hot reload)          │    │
│  │  Depends:  backend                                    │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                    │
│                  /api/* proxy                                 │
│                          │                                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              Backend Container                        │    │
│  │  Image: python:3.11-slim                              │    │
│  │  Port:  8000                                          │    │
│  │  CMD:   uvicorn app.main:app --host 0.0.0.0          │    │
│  │                                                       │    │
│  │  Volumes:  ./backend:/app (dev hot reload)           │    │
│  │  Env:      .env file (DATABASE_URL, JWT_SECRET_KEY)  │    │
│  └──────────────────────────────────────────────────────┘    │
│                          │                                    │
│                   DATABASE_URL                                │
│                          │                                    │
│                          ▼                                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │         External: Supabase PostgreSQL                 │    │
│  │         (Cloud-managed, not in Docker)                │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.2 Production Deployment (Render)

```
┌──────────── Render Cloud Platform ─────────────┐
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Frontend Service                         │  │
│  │  Build:  npm ci && npm run build          │  │
│  │  Start:  vite preview --host 0.0.0.0      │  │
│  │  URL:    cargozen.onrender.com            │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Backend Service                          │  │
│  │  Build:  pip install -r requirements.txt  │  │
│  │  Start:  uvicorn app.main:app             │  │
│  │  URL:    cargozen-api.onrender.com        │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Database: Supabase (PostgreSQL)          │  │
│  │  Region:  Nearest to Render region        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## 9. Module-Level Architecture

### 9.1 Administration Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ADMINISTRATION MODULES                             │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Module              │ Functionality                                         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Organizations       │ CRUD for customers, vendors, agents, carriers.        │
│                     │ Approval workflow (PENDING → APPROVED/REJECTED).      │
│                     │ Credit limit/days management. Multi-role flags.       │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Org Groups          │ Group organizations by type (Customer Group, etc.).   │
│                     │ Used for filtering and reporting hierarchy.           │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Airlines            │ Airline master with IATA/ICAO codes and alliance.     │
│                     │ Referenced in air freight import jobs.                │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Shipping Lines      │ Ocean carrier master with SCAC codes.                │
│                     │ Referenced in sea freight import jobs.                │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Chart of Accounts   │ Hierarchical GL accounts (Asset/Liability/Equity/    │
│                     │ Income/Expense). Parent-child tree structure.         │
│                     │ Linked to charges and journal entries.                │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Charge Master       │ Define freight charges: FREIGHT, CUSTOMS, LOCAL,     │
│                     │ HANDLING, MISC. Link to GL accounts. Tax settings.   │
│                     │ Unit types: LUMP, PER_KG, PER_CBM, PER_UNIT.        │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Default Charges     │ Pre-assign charges by job type (Import/Export)       │
│                     │ and transport mode (Air/Sea/Road).                   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Business Dimensions │ Hierarchical dimensions: Departments, Branches,     │
│                     │ Cost Centers, Projects. Used in journal lines.       │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Commodities         │ Cargo types with HS codes. Dangerous goods           │
│                     │ classification (IMDG class, UN number).              │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Vendor Contracts    │ Rate agreements: air/sea/trucking/customs.            │
│                     │ Contract rates by origin-destination lane.            │
│                     │ Status: DRAFT → ACTIVE → EXPIRED/CANCELLED.          │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Custom Clearing     │ Import/export customs procedure setup per port.      │
│                     │ Define procedure steps (JSON), required documents.    │
│                     │ Link to broker organizations.                        │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ System Settings     │ Global configuration: company info, defaults,        │
│                     │ numbering formats. Key-value with type safety.       │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

### 9.2 Transaction Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRANSACTION MODULES                               │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Module              │ Functionality                                         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Import Jobs         │ Core freight operations module. Create/manage import  │
│                     │ jobs for Air/Sea/Road. Track shipper, consignee,      │
│                     │ carrier, B/L, flight/vessel, POL/POD, ETA/ATA.       │
│                     │ Add charge lines with quantities and rates.           │
│                     │ Status: OPEN → IN_PROGRESS → COMPLETED/CANCELLED.    │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Bank Payments       │ Record outgoing payments. Select bank account,        │
│                     │ payee org, method (WIRE/CHEQUE/CASH/ONLINE).          │
│                     │ Multi-currency with exchange rates.                   │
│                     │ Allocate payments to specific jobs/invoices.          │
│                     │ Status: DRAFT → POSTED → CANCELLED.                  │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Bank Receipts       │ Record incoming customer payments. Track payer,       │
│                     │ receipt method, reference numbers.                    │
│                     │ Multi-currency support. DRAFT → POSTED workflow.      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Journal Entries     │ Double-entry bookkeeping. Entry types: Standard,      │
│                     │ Adjusting, Reversing, Opening. Multiple debit/credit  │
│                     │ lines per entry. Balanced validation (debit=credit).  │
│                     │ Link to business dimensions for cost tracking.        │
│                     │ Status: DRAFT → POSTED → REVERSED.                   │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ General Debit Notes │ Issue debit notes to parties (customers/vendors).     │
│                     │ Link to specific import jobs. Track reason & amount.  │
│                     │ Status: DRAFT → POSTED workflow.                      │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Purchase Bills      │ Record vendor invoices with line items. Track vendor  │
│                     │ invoice number & date. Tax calculations.              │
│                     │ Link charges to GL accounts. Due date tracking.       │
│                     │ Status: DRAFT → APPROVED → PAID → CANCELLED.         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Customs Export      │ Export customs declarations. Track exporter,           │
│                     │ consignee, commodity (with HS code), countries,       │
│                     │ transport mode, incoterms, weights, packages.         │
│                     │ Customs entry number tracking.                        │
│                     │ Status: DRAFT → SUBMITTED → CLEARED.                 │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

### 9.3 Reports Module

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              REPORTS                                        │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Report              │ Functionality                                         │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Import Jobs Report  │ List of import jobs with filters (date range,         │
│                     │ transport mode, status). Charge summaries.            │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ Financial Ledger    │ General ledger with account-wise transaction details. │
│                     │ Date range filtering. Opening/closing balances.       │
├─────────────────────┼───────────────────────────────────────────────────────┤
│ AP Aging Report     │ Accounts payable aging analysis. Vendor-wise         │
│                     │ outstanding amounts by aging buckets (30/60/90 days). │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 10. Data Flow Diagrams

### 10.1 Import Job Creation Flow

```
┌────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐
│  User  │    │ Frontend │    │  FastAPI  │    │   DB     │    │ Result │
└───┬────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └───┬────┘
    │              │               │               │               │
    │  Fill Form   │               │               │               │
    ├─────────────▶│               │               │               │
    │              │               │               │               │
    │              │  Zod Validate │               │               │
    │              ├──────┐        │               │               │
    │              │◀─────┘        │               │               │
    │              │               │               │               │
    │              │  POST /api/txn/import-jobs    │               │
    │              ├──────────────▶│               │               │
    │              │               │               │               │
    │              │               │  Pydantic     │               │
    │              │               │  Validate     │               │
    │              │               ├──────┐        │               │
    │              │               │◀─────┘        │               │
    │              │               │               │               │
    │              │               │  INSERT INTO  │               │
    │              │               │  IMPORT_JOBS  │               │
    │              │               ├──────────────▶│               │
    │              │               │               │               │
    │              │               │  INSERT INTO  │               │
    │              │               │  JOB_CHARGES  │               │
    │              │               ├──────────────▶│               │
    │              │               │               │               │
    │              │               │  job_id       │               │
    │              │               │◀──────────────┤               │
    │              │               │               │               │
    │              │  201 Created  │               │               │
    │              │◀──────────────┤               │               │
    │              │               │               │               │
    │              │  Invalidate   │               │               │
    │              │  Query Cache  │               │               │
    │              │  Toast: ✅    │               │               │
    │  Updated List│               │               │               │
    │◀─────────────┤               │               │               │
```

### 10.2 Financial Transaction Flow

```
                    ┌─────────────────────────┐
                    │      Import Job          │
                    │   (JOB_CHARGES added)    │
                    └──────────┬──────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Purchase   │  │    Bank      │  │   Debit      │
    │    Bill     │  │  Payment     │  │    Note      │
    │  (Vendor)   │  │  (Pay Out)   │  │  (Charge)    │
    └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
           │                │                  │
           │    ┌───────────┘                  │
           ▼    ▼                              ▼
    ┌──────────────┐                  ┌──────────────┐
    │   Journal    │                  │     Bank     │
    │   Entry      │                  │   Receipt    │
    │  (Auto GL)   │                  │  (Collect)   │
    └──────┬───────┘                  └──────┬───────┘
           │                                 │
           └─────────────┬───────────────────┘
                         ▼
               ┌─────────────────┐
               │   GL Ledger     │
               │   Reports       │
               │   AP Aging      │
               └─────────────────┘
```

---

## 11. Database Schema Diagram (ER)

```
                              ┌─────────────┐
                              │    ROLES     │
                              │─────────────│
                              │ role_id (PK) │
                              │ role_name    │
                              └──────┬───────┘
                                     │ 1:N
                  ┌──────────────────┼──────────────────┐
                  ▼                  ▼                   │
         ┌──────────────┐  ┌────────────────┐           │
         │    USERS      │  │ROLE_PERMISSIONS│           │
         │──────────────│  │────────────────│           │
         │ user_id (PK) │  │ role_id (FK)   │           │
         │ role_id (FK)  │  │ module         │           │
         │ password_hash │  │ can_view/...   │           │
         │ refresh_token │  └────────────────┘           │
         └──────┬────────┘                               │
                │ 1:N                                    │
         ┌──────┴──────┐                                 │
         ▼             ▼                                 │
  ┌──────────────┐ ┌───────────────┐                    │
  │USER_COL_PREFS│ │TOKEN_BLACKLIST│                    │
  └──────────────┘ └───────────────┘                    │

  ═══════════════════════════════════════════════════════
         ADMIN SCHEMA
  ═══════════════════════════════════════════════════════

  ┌──────────────────┐      ┌──────────────────┐
  │ ORG_GROUPS       │◀──── │ ORGANIZATIONS    │
  │ group_id (PK)    │ 1:N  │ org_id (PK)      │
  │ group_code       │      │ group_id (FK)    │
  └──────────────────┘      │ is_customer/...  │
                            │ approval_status  │
                            └──────┬───────────┘
                                   │ Referenced by
                    ┌──────────────┼──────────────┐
                    ▼              ▼               ▼
           ┌──────────────┐ ┌───────────┐ ┌────────────┐
           │VENDOR_CONTRACTS│ │CUSTOM_CLR │ │ TXN tables │
           │ vendor_id(FK) │ │broker(FK) │ │(various FK)│
           └───────┬───────┘ └───────────┘ └────────────┘
                   │ 1:N
                   ▼
           ┌──────────────────┐
           │VENDOR_CONTRACT_  │
           │RATES             │
           │ contract_id (FK) │
           │ charge_id (FK)   │
           └──────────────────┘

  ┌────────────────┐     ┌──────────────────┐
  │  ACCOUNTS      │◀────│  CHARGE_MASTER   │
  │ account_id(PK) │ FK  │ charge_id (PK)   │
  │ parent_id(FK)  │     │ gl_account_id(FK)│
  │ account_type   │     │ charge_type      │
  └────────┬───────┘     └────────┬─────────┘
           │ self-ref              │ 1:N
           │ (tree)               ▼
           │              ┌───────────────┐
           │              │DEFAULT_CHARGES │
           │              │ charge_id (FK) │
           │              └───────────────┘
           │
  ┌────────────────────┐  ┌──────────────┐  ┌─────────────────┐
  │BUSINESS_DIMENSIONS │  │ COMMODITIES  │  │ SYSTEM_SETTINGS │
  │ dim_id (PK)        │  │commodity_id  │  │ setting_key     │
  │ parent_dim_id (FK) │  │ hs_code      │  │ setting_value   │
  │ dim_type           │  │ is_dangerous │  │ (VARIANT/JSON)  │
  └────────────────────┘  └──────────────┘  └─────────────────┘

  ═══════════════════════════════════════════════════════
         TXN SCHEMA
  ═══════════════════════════════════════════════════════

  ┌──────────────────────┐
  │    IMPORT_JOBS        │
  │ job_id (PK)           │
  │ shipper_id → Orgs     │
  │ consignee_id → Orgs   │
  │ carrier_id            │
  │ commodity_id → Commod │
  │ transport_mode        │
  │ bl_no, pol, pod       │
  └───────────┬───────────┘
              │ 1:N                1:N                1:N
     ┌────────┼────────────────────┼──────────────────┼─────────┐
     ▼        ▼                    ▼                  ▼         ▼
┌──────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────┐ ┌──────────┐
│JOB_      │ │BANK_PAYMENTS │ │GENERAL_      │ │PURCHASE │ │CUSTOMS_  │
│CHARGES   │ │payment_id(PK)│ │DEBIT_NOTES   │ │BILLS    │ │EXPORT    │
│job_id(FK)│ │payee_id→Orgs │ │party_id→Orgs │ │vendor_id│ │export_id │
│charge_id │ │job alloc     │ │job_id(FK)    │ │job_id   │ │hs_code   │
└──────────┘ └──────┬───────┘ └──────────────┘ └────┬────┘ └──────────┘
                    │ 1:N                           │ 1:N
                    ▼                               ▼
             ┌──────────────┐                ┌──────────────┐
             │PAYMENT_      │                │PURCHASE_BILL │
             │ALLOCATIONS   │                │_LINES        │
             │payment_id(FK)│                │bill_id(FK)   │
             │job_id(FK)    │                │charge_id     │
             └──────────────┘                │gl_account_id │
                                             └──────────────┘

  ┌──────────────────┐
  │ JOURNAL_ENTRIES  │
  │ entry_id (PK)    │
  │ entry_type       │         ┌──────────────────┐
  │ reference_type   │────────▶│  BANK_RECEIPTS   │
  │ reference_id     │  1:N    │ receipt_id (PK)  │
  └───────┬──────────┘         │ payer_id → Orgs  │
          │ 1:N                └──────────────────┘
          ▼
  ┌──────────────────┐
  │ JOURNAL_LINES    │
  │ entry_id (FK)    │
  │ account_id→Accts │
  │ debit_amount     │
  │ credit_amount    │
  │ dim_id → BizDims │
  └──────────────────┘
```

---

## 12. API Endpoint Map

### 12.1 Authentication Endpoints

| Method | Endpoint | Functionality |
|--------|----------|--------------|
| POST | `/api/auth/login` | Authenticate user, return JWT tokens |
| POST | `/api/auth/refresh` | Refresh access token using refresh token |
| POST | `/api/auth/logout` | Revoke token (add to blacklist) |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/auth/permissions` | Get role-based permissions for current user |

### 12.2 Administration Endpoints

| Method | Endpoint | Functionality |
|--------|----------|--------------|
| GET/POST | `/api/organizations` | List / Create organizations |
| GET/PUT/DELETE | `/api/organizations/{id}` | Read / Update / Delete organization |
| PUT | `/api/organizations/{id}/approve` | Approve/reject organization |
| GET/POST | `/api/admin/org-groups` | List / Create org groups |
| GET/PUT/DELETE | `/api/admin/org-groups/{id}` | CRUD org group |
| GET/POST | `/api/admin/airlines` | List / Create airlines |
| GET/PUT/DELETE | `/api/admin/airlines/{id}` | CRUD airline |
| GET/POST | `/api/admin/shipping-lines` | List / Create shipping lines |
| GET/PUT/DELETE | `/api/admin/shipping-lines/{id}` | CRUD shipping line |
| GET/POST | `/api/admin/accounts` | List / Create GL accounts |
| GET/PUT/DELETE | `/api/admin/accounts/{id}` | CRUD account |
| GET/POST | `/api/admin/charge-master` | List / Create charges |
| GET/PUT/DELETE | `/api/admin/charge-master/{id}` | CRUD charge |
| GET/POST | `/api/admin/default-charges` | List / Create default charges |
| GET/PUT/DELETE | `/api/admin/default-charges/{id}` | CRUD default charge |
| GET/POST | `/api/admin/business-dimensions` | List / Create dimensions |
| GET/PUT/DELETE | `/api/admin/business-dimensions/{id}` | CRUD dimension |
| GET/POST | `/api/admin/commodities` | List / Create commodities |
| GET/PUT/DELETE | `/api/admin/commodities/{id}` | CRUD commodity |
| GET/POST | `/api/admin/vendor-contracts` | List / Create vendor contracts |
| GET/PUT/DELETE | `/api/admin/vendor-contracts/{id}` | CRUD vendor contract |
| GET/POST | `/api/admin/custom-clearing` | List / Create custom clearing setups |
| GET/PUT/DELETE | `/api/admin/custom-clearing/{id}` | CRUD clearing setup |
| GET/PUT | `/api/admin/system-settings` | Read / Update system settings |

### 12.3 Transaction Endpoints

| Method | Endpoint | Functionality |
|--------|----------|--------------|
| GET/POST | `/api/txn/import-jobs` | List / Create import jobs |
| GET/PUT/DELETE | `/api/txn/import-jobs/{id}` | CRUD import job |
| GET/POST | `/api/txn/bank-payments` | List / Create bank payments |
| GET/PUT/DELETE | `/api/txn/bank-payments/{id}` | CRUD bank payment |
| GET/POST | `/api/txn/bank-receipts` | List / Create bank receipts |
| GET/PUT/DELETE | `/api/txn/bank-receipts/{id}` | CRUD bank receipt |
| GET/POST | `/api/txn/journal-entries` | List / Create journal entries |
| GET/PUT/DELETE | `/api/txn/journal-entries/{id}` | CRUD journal entry |
| GET/POST | `/api/txn/purchase-bills` | List / Create purchase bills |
| GET/PUT/DELETE | `/api/txn/purchase-bills/{id}` | CRUD purchase bill |
| GET/POST | `/api/txn/debit-notes` | List / Create debit notes |
| GET/PUT/DELETE | `/api/txn/debit-notes/{id}` | CRUD debit note |
| GET/POST | `/api/txn/customs-export` | List / Create customs exports |
| GET/PUT/DELETE | `/api/txn/customs-export/{id}` | CRUD customs export |

### 12.4 Report Endpoints

| Method | Endpoint | Functionality |
|--------|----------|--------------|
| GET | `/api/reports/import-jobs` | Import jobs report with filters |
| GET | `/api/reports/ledger` | Financial ledger report |
| GET | `/api/reports/ap-aging` | Accounts payable aging report |

### 12.5 Utility Endpoints

| Method | Endpoint | Functionality |
|--------|----------|--------------|
| GET | `/` | API health message |
| GET | `/health` | Health check endpoint |
| GET | `/api/docs` | Swagger UI documentation |
| GET | `/api/redoc` | ReDoc documentation |

---

## 13. Frontend Component Architecture

### 13.1 Component Hierarchy

```
<App>
└── <AppRouter>                              ← React Router v6
    ├── /login → <LoginPage>                 ← Public route
    └── <ProtectedRoute>                     ← Auth guard (checks Zustand)
        └── <AppLayout>                      ← Sidebar + TopBar + Content
            ├── <Sidebar>                    ← Collapsible navigation
            │   ├── NavLeaf (Dashboard, Reports, Tools)
            │   └── NavGroup (Administration, Transactions)
            │       └── NavLeaf (child items)
            │
            ├── <TopBar>                     ← User info, logout button
            │
            └── <Suspense fallback={Loading}>  ← Lazy-loaded page
                ├── <DashboardPage>
                │
                ├── <OrganizationsPage>       ← Administration Pages
                │   ├── <PageHeader>          ← Title + "New" button
                │   ├── <DataTable>           ← Sortable, paginated grid
                │   │   ├── Column headers
                │   │   ├── Row rendering
                │   │   ├── <StatusBadge>
                │   │   └── Pagination controls
                │   └── <Modal>               ← Create/Edit form dialog
                │       └── <form> (React Hook Form + Zod)
                │
                ├── <ImportJobsPage>          ← Transaction Pages
                │   ├── <PageHeader>
                │   ├── <DataTable>
                │   └── <Modal>
                │       └── Job form + Charge lines
                │
                ├── <ReportsPage>             ← Report Pages
                │   ├── Filter controls
                │   └── <DataTable> (read-only)
                │
                └── <ToolsPage>               ← Utility Tools
```

### 13.2 Shared Components

| Component | Props | Functionality |
|-----------|-------|--------------|
| **DataTable** | columns, data, pagination, sorting | Reusable data grid with sortable headers, status badges, row actions (edit/delete), pagination |
| **Modal** | isOpen, onClose, title, children | Centered dialog overlay for create/edit forms |
| **PageHeader** | title, subtitle, actions | Page title bar with action buttons (New, Export, etc.) |
| **StatusBadge** | status, variant | Color-coded status pills (ACTIVE/INACTIVE, PENDING/APPROVED, DRAFT/POSTED) |

### 13.3 State Management Architecture

```
┌──────────────────────────────────────────────────────┐
│                  STATE MANAGEMENT                     │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │          Zustand (Client State)                 │ │
│  │                                                 │ │
│  │  authStore                uiStore               │ │
│  │  ┌──────────────────┐    ┌──────────────────┐  │ │
│  │  │ user: User       │    │ sidebarCollapsed │  │ │
│  │  │ access_token     │    │ (boolean)        │  │ │
│  │  │ refresh_token    │    └──────────────────┘  │ │
│  │  │ isAuthenticated  │                          │ │
│  │  │ login()          │    Persisted: No         │ │
│  │  │ logout()         │                          │ │
│  │  │ setTokens()      │                          │ │
│  │  └──────────────────┘                          │ │
│  │  Persisted: refresh_token, user, isAuth        │ │
│  │  Storage: localStorage (cargozen-auth)         │ │
│  └─────────────────────────────────────────────────┘ │
│                                                      │
│  ┌─────────────────────────────────────────────────┐ │
│  │       TanStack React Query (Server State)       │ │
│  │                                                 │ │
│  │  useQuery('organizations', fetchOrgs)           │ │
│  │  useQuery('import-jobs', fetchJobs)             │ │
│  │  useMutation(createJob, { onSuccess: ... })     │ │
│  │                                                 │ │
│  │  Features:                                      │ │
│  │  - Automatic caching & deduplication            │ │
│  │  - Background refetching                        │ │
│  │  - Optimistic updates                           │ │
│  │  - Query invalidation on mutations              │ │
│  └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

---

## 14. Non-Functional Requirements

### 14.1 Performance

| Aspect | Implementation |
|--------|---------------|
| **Lazy Loading** | All page components loaded via `React.lazy()` + `Suspense` |
| **Connection Pooling** | psycopg2 pool (1–10 connections) |
| **Caching** | TanStack Query in-memory cache with stale-while-revalidate |
| **Bundle Optimization** | Vite tree-shaking, code splitting per route |

### 14.2 Security

| Aspect | Implementation |
|--------|---------------|
| **Authentication** | JWT (HS256) with access + refresh token pattern |
| **Password Storage** | bcrypt with 12 salt rounds |
| **Token Revocation** | Server-side blacklist table (TOKEN_BLACKLIST) |
| **CORS** | Explicit origin whitelist |
| **RBAC** | Module-level permissions (view/create/edit/delete/export/approve) |

### 14.3 Scalability

| Aspect | Implementation |
|--------|---------------|
| **Containerization** | Docker containers for frontend & backend |
| **Stateless API** | JWT-based auth, no server sessions |
| **Cloud Database** | Supabase-managed PostgreSQL (auto-scaling) |
| **Cloud Deployment** | Render platform with auto-deploy from Git |

### 14.4 Maintainability

| Aspect | Implementation |
|--------|---------------|
| **Type Safety** | TypeScript (frontend) + Pydantic (backend) |
| **Code Organization** | Feature-based folder structure (admin/transactions/reports) |
| **API Documentation** | Auto-generated Swagger UI + ReDoc |
| **Schema Separation** | AUTH / ADMIN / TXN database schemas |

---

> **Document generated from CargoZen codebase analysis**
> **Project Version:** 1.0.0
> **Architecture Style:** 3-Tier (Presentation → API → Data)
> **Pattern:** SPA + REST API + Relational Database

