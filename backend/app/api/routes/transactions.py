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
        conditions.append("(JOB_NO ILIKE %s OR BL_NO ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    if transport_mode:
        conditions.append("TRANSPORT_MODE = %s")
        params.append(transport_mode)
    if date_from:
        conditions.append("JOB_DATE >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("JOB_DATE <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.IMPORT_JOBS WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"""SELECT j.*, 
                   s.ORG_NAME AS shipper_name, c.ORG_NAME AS consignee_name
            FROM TXN.IMPORT_JOBS j
            LEFT JOIN ADMIN.ORGANIZATIONS s ON j.SHIPPER_ID = s.ORG_ID
            LEFT JOIN ADMIN.ORGANIZATIONS c ON j.CONSIGNEE_ID = c.ORG_ID
            WHERE {where} ORDER BY j.JOB_DATE DESC, j.JOB_NO DESC LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@import_jobs_router.get("/{job_id}")
async def get_import_job(job_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT j.*, s.ORG_NAME AS shipper_name, c.ORG_NAME AS consignee_name
           FROM TXN.IMPORT_JOBS j
           LEFT JOIN ADMIN.ORGANIZATIONS s ON j.SHIPPER_ID = s.ORG_ID
           LEFT JOIN ADMIN.ORGANIZATIONS c ON j.CONSIGNEE_ID = c.ORG_ID
           WHERE j.JOB_ID = %s""",
        (job_id,), schema="TXN"
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    charges = execute_query(
        "SELECT * FROM TXN.JOB_CHARGES WHERE JOB_ID = %s ORDER BY LINE_ID",
        (job_id,), schema="TXN"
    )
    result = {k.lower(): v for k, v in row.items()}
    result["charges"] = [{k.lower(): v for k, v in c.items()} for c in charges]
    return result


@import_jobs_router.post("", status_code=201)
async def create_import_job(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.IMPORT_JOBS (JOB_NO, JOB_DATE, TRANSPORT_MODE, SHIPPER_ID, CONSIGNEE_ID,
           CARRIER_ID, CARRIER_TYPE, BL_NO, FLIGHT_NO, VESSEL_NAME, VOYAGE_NO, POL, POD,
           ETA, ATA, COMMODITY_ID, GROSS_WEIGHT, CHARGEABLE_WEIGHT, VOLUME_CBM,
           PACKAGES, PACKAGE_TYPE, INCOTERMS, FREIGHT_CURRENCY, FREIGHT_AMOUNT, STATUS, REMARKS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           RETURNING JOB_ID""",
        (payload["job_no"], payload["job_date"], payload.get("transport_mode"),
         payload.get("shipper_id"), payload.get("consignee_id"), payload.get("carrier_id"),
         payload.get("carrier_type"), payload.get("bl_no"), payload.get("flight_no"),
         payload.get("vessel_name"), payload.get("voyage_no"), payload.get("pol"), payload.get("pod"),
         payload.get("eta"), payload.get("ata"), payload.get("commodity_id"),
         payload.get("gross_weight"), payload.get("chargeable_weight"), payload.get("volume_cbm"),
         payload.get("packages"), payload.get("package_type"), payload.get("incoterms"),
         payload.get("freight_currency"), payload.get("freight_amount"),
         payload.get("status", "OPEN"), payload.get("remarks"), current_user.user_id),
        schema="TXN"
    )
    job_id = row["JOB_ID"] if row else None
    # Insert charges if provided
    for charge in payload.get("charges", []):
        execute_write(
            """INSERT INTO TXN.JOB_CHARGES (JOB_ID, CHARGE_ID, CHARGE_NAME, QUANTITY, UNIT_TYPE,
               RATE, CURRENCY, AMOUNT, TAX_AMOUNT, TOTAL_AMOUNT, VENDOR_ID)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (job_id, charge.get("charge_id"), charge.get("charge_name"),
             charge.get("quantity", 1), charge.get("unit_type"), charge.get("rate"),
             charge.get("currency"), charge.get("amount"), charge.get("tax_amount", 0),
             charge.get("total_amount"), charge.get("vendor_id")),
            schema="TXN"
        )
    return {"job_id": job_id, "message": "Import job created"}


@import_jobs_router.put("/{job_id}", response_model=MessageResponse)
async def update_import_job(job_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE TXN.IMPORT_JOBS SET TRANSPORT_MODE=%s, SHIPPER_ID=%s, CONSIGNEE_ID=%s,
           BL_NO=%s, VESSEL_NAME=%s, ETA=%s, ATA=%s, STATUS=%s, REMARKS=%s,
           UPDATED_AT=CURRENT_TIMESTAMP() WHERE JOB_ID=%s""",
        (payload.get("transport_mode"), payload.get("shipper_id"), payload.get("consignee_id"),
         payload.get("bl_no"), payload.get("vessel_name"), payload.get("eta"), payload.get("ata"),
         payload.get("status"), payload.get("remarks"), job_id),
        schema="TXN"
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
        conditions.append("(PAYMENT_NO ILIKE %s OR PAYEE_NAME ILIKE %s OR BANK_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    if date_from:
        conditions.append("PAYMENT_DATE >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("PAYMENT_DATE <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.BANK_PAYMENTS WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.BANK_PAYMENTS WHERE {where} ORDER BY PAYMENT_DATE DESC, PAYMENT_NO DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@bank_payments_router.get("/{payment_id}")
async def get_bank_payment(payment_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM TXN.BANK_PAYMENTS WHERE PAYMENT_ID = %s", (payment_id,), schema="TXN")
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {k.lower(): v for k, v in row.items()}


@bank_payments_router.post("", status_code=201)
async def create_bank_payment(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.BANK_PAYMENTS (PAYMENT_NO, PAYMENT_DATE, BANK_ACCOUNT_ID, BANK_NAME,
           PAYEE_ID, PAYEE_NAME, AMOUNT, CURRENCY, EXCHANGE_RATE, BASE_AMOUNT,
           PAYMENT_METHOD, REFERENCE_NO, NARRATION, STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING PAYMENT_ID""",
        (payload["payment_no"], payload["payment_date"], payload.get("bank_account_id"),
         payload.get("bank_name"), payload.get("payee_id"), payload.get("payee_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("exchange_rate", 1.0),
         payload.get("base_amount"), payload.get("payment_method"), payload.get("reference_no"),
         payload.get("narration"), payload.get("status", "DRAFT"), current_user.user_id),
        schema="TXN"
    )
    return {"payment_id": row["PAYMENT_ID"] if row else None, "message": "Payment created"}


@bank_payments_router.put("/{payment_id}", response_model=MessageResponse)
async def update_bank_payment(payment_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE TXN.BANK_PAYMENTS SET BANK_NAME=%s, PAYEE_NAME=%s, AMOUNT=%s, STATUS=%s,
           NARRATION=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE PAYMENT_ID=%s""",
        (payload.get("bank_name"), payload.get("payee_name"), payload.get("amount"),
         payload.get("status"), payload.get("narration"), payment_id), schema="TXN"
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
        conditions.append("(RECEIPT_NO ILIKE %s OR PAYER_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.BANK_RECEIPTS WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.BANK_RECEIPTS WHERE {where} ORDER BY RECEIPT_DATE DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@bank_receipts_router.post("", status_code=201)
async def create_bank_receipt(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.BANK_RECEIPTS (RECEIPT_NO, RECEIPT_DATE, BANK_ACCOUNT_ID, BANK_NAME,
           PAYER_ID, PAYER_NAME, AMOUNT, CURRENCY, EXCHANGE_RATE, BASE_AMOUNT,
           RECEIPT_METHOD, REFERENCE_NO, NARRATION, STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING RECEIPT_ID""",
        (payload["receipt_no"], payload["receipt_date"], payload.get("bank_account_id"),
         payload.get("bank_name"), payload.get("payer_id"), payload.get("payer_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("exchange_rate", 1.0),
         payload.get("base_amount"), payload.get("receipt_method"), payload.get("reference_no"),
         payload.get("narration"), payload.get("status", "DRAFT"), current_user.user_id),
        schema="TXN"
    )
    return {"receipt_id": row["RECEIPT_ID"] if row else None, "message": "Receipt created"}


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
        conditions.append("(ENTRY_NO ILIKE %s OR DESCRIPTION ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.JOURNAL_ENTRIES WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.JOURNAL_ENTRIES WHERE {where} ORDER BY ENTRY_DATE DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@journal_entries_router.get("/{entry_id}")
async def get_journal_entry(entry_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM TXN.JOURNAL_ENTRIES WHERE ENTRY_ID = %s", (entry_id,), schema="TXN")
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    lines = execute_query("SELECT * FROM TXN.JOURNAL_LINES WHERE ENTRY_ID = %s ORDER BY LINE_NO",
                          (entry_id,), schema="TXN")
    result = {k.lower(): v for k, v in row.items()}
    result["lines"] = [{k.lower(): v for k, v in l.items()} for l in lines]
    return result


@journal_entries_router.post("", status_code=201)
async def create_journal_entry(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    lines = payload.get("lines", [])
    total_debit = sum(l.get("debit_amount", 0) for l in lines)
    total_credit = sum(l.get("credit_amount", 0) for l in lines)
    row = execute_one(
        """INSERT INTO TXN.JOURNAL_ENTRIES (ENTRY_NO, ENTRY_DATE, ENTRY_TYPE, DESCRIPTION,
           TOTAL_DEBIT, TOTAL_CREDIT, STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ENTRY_ID""",
        (payload["entry_no"], payload["entry_date"], payload.get("entry_type", "STANDARD"),
         payload.get("description"), total_debit, total_credit,
         payload.get("status", "DRAFT"), current_user.user_id),
        schema="TXN"
    )
    entry_id = row["ENTRY_ID"] if row else None
    for i, line in enumerate(lines, 1):
        execute_write(
            """INSERT INTO TXN.JOURNAL_LINES (ENTRY_ID, LINE_NO, ACCOUNT_ID, ACCOUNT_CODE,
               ACCOUNT_NAME, DEBIT_AMOUNT, CREDIT_AMOUNT, CURRENCY, NARRATION)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (entry_id, i, line.get("account_id"), line.get("account_code"),
             line.get("account_name"), line.get("debit_amount", 0), line.get("credit_amount", 0),
             line.get("currency", "USD"), line.get("narration")),
            schema="TXN"
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
        conditions.append("(BILL_NO ILIKE %s OR VENDOR_NAME ILIKE %s OR VENDOR_INVOICE_NO ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.PURCHASE_BILLS WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.PURCHASE_BILLS WHERE {where} ORDER BY BILL_DATE DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@purchase_bills_router.post("", status_code=201)
async def create_purchase_bill(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.PURCHASE_BILLS (BILL_NO, BILL_DATE, VENDOR_ID, VENDOR_NAME,
           VENDOR_INVOICE_NO, VENDOR_INV_DATE, AMOUNT, TAX_AMOUNT, TOTAL_AMOUNT,
           CURRENCY, DUE_DATE, JOB_ID, STATUS, REMARKS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING BILL_ID""",
        (payload["bill_no"], payload["bill_date"], payload.get("vendor_id"),
         payload.get("vendor_name"), payload.get("vendor_invoice_no"), payload.get("vendor_inv_date"),
         payload.get("amount"), payload.get("tax_amount", 0), payload.get("total_amount"),
         payload.get("currency", "USD"), payload.get("due_date"), payload.get("job_id"),
         payload.get("status", "DRAFT"), payload.get("remarks"), current_user.user_id),
        schema="TXN"
    )
    return {"bill_id": row["BILL_ID"] if row else None, "message": "Purchase bill created"}


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
        conditions.append("(DN_NO ILIKE %s OR PARTY_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.GENERAL_DEBIT_NOTES WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.GENERAL_DEBIT_NOTES WHERE {where} ORDER BY DN_DATE DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@debit_notes_router.post("", status_code=201)
async def create_debit_note(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.GENERAL_DEBIT_NOTES (DN_NO, DN_DATE, PARTY_ID, PARTY_NAME,
           AMOUNT, CURRENCY, REASON, JOB_ID, STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING DN_ID""",
        (payload["dn_no"], payload["dn_date"], payload.get("party_id"), payload.get("party_name"),
         payload["amount"], payload.get("currency", "USD"), payload.get("reason"),
         payload.get("job_id"), payload.get("status", "DRAFT"), current_user.user_id),
        schema="TXN"
    )
    return {"dn_id": row["DN_ID"] if row else None, "message": "Debit note created"}


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
        conditions.append("(EXPORT_NO ILIKE %s OR EXPORTER_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM TXN.CUSTOMS_EXPORT WHERE {where}",
                        tuple(params), schema="TXN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM TXN.CUSTOMS_EXPORT WHERE {where} ORDER BY EXPORT_DATE DESC LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="TXN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@customs_export_router.post("", status_code=201)
async def create_customs_export(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO TXN.CUSTOMS_EXPORT (EXPORT_NO, EXPORT_DATE, EXPORTER_ID, EXPORTER_NAME,
           CONSIGNEE_ID, CONSIGNEE_NAME, COMMODITY_ID, COMMODITY_DESC, HS_CODE,
           COUNTRY_OF_ORIGIN, DESTINATION_COUNTRY, TRANSPORT_MODE, INCOTERMS,
           TOTAL_VALUE, CURRENCY, GROSS_WEIGHT, PACKAGES, STATUS, REMARKS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING EXPORT_ID""",
        (payload["export_no"], payload["export_date"], payload.get("exporter_id"),
         payload.get("exporter_name"), payload.get("consignee_id"), payload.get("consignee_name"),
         payload.get("commodity_id"), payload.get("commodity_desc"), payload.get("hs_code"),
         payload.get("country_of_origin"), payload.get("destination_country"),
         payload.get("transport_mode"), payload.get("incoterms"), payload.get("total_value"),
         payload.get("currency", "USD"), payload.get("gross_weight"), payload.get("packages"),
         payload.get("status", "DRAFT"), payload.get("remarks"), current_user.user_id),
        schema="TXN"
    )
    return {"export_id": row["EXPORT_ID"] if row else None, "message": "Customs export created"}
