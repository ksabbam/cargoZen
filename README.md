# 🚢 CargoZen — Freight & Logistics Management System

A full-stack enterprise freight management system built with **React.js**, **FastAPI**, and **Snowflake**.

---

## 🏗️ Architecture

```
cargozen/
├── frontend/          # React.js + TypeScript + Vite + Tailwind CSS
├── backend/           # FastAPI (Python) middleware
├── database/          # Snowflake SQL schemas & seed data
└── docker-compose.yml # Docker orchestration
```

### Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand, React Hook Form, Lucide React |
| Middleware | FastAPI, Python 3.11, Pydantic v2, Python-Jose (JWT), Passlib (bcrypt) |
| Backend | Snowflake SQL (CARGOZEN_DB) |
| Auth | JWT (access token 30min + refresh token 24h) |

---

## 📦 Modules

### Administration
| Module | Description |
|--------|-------------|
| Organizations | Customer/vendor/agent/carrier master with approval workflow |
| Organization Groups | Group organizations by type |
| Airlines | Airline master with IATA/ICAO codes |
| Shipping Lines | Ocean carrier master with SCAC codes |
| Accounts | Chart of accounts (hierarchical) |
| Charge Master | Freight charges with type/category/applicability |
| Default Charges | Default charge assignments by job/mode |
| Business Dimensions | Branches, departments, cost centers |
| Commodities | Cargo types with HS codes and dangerous goods classification |
| Vendor Contracts | Rate agreements with vendors |
| Custom Clearing Setup | Import/export customs procedure setup |
| System Settings | Global application configuration |

### Transactions
| Module | Description |
|--------|-------------|
| Import Jobs | Sea/air/road freight import jobs with charge lines |
| Bank Payments | Outgoing payments with allocation to jobs |
| Bank Receipts | Incoming receipts from customers |
| Journal Entries | Double-entry bookkeeping with line items |
| General Debit Notes | Debit notes issued to parties |
| Purchase Bills | Vendor invoices with line items |
| Customs Export | Export customs declarations |

### Reports
- Import Jobs Report
- Financial Ledger Report
- AP Aging Report

---

## 🚀 Getting Started

### Prerequisites
- Node.js 20+
- Python 3.11+
- Snowflake account
- Git

### 1. Database Setup

Run the SQL scripts in Snowflake (in order):
```sql
-- In your Snowflake Worksheet:
-- 1. Execute: database/01_schema.sql
-- 2. Execute: database/02_seed_data.sql
```

### 2. Backend Setup

```powershell
cd backend

# Copy and configure environment
Copy-Item .env.example .env
# Edit .env with your Snowflake credentials and JWT secret

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/api/docs

### 3. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

App available at: http://localhost:5173

### 4. Docker (Full Stack)

```bash
# Copy backend env
cp backend/.env.example backend/.env
# Edit backend/.env

docker-compose up --build
```

---

## 🔐 Authentication

Default credentials (change immediately in production):
- **Username:** `admin`
- **Password:** `Admin@123`

### JWT Flow
```
POST /api/auth/login  →  { access_token (30min), refresh_token (24h) }
                    ↓
Axios interceptor injects Bearer token on every request
                    ↓
On 401 → auto-refresh via POST /api/auth/refresh
                    ↓
On refresh failure → redirect to /login
```

---

## 🗄️ Snowflake Database Structure

```
CARGOZEN_DB
├── AUTH schema
│   ├── USERS
│   ├── ROLES
│   ├── ROLE_PERMISSIONS
│   ├── USER_COLUMN_PREFS
│   └── TOKEN_BLACKLIST
├── ADMIN schema
│   ├── ORGANIZATION_GROUPS
│   ├── ORGANIZATIONS
│   ├── AIRLINES
│   ├── SHIPPING_LINES
│   ├── ACCOUNTS
│   ├── CHARGE_MASTER
│   ├── DEFAULT_CHARGES
│   ├── BUSINESS_DIMENSIONS
│   ├── COMMODITIES
│   ├── SYSTEM_SETTINGS
│   ├── VENDOR_CONTRACTS
│   ├── VENDOR_CONTRACT_RATES
│   └── CUSTOM_CLEARING_SETUP
└── TXN schema
    ├── IMPORT_JOBS
    ├── JOB_CHARGES
    ├── BANK_PAYMENTS
    ├── PAYMENT_ALLOCATIONS
    ├── BANK_RECEIPTS
    ├── JOURNAL_ENTRIES
    ├── JOURNAL_LINES
    ├── GENERAL_DEBIT_NOTES
    ├── PURCHASE_BILLS
    ├── PURCHASE_BILL_LINES
    └── CUSTOMS_EXPORT
