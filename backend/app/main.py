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
    """Log startup info. DB checks are done lazily on first request."""
    import logging
    log = logging.getLogger("cargozen")
    log.info(f"CargoZen API started")
    log.info(f"Snowflake: {settings.SNOWFLAKE_ACCOUNT} / {settings.SNOWFLAKE_USER}")
    if not settings.SNOWFLAKE_PASSWORD:
        print("\n  ⚠  SNOWFLAKE_PASSWORD is empty in backend/.env")
        print("     Set it so the app can connect to Snowflake.")
        print("     In Snowflake Worksheet run:")
        print("       ALTER USER SUSANI SET PASSWORD = 'YourPassword';")
        print("     Then set SNOWFLAKE_PASSWORD=YourPassword in backend/.env\n")
    else:
        print("\n  ★ CargoZen API ready — Snowflake password configured\n")


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})