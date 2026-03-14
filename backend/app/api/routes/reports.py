from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.api.deps import get_current_active_user
from app.core.database import execute_query, execute_one
from app.models.schemas import UserResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard-summary")
async def dashboard_summary(current_user: UserResponse = Depends(get_current_active_user)):
    """Get KPI summary for the dashboard."""
    stats = {}

    # Active import jobs
    row = execute_one("SELECT COUNT(*) AS CNT FROM TXN.IMPORT_JOBS WHERE STATUS IN ('OPEN', 'IN_PROGRESS')",
                      schema="TXN")
    stats["active_import_jobs"] = row["CNT"] if row else 0

    # Today's payments
    row = execute_one(
        "SELECT COALESCE(SUM(AMOUNT), 0) AS TOTAL FROM TXN.BANK_PAYMENTS WHERE PAYMENT_DATE = CURRENT_DATE()",
        schema="TXN"
    )
    stats["todays_payments"] = float(row["TOTAL"]) if row else 0

    # Today's receipts
    row = execute_one(
        "SELECT COALESCE(SUM(AMOUNT), 0) AS TOTAL FROM TXN.BANK_RECEIPTS WHERE RECEIPT_DATE = CURRENT_DATE()",
        schema="TXN"
    )
    stats["todays_receipts"] = float(row["TOTAL"]) if row else 0

    # Pending approvals
    row = execute_one(
        "SELECT COUNT(*) AS CNT FROM ADMIN.ORGANIZATIONS WHERE APPROVAL_STATUS = 'PENDING'",
        schema="ADMIN"
    )
    stats["pending_approvals"] = row["CNT"] if row else 0

    # Total organizations
    row = execute_one("SELECT COUNT(*) AS CNT FROM ADMIN.ORGANIZATIONS WHERE IS_ACTIVE = TRUE",
                      schema="ADMIN")
    stats["total_organizations"] = row["CNT"] if row else 0

    # Jobs by transport mode
    rows = execute_query(
        "SELECT TRANSPORT_MODE, COUNT(*) AS CNT FROM TXN.IMPORT_JOBS GROUP BY TRANSPORT_MODE",
        schema="TXN"
    )
    stats["jobs_by_mode"] = [{k.lower(): v for k, v in r.items()} for r in rows]

    # Recent jobs
    recent_jobs = execute_query(
        """SELECT j.JOB_NO, j.JOB_DATE, j.TRANSPORT_MODE, j.STATUS,
                  s.ORG_NAME AS shipper_name
           FROM TXN.IMPORT_JOBS j
           LEFT JOIN ADMIN.ORGANIZATIONS s ON j.SHIPPER_ID = s.ORG_ID
           ORDER BY j.CREATED_AT DESC LIMIT 5""",
        schema="TXN"
    )
    stats["recent_jobs"] = [{k.lower(): v for k, v in r.items()} for r in recent_jobs]

    return stats


@router.get("/import-jobs-report")
async def import_jobs_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    transport_mode: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if date_from:
        conditions.append("j.JOB_DATE >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("j.JOB_DATE <= %s")
        params.append(date_to)
    if transport_mode:
        conditions.append("j.TRANSPORT_MODE = %s")
        params.append(transport_mode)
    if status:
        conditions.append("j.STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)

    rows = execute_query(
        f"""SELECT j.JOB_NO, j.JOB_DATE, j.TRANSPORT_MODE, j.BL_NO,
                   s.ORG_NAME AS shipper, c.ORG_NAME AS consignee,
                   j.POL, j.POD, j.ETA, j.ATA,
                   j.GROSS_WEIGHT, j.PACKAGES, j.STATUS
            FROM TXN.IMPORT_JOBS j
            LEFT JOIN ADMIN.ORGANIZATIONS s ON j.SHIPPER_ID = s.ORG_ID
            LEFT JOIN ADMIN.ORGANIZATIONS c ON j.CONSIGNEE_ID = c.ORG_ID
            WHERE {where}
            ORDER BY j.JOB_DATE DESC""",
        tuple(params), schema="TXN"
    )
    return {"data": [{k.lower(): v for k, v in r.items()} for r in rows],
            "total": len(rows)}


@router.get("/financial-report")
async def financial_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if date_from:
        conditions.append("ENTRY_DATE >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("ENTRY_DATE <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)

    rows = execute_query(
        f"""SELECT jl.ACCOUNT_CODE, jl.ACCOUNT_NAME,
                   SUM(jl.DEBIT_AMOUNT) AS total_debit,
                   SUM(jl.CREDIT_AMOUNT) AS total_credit
            FROM TXN.JOURNAL_LINES jl
            JOIN TXN.JOURNAL_ENTRIES je ON jl.ENTRY_ID = je.ENTRY_ID
            WHERE je.STATUS = 'POSTED' AND {where}
            GROUP BY jl.ACCOUNT_CODE, jl.ACCOUNT_NAME
            ORDER BY jl.ACCOUNT_CODE""",
        tuple(params), schema="TXN"
    )
    return {"data": [{k.lower(): v for k, v in r.items()} for r in rows]}


@router.get("/ar-aging")
async def ar_aging_report(current_user: UserResponse = Depends(get_current_active_user)):
    """Accounts Receivable Aging Report."""
    rows = execute_query(
        """SELECT o.ORG_NAME AS customer, o.ORG_CODE,
                  COUNT(pb.BILL_ID) AS bill_count,
                  SUM(pb.TOTAL_AMOUNT) AS total_amount
           FROM TXN.PURCHASE_BILLS pb
           LEFT JOIN ADMIN.ORGANIZATIONS o ON pb.VENDOR_ID = o.ORG_ID
           WHERE pb.STATUS NOT IN ('PAID', 'CANCELLED')
           GROUP BY o.ORG_NAME, o.ORG_CODE
           ORDER BY total_amount DESC""",
        schema="TXN"
    )
    return {"data": [{k.lower(): v for k, v in r.items()} for r in rows]}