```

---

## 📁 Frontend Structure

```
src/
├── api/
│   ├── client.ts          # Axios instance with JWT interceptors + auto-refresh
│   └── hooks/             # TanStack Query hooks per module
├── components/
│   ├── layout/
│   │   ├── AppLayout.tsx  # Main layout with sidebar
│   │   └── Sidebar.tsx    # Collapsible navigation
│   └── common/
│       ├── DataTable/     # Reusable paginated table with search/sort
│       ├── Modal.tsx      # Accessible modal dialog
│       ├── PageHeader.tsx # Page title + action buttons
│       └── StatusBadge.tsx
├── pages/
│   ├── auth/              # Login page
│   ├── dashboard/         # KPI dashboard
│   ├── administration/    # 12 admin modules
│   ├── transactions/      # 7 transaction modules
│   ├── reports/           # Report runner
│   └── GenericListPage.tsx
├── router/                # React Router v6 + ProtectedRoute
├── store/
│   ├── authStore.ts       # Zustand auth state (persisted)
│   └── uiStore.ts         # UI state (sidebar)
└── types/index.ts         # TypeScript interfaces
```

---

## 🌐 API Endpoints

### Auth
```
POST   /api/auth/login          # Login
POST   /api/auth/refresh        # Refresh access token
POST   /api/auth/logout         # Logout (blacklist token)
```

### Standard CRUD Pattern (all modules)
```
GET    /api/{module}            # List with pagination + search
GET    /api/{module}/{id}       # Get single record
POST   /api/{module}            # Create
PUT    /api/{module}/{id}       # Update
DELETE /api/{module}/{id}       # Soft delete (set IS_ACTIVE=FALSE)
GET    /api/{module}/search-select?q=  # Lightweight lookup for dropdowns
```

### Special Endpoints
```
PATCH  /api/organizations/{id}/approval    # Approve/Reject organization
GET    /api/reports/dashboard-summary      # KPI cards
GET    /api/reports/import-jobs-report     # Jobs report
GET    /api/reports/financial-report       # Ledger report
GET    /api/reports/ar-aging               # AP aging
```

---

## 🔧 Environment Variables

### Backend (.env)
```env
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=CARGOZEN_WH
SNOWFLAKE_DATABASE=CARGOZEN_DB
SNOWFLAKE_ROLE=CARGOZEN_ROLE

JWT_SECRET_KEY=your-32-char-minimum-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_HOURS=24

CORS_ORIGINS=http://localhost:5173
```

---

## 🛡️ Security Features
- JWT with short-lived access tokens (30 min)
- Refresh token rotation (24h, stored server-side)
- Token blacklisting on logout
- bcrypt password hashing
- CORS configured for specific origins
- Soft deletes (no data destruction)
- Approval workflow for organizations

---

## 📝 Development Notes

### Adding a New Module
1. Add Snowflake table to `database/01_schema.sql`
2. Add Pydantic schemas to `backend/app/models/schemas.py`
3. Add FastAPI router to `backend/app/api/routes/`
4. Register router in `backend/app/main.py`
5. Create React page in `frontend/src/pages/`
6. Add route to `frontend/src/router/index.tsx`
7. Add nav item to `frontend/src/components/layout/Sidebar.tsx`

### Building for Production
```bash
# Frontend
cd frontend && npm run build

# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```
