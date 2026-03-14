from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_current_active_user
from app.core.database import execute_query, execute_one, execute_write
from app.models.schemas import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    PaginatedResponse, MessageResponse, UserResponse
)
import math

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def build_org_filters(search: Optional[str], org_type: Optional[str],
                      approval_status: Optional[str], is_active: Optional[bool]):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(org_code ILIKE %s OR org_name ILIKE %s OR org_short_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if org_type:
        conditions.append("org_type = %s")
        params.append(org_type)
    if approval_status:
        conditions.append("approval_status = %s")
        params.append(approval_status)
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    return " AND ".join(conditions), params


@router.get("", response_model=PaginatedResponse)
async def list_organizations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    org_type: Optional[str] = None,
    approval_status: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = "org_name",
    sort_order: str = "ASC",
    current_user: UserResponse = Depends(get_current_active_user)
):
    where_clause, params = build_org_filters(search, org_type, approval_status, is_active)
    offset = (page - 1) * limit

    count_row = execute_one(
        f"SELECT COUNT(*) AS cnt FROM organizations WHERE {where_clause}",
        tuple(params)
    )
    total = count_row["cnt"] if count_row else 0

    rows = execute_query(
        f"""SELECT o.*, g.group_name FROM organizations o
            LEFT JOIN organization_groups g ON o.group_id = g.group_id
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset])
    )

    return PaginatedResponse(
        data=rows,
        total=total, page=page, limit=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 1
    )


@router.get("/search-select", response_model=List[dict])
async def search_organizations(
    q: Optional[str] = None,
    type_filter: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    params = []
    conditions = ["is_active = TRUE", "approval_status = 'APPROVED'"]
    if q:
        conditions.append("(org_code ILIKE %s OR org_name ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    if type_filter == "customer":
        conditions.append("is_customer = TRUE")
    elif type_filter == "vendor":
        conditions.append("is_vendor = TRUE")
    elif type_filter == "agent":
        conditions.append("is_agent = TRUE")

    rows = execute_query(
        f"SELECT org_id AS id, org_code AS code, org_name AS name FROM organizations "
        f"WHERE {' AND '.join(conditions)} LIMIT 50",
        tuple(params)
    )
    return rows


@router.get("/{org_id}", response_model=dict)
async def get_organization(
    org_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    row = execute_one(
        """SELECT o.*, g.group_name FROM organizations o
           LEFT JOIN organization_groups g ON o.group_id = g.group_id
           WHERE o.org_id = %s""",
        (org_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Organization not found")
    return row


@router.post("", response_model=dict, status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    existing = execute_one(
        "SELECT org_id FROM organizations WHERE org_code = %s",
        (payload.org_code,)
    )
    if existing:
        raise HTTPException(status_code=400, detail="Organization code already exists")

    row = execute_one(
        """INSERT INTO organizations
           (org_code, org_name, org_short_name, group_id, org_type,
            is_customer, is_vendor, is_agent, is_carrier,
            address_line1, address_line2, city, state, country, postal_code,
            phone, email, website, tax_id, credit_limit, credit_days, currency,
            approval_status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDING',%s)
           RETURNING org_id""",
        (payload.org_code, payload.org_name, payload.org_short_name, payload.group_id,
         payload.org_type, payload.is_customer, payload.is_vendor, payload.is_agent,
         payload.is_carrier, payload.address_line1, payload.address_line2, payload.city,
         payload.state, payload.country, payload.postal_code, payload.phone, payload.email,
         payload.website, payload.tax_id, payload.credit_limit, payload.credit_days,
         payload.currency, current_user.user_id)
    )
    return {"org_id": row["org_id"] if row else None, "message": "Organization created successfully"}


@router.put("/{org_id}", response_model=MessageResponse)
async def update_organization(
    org_id: int,
    payload: OrganizationUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    existing = execute_one(
        "SELECT org_id FROM organizations WHERE org_id = %s", (org_id,)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Organization not found")

    execute_write(
        """UPDATE organizations SET
           org_name=%s, org_short_name=%s, group_id=%s, org_type=%s,
           is_customer=%s, is_vendor=%s, is_agent=%s, is_carrier=%s,
           address_line1=%s, address_line2=%s, city=%s, state=%s, country=%s,
           postal_code=%s, phone=%s, email=%s, website=%s, tax_id=%s,
           credit_limit=%s, credit_days=%s, currency=%s, updated_at=NOW()
           WHERE org_id=%s""",
        (payload.org_name, payload.org_short_name, payload.group_id, payload.org_type,
         payload.is_customer, payload.is_vendor, payload.is_agent, payload.is_carrier,
         payload.address_line1, payload.address_line2, payload.city, payload.state,
         payload.country, payload.postal_code, payload.phone, payload.email, payload.website,
         payload.tax_id, payload.credit_limit, payload.credit_days, payload.currency, org_id)
    )
    return MessageResponse(message="Organization updated successfully")


@router.patch("/{org_id}/approval", response_model=MessageResponse)
async def update_approval_status(
    org_id: int,
    body: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    status_val = body.get("approval_status")
    if status_val not in ("APPROVED", "REJECTED", "PENDING"):
        raise HTTPException(status_code=400, detail="Invalid approval status")

    execute_write(
        """UPDATE organizations SET
           approval_status=%s, approval_date=NOW(), approved_by=%s,
           updated_at=NOW()
           WHERE org_id=%s""",
        (status_val, current_user.user_id, org_id)
    )
    return MessageResponse(message=f"Organization {status_val.lower()} successfully")


@router.delete("/{org_id}", response_model=MessageResponse)
async def delete_organization(
    org_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    execute_write(
        "UPDATE organizations SET is_active=FALSE, updated_at=NOW() WHERE org_id=%s",
        (org_id,)
    )
    return MessageResponse(message="Organization deactivated successfully")