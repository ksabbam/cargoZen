from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes.auth import router as auth_router
from app.api.routes.organizations import router as org_router
from app.api.routes.reports import router as reports_router
from app.api.routes.administration import (
    org_groups_router, airlines_router, shipping_lines_router,
    charge_master_router, accounts_router, commodities_router,
    biz_dim_router, vendor_contracts_router, system_settings_router,
    default_charges_router, custom_clearing_router
)
from app.api.routes.transactions import (
    import_jobs_router, bank_payments_router, bank_receipts_router,
    journal_entries_router, purchase_bills_router, debit_notes_router,
    customs_export_router
)

app = FastAPI(
    title="CargoZen API",
    description="Freight & Logistics Management System - FastAPI Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers under /api prefix
PREFIX = "/api"

app.include_router(auth_router, prefix=PREFIX)
app.include_router(org_router, prefix=PREFIX)
app.include_router(reports_router, prefix=PREFIX)

# Administration routers
app.include_router(org_groups_router, prefix=PREFIX)
app.include_router(airlines_router, prefix=PREFIX)
app.include_router(shipping_lines_router, prefix=PREFIX)
app.include_router(charge_master_router, prefix=PREFIX)
app.include_router(accounts_router, prefix=PREFIX)
app.include_router(commodities_router, prefix=PREFIX)
app.include_router(biz_dim_router, prefix=PREFIX)
app.include_router(vendor_contracts_router, prefix=PREFIX)
app.include_router(system_settings_router, prefix=PREFIX)
app.include_router(default_charges_router, prefix=PREFIX)
app.include_router(custom_clearing_router, prefix=PREFIX)

# Transaction routers
app.include_router(import_jobs_router, prefix=PREFIX)
app.include_router(bank_payments_router, prefix=PREFIX)
app.include_router(bank_receipts_router, prefix=PREFIX)
app.include_router(journal_entries_router, prefix=PREFIX)
app.include_router(purchase_bills_router, prefix=PREFIX)
app.include_router(debit_notes_router, prefix=PREFIX)
app.include_router(customs_export_router, prefix=PREFIX)


@app.get("/")
async def root():
    return {"message": "CargoZen API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_info():
    """Log startup info and verify database readiness."""
    import logging
    log = logging.getLogger("cargozen")
    log.info("CargoZen API started (Supabase / PostgreSQL)")
    print("\n  [*] CargoZen API starting — Supabase (PostgreSQL)")
    _check_database(log)


def _check_database(log):
    """Read-only check: verify tables, roles, and admin user exist."""
    from app.core.security import verify_password
    from app.core.database import execute_one

    ok = True

    # Test basic connectivity
    try:
        execute_one("SELECT 1 AS ok")
        print("  [OK] Database connection successful")
    except Exception as exc:
        print(f"  [!!] Cannot connect to database: {exc}")
        return

    # Check roles
    try:
        row = execute_one("SELECT COUNT(*) AS cnt FROM roles")
        cnt = int(row["cnt"]) if row else 0
        if cnt > 0:
            print(f"  [OK] Roles: {cnt} found")
        else:
            print("  [!!] Roles table is EMPTY")
            ok = False
    except Exception as exc:
        print(f"  [!!] Cannot query roles: {exc}")
        ok = False

    # Check admin user + password hash
    try:
        user = execute_one(
            "SELECT user_id, username, password_hash FROM users WHERE username = 'admin'"
        )
        if user:
            stored_hash = user.get("password_hash", "")
            if stored_hash and verify_password("Admin@123", stored_hash):
                print("  [OK] Admin user found, password hash verified")
            else:
                print("  [!!] Admin user found but password hash DOES NOT match 'Admin@123'")
                ok = False
        else:
            print("  [!!] Admin user NOT FOUND")
            ok = False
    except Exception as exc:
        print(f"  [!!] Cannot query users: {exc}")
        ok = False

    if not ok:
        print("")
        print("  ================================================")
        print("  ACTION REQUIRED: Run the setup script!")
        print("  ================================================")
        print("  cd backend && python setup_db.py")
        print("")
    else:
        print("  [OK] Database ready\n")


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})