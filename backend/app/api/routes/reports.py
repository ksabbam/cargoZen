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
    row = execute_one("SELECT COUNT(*) AS cnt FROM import_jobs WHERE status IN ('OPEN', 'IN_PROGRESS')")
    stats["active_import_jobs"] = row["cnt"] if row else 0

    # Today's payments
    row = execute_one(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM bank_payments WHERE payment_date = CURRENT_DATE"
    )
    stats["todays_payments"] = float(row["total"]) if row else 0

    # Today's receipts
    row = execute_one(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM bank_receipts WHERE receipt_date = CURRENT_DATE"
    )
    stats["todays_receipts"] = float(row["total"]) if row else 0

    # Pending approvals
    row = execute_one(
        "SELECT COUNT(*) AS cnt FROM organizations WHERE approval_status = 'PENDING'"
    )
    stats["pending_approvals"] = row["cnt"] if row else 0

    # Total organizations
    row = execute_one("SELECT COUNT(*) AS cnt FROM organizations WHERE is_active = TRUE")
    stats["total_organizations"] = row["cnt"] if row else 0

    # Jobs by transport mode
    rows = execute_query(
        "SELECT transport_mode, COUNT(*) AS cnt FROM import_jobs GROUP BY transport_mode"
    )
    stats["jobs_by_mode"] = rows

    # Recent jobs
    recent_jobs = execute_query(
        """SELECT j.job_no, j.job_date, j.transport_mode, j.status,
                  s.org_name AS shipper_name
           FROM import_jobs j
           LEFT JOIN organizations s ON j.shipper_id = s.org_id
           ORDER BY j.created_at DESC LIMIT 5"""
    )
    stats["recent_jobs"] = recent_jobs

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
        conditions.append("j.job_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("j.job_date <= %s")
        params.append(date_to)
    if transport_mode:
        conditions.append("j.transport_mode = %s")
        params.append(transport_mode)
    if status:
        conditions.append("j.status = %s")
        params.append(status)
    where = " AND ".join(conditions)

    rows = execute_query(
        f"""SELECT j.job_no, j.job_date, j.transport_mode, j.bl_no,
                   s.org_name AS shipper, c.org_name AS consignee,
                   j.pol, j.pod, j.eta, j.ata,
                   j.gross_weight, j.packages, j.status
            FROM import_jobs j
            LEFT JOIN organizations s ON j.shipper_id = s.org_id
            LEFT JOIN organizations c ON j.consignee_id = c.org_id
            WHERE {where}
            ORDER BY j.job_date DESC""",
        tuple(params)
    )
    return {"data": rows, "total": len(rows)}


@router.get("/financial-report")
async def financial_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if date_from:
        conditions.append("je.entry_date >= %s")
        params.append(date_from)
    if date_to:
        conditions.append("je.entry_date <= %s")
        params.append(date_to)
    where = " AND ".join(conditions)

    rows = execute_query(
        f"""SELECT jl.account_code, jl.account_name,
                   SUM(jl.debit_amount) AS total_debit,
                   SUM(jl.credit_amount) AS total_credit
            FROM journal_lines jl
            JOIN journal_entries je ON jl.entry_id = je.entry_id
            WHERE je.status = 'POSTED' AND {where}
            GROUP BY jl.account_code, jl.account_name
            ORDER BY jl.account_code""",
        tuple(params)
    )
    return {"data": rows}


@router.get("/ar-aging")
async def ar_aging_report(current_user: UserResponse = Depends(get_current_active_user)):
    rows = execute_query(
        """SELECT o.org_name AS customer, o.org_code,
                  COUNT(pb.bill_id) AS bill_count,
                  SUM(pb.total_amount) AS total_amount
           FROM purchase_bills pb
           LEFT JOIN organizations o ON pb.vendor_id = o.org_id
           WHERE pb.status NOT IN ('PAID', 'CANCELLED')
           GROUP BY o.org_name, o.org_code
           ORDER BY total_amount DESC"""
    )
    return {"data": rows}