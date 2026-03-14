from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_current_active_user
from app.core.database import execute_query, execute_one, execute_write
from app.models.schemas import PaginatedResponse, MessageResponse, UserResponse
import math

router = APIRouter(tags=["Transactions"])

# ========================
# Import Jobs
# ========================
import_jobs_router = APIRouter(prefix="/import-jobs")


@import_jobs_router.get("", response_model=PaginatedResponse)
async def list_import_jobs(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    transport_mode: Optional[str] = None, date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(j.job_no ILIKE %s OR j.bl_no ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("j.status = %s")
        params.append(status)
    if transport_mode:
        conditions.append("j.transport_mode = %s")
        params.append(transport_mode)
    if date_from:
        conditions.append("j.job_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("j.job_date <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM import_jobs j WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"""SELECT j.*,
                   s.org_name AS shipper_name, c.org_name AS consignee_name
            FROM import_jobs j
            LEFT JOIN organizations s ON j.shipper_id = s.org_id
            LEFT JOIN organizations c ON j.consignee_id = c.org_id
            WHERE {where} ORDER BY j.job_date DESC, j.job_no DESC LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@import_jobs_router.get("/{job_id}")
async def get_import_job(job_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT j.*, s.org_name AS shipper_name, c.org_name AS consignee_name
           FROM import_jobs j
           LEFT JOIN organizations s ON j.shipper_id = s.org_id
           LEFT JOIN organizations c ON j.consignee_id = c.org_id
           WHERE j.job_id = %s""",
        (job_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    charges = execute_query(
        "SELECT * FROM job_charges WHERE job_id = %s ORDER BY line_id",
        (job_id,)
    )
    result = dict(row)
    result["charges"] = charges
    return result


@import_jobs_router.post("", status_code=201)
async def create_import_job(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO import_jobs (job_no, job_date, transport_mode, shipper_id, consignee_id,
           carrier_id, carrier_type, bl_no, flight_no, vessel_name, voyage_no, pol, pod,
           eta, ata, commodity_id, gross_weight, chargeable_weight, volume_cbm,
           packages, package_type, incoterms, freight_currency, freight_amount, status, remarks, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           RETURNING job_id""",
        (payload["job_no"], payload["job_date"], payload.get("transport_mode"),
         payload.get("shipper_id"), payload.get("consignee_id"), payload.get("carrier_id"),
         payload.get("carrier_type"), payload.get("bl_no"), payload.get("flight_no"),
         payload.get("vessel_name"), payload.get("voyage_no"), payload.get("pol"), payload.get("pod"),
         payload.get("eta"), payload.get("ata"), payload.get("commodity_id"),
         payload.get("gross_weight"), payload.get("chargeable_weight"), payload.get("volume_cbm"),
         payload.get("packages"), payload.get("package_type"), payload.get("incoterms"),
         payload.get("freight_currency"), payload.get("freight_amount"),
         payload.get("status", "OPEN"), payload.get("remarks"), current_user.user_id)
    )
    job_id = row["job_id"] if row else None
    for charge in payload.get("charges", []):
        execute_write(
            """INSERT INTO job_charges (job_id, charge_id, charge_name, quantity, unit_type,
               rate, currency, amount, tax_amount, total_amount, vendor_id)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (job_id, charge.get("charge_id"), charge.get("charge_name"),
             charge.get("quantity", 1), charge.get("unit_type"), charge.get("rate"),
             charge.get("currency"), charge.get("amount"), charge.get("tax_amount", 0),
             charge.get("total_amount"), charge.get("vendor_id"))
        )
    return {"job_id": job_id, "message": "Import job created"}


@import_jobs_router.put("/{job_id}", response_model=MessageResponse)
async def update_import_job(job_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE import_jobs SET transport_mode=%s, shipper_id=%s, consignee_id=%s,
           bl_no=%s, vessel_name=%s, eta=%s, ata=%s, status=%s, remarks=%s,
           updated_at=NOW() WHERE job_id=%s""",
        (payload.get("transport_mode"), payload.get("shipper_id"), payload.get("consignee_id"),
         payload.get("bl_no"), payload.get("vessel_name"), payload.get("eta"), payload.get("ata"),
         payload.get("status"), payload.get("remarks"), job_id)
    )
    return MessageResponse(message="Job updated")


# ========================
# Bank Payments
# ========================
bank_payments_router = APIRouter(prefix="/bank-payments")


@bank_payments_router.get("", response_model=PaginatedResponse)
async def list_bank_payments(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    date_from: Optional[str] = None, date_to: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(payment_no ILIKE %s OR payee_name ILIKE %s OR bank_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    if date_from:
        conditions.append("payment_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("payment_date <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM bank_payments WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM bank_payments WHERE {where} ORDER BY payment_date DESC, payment_no DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@bank_payments_router.get("/{payment_id}")
async def get_bank_payment(payment_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM bank_payments WHERE payment_id = %s", (payment_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found")
    return row


@bank_payments_router.post("", status_code=201)
async def create_bank_payment(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO bank_payments (payment_no, payment_date, bank_account_id, bank_name,
           payee_id, payee_name, amount, currency, exchange_rate, base_amount,
           payment_method, reference_no, narration, status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING payment_id""",
        (payload["payment_no"], payload["payment_date"], payload.get("bank_account_id"),
         payload.get("bank_name"), payload.get("payee_id"), payload.get("payee_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("exchange_rate", 1.0),
         payload.get("base_amount"), payload.get("payment_method"), payload.get("reference_no"),
         payload.get("narration"), payload.get("status", "DRAFT"), current_user.user_id)
    )
    return {"payment_id": row["payment_id"] if row else None, "message": "Payment created"}


@bank_payments_router.put("/{payment_id}", response_model=MessageResponse)
async def update_bank_payment(payment_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE bank_payments SET bank_name=%s, payee_name=%s, amount=%s, status=%s,
           narration=%s, updated_at=NOW() WHERE payment_id=%s""",
        (payload.get("bank_name"), payload.get("payee_name"), payload.get("amount"),
         payload.get("status"), payload.get("narration"), payment_id)
    )
    return MessageResponse(message="Payment updated")


# ========================
# Bank Receipts
# ========================
bank_receipts_router = APIRouter(prefix="/bank-receipts")


@bank_receipts_router.get("", response_model=PaginatedResponse)
async def list_bank_receipts(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(receipt_no ILIKE %s OR payer_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM bank_receipts WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM bank_receipts WHERE {where} ORDER BY receipt_date DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@bank_receipts_router.post("", status_code=201)
async def create_bank_receipt(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO bank_receipts (receipt_no, receipt_date, bank_account_id, bank_name,
           payer_id, payer_name, amount, currency, exchange_rate, base_amount,
           receipt_method, reference_no, narration, status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING receipt_id""",
        (payload["receipt_no"], payload["receipt_date"], payload.get("bank_account_id"),
         payload.get("bank_name"), payload.get("payer_id"), payload.get("payer_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("exchange_rate", 1.0),
         payload.get("base_amount"), payload.get("receipt_method"), payload.get("reference_no"),
         payload.get("narration"), payload.get("status", "DRAFT"), current_user.user_id)
    )
    return {"receipt_id": row["receipt_id"] if row else None, "message": "Receipt created"}


# ========================
# Journal Entries
# ========================
journal_entries_router = APIRouter(prefix="/journal-entries")


@journal_entries_router.get("", response_model=PaginatedResponse)
async def list_journal_entries(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(entry_no ILIKE %s OR description ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM journal_entries WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM journal_entries WHERE {where} ORDER BY entry_date DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@journal_entries_router.get("/{entry_id}")
async def get_journal_entry(entry_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM journal_entries WHERE entry_id = %s", (entry_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    lines = execute_query("SELECT * FROM journal_lines WHERE entry_id = %s ORDER BY line_no",
                          (entry_id,))
    result = dict(row)
    result["lines"] = lines
    return result


@journal_entries_router.post("", status_code=201)
async def create_journal_entry(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    lines = payload.get("lines", [])
    total_debit = sum(l.get("debit_amount", 0) for l in lines)
    total_credit = sum(l.get("credit_amount", 0) for l in lines)
    row = execute_one(
        """INSERT INTO journal_entries (entry_no, entry_date, entry_type, description,
           total_debit, total_credit, status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING entry_id""",
        (payload["entry_no"], payload["entry_date"], payload.get("entry_type", "STANDARD"),
         payload.get("description"), total_debit, total_credit,
         payload.get("status", "DRAFT"), current_user.user_id)
    )
    entry_id = row["entry_id"] if row else None
    for i, line in enumerate(lines, 1):
        execute_write(
            """INSERT INTO journal_lines (entry_id, line_no, account_id, account_code,
               account_name, debit_amount, credit_amount, currency, narration)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (entry_id, i, line.get("account_id"), line.get("account_code"),
             line.get("account_name"), line.get("debit_amount", 0), line.get("credit_amount", 0),
             line.get("currency", "USD"), line.get("narration"))
        )
    return {"entry_id": entry_id, "message": "Journal entry created"}


# ========================
# Purchase Bills
# ========================
purchase_bills_router = APIRouter(prefix="/purchase-bills")


@purchase_bills_router.get("", response_model=PaginatedResponse)
async def list_purchase_bills(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(bill_no ILIKE %s OR vendor_name ILIKE %s OR vendor_invoice_no ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM purchase_bills WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM purchase_bills WHERE {where} ORDER BY bill_date DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@purchase_bills_router.post("", status_code=201)
async def create_purchase_bill(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO purchase_bills (bill_no, bill_date, vendor_id, vendor_name,
           vendor_invoice_no, vendor_inv_date, amount, tax_amount, total_amount,
           currency, due_date, job_id, status, remarks, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING bill_id""",
        (payload["bill_no"], payload["bill_date"], payload.get("vendor_id"),
         payload.get("vendor_name"), payload.get("vendor_invoice_no"), payload.get("vendor_inv_date"),
         payload.get("amount"), payload.get("tax_amount", 0), payload.get("total_amount"),
         payload.get("currency", "USD"), payload.get("due_date"), payload.get("job_id"),
         payload.get("status", "DRAFT"), payload.get("remarks"), current_user.user_id)
    )
    return {"bill_id": row["bill_id"] if row else None, "message": "Purchase bill created"}


# ========================
# General Debit Notes
# ========================
debit_notes_router = APIRouter(prefix="/debit-notes")


@debit_notes_router.get("", response_model=PaginatedResponse)
async def list_debit_notes(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(dn_no ILIKE %s OR party_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM general_debit_notes WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM general_debit_notes WHERE {where} ORDER BY dn_date DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@debit_notes_router.post("", status_code=201)
async def create_debit_note(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO general_debit_notes (dn_no, dn_date, party_id, party_name,
           amount, currency, reason, job_id, status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING dn_id""",
        (payload["dn_no"], payload["dn_date"], payload.get("party_id"), payload.get("party_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("reason"),
         payload.get("job_id"), payload.get("status", "DRAFT"), current_user.user_id)
    )
    return {"dn_id": row["dn_id"] if row else None, "message": "Debit note created"}


# ========================
# Customs Export
# ========================
customs_export_router = APIRouter(prefix="/customs-export")


@customs_export_router.get("", response_model=PaginatedResponse)
async def list_customs_exports(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(export_no ILIKE %s OR exporter_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM customs_export WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM customs_export WHERE {where} ORDER BY export_date DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@customs_export_router.post("", status_code=201)
async def create_customs_export(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO customs_export (export_no, export_date, exporter_id, exporter_name,
           consignee_id, consignee_name, commodity_id, commodity_desc, hs_code,
           country_of_origin, destination_country, transport_mode, incoterms,
           total_value, currency, gross_weight, packages, status, remarks, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING export_id""",
        (payload["export_no"], payload["export_date"], payload.get("exporter_id"),
         payload.get("exporter_name"), payload.get("consignee_id"), payload.get("consignee_name"),
         payload.get("commodity_id"), payload.get("commodity_desc"), payload.get("hs_code"),
         payload.get("country_of_origin"), payload.get("destination_country"),
         payload.get("transport_mode"), payload.get("incoterms"), payload.get("total_value"),
         payload.get("currency", "USD"), payload.get("gross_weight"), payload.get("packages"),
         payload.get("status", "DRAFT"), payload.get("remarks"), current_user.user_id)
    )
    return {"export_id": row["export_id"] if row else None, "message": "Customs export created"}