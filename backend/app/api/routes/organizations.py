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
        conditions.append("(ORG_CODE ILIKE %s OR ORG_NAME ILIKE %s OR ORG_SHORT_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if org_type:
        conditions.append("ORG_TYPE = %s")
        params.append(org_type)
    if approval_status:
        conditions.append("APPROVAL_STATUS = %s")
        params.append(approval_status)
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
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
    sort_by: str = "ORG_NAME",
    sort_order: str = "ASC",
    current_user: UserResponse = Depends(get_current_active_user)
):
    where_clause, params = build_org_filters(search, org_type, approval_status, is_active)
    offset = (page - 1) * limit

    count_row = execute_one(
        f"SELECT COUNT(*) AS CNT FROM ADMIN.ORGANIZATIONS WHERE {where_clause}",
        tuple(params), schema="ADMIN"
    )
    total = count_row["CNT"] if count_row else 0

    rows = execute_query(
        f"""SELECT o.*, g.GROUP_NAME FROM ADMIN.ORGANIZATIONS o
            LEFT JOIN ADMIN.ORGANIZATION_GROUPS g ON o.GROUP_ID = g.GROUP_ID
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset]), schema="ADMIN"
    )

    return PaginatedResponse(
        data=[{k.lower(): v for k, v in r.items()} for r in rows],
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
    conditions = ["IS_ACTIVE = TRUE", "APPROVAL_STATUS = 'APPROVED'"]
    if q:
        conditions.append("(ORG_CODE ILIKE %s OR ORG_NAME ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%"])
    if type_filter == "customer":
        conditions.append("IS_CUSTOMER = TRUE")
    elif type_filter == "vendor":
        conditions.append("IS_VENDOR = TRUE")
    elif type_filter == "agent":
        conditions.append("IS_AGENT = TRUE")

    rows = execute_query(
        f"SELECT ORG_ID AS id, ORG_CODE AS code, ORG_NAME AS name FROM ADMIN.ORGANIZATIONS "
        f"WHERE {' AND '.join(conditions)} LIMIT 50",
        tuple(params), schema="ADMIN"
    )
    return [{k.lower(): v for k, v in r.items()} for r in rows]


@router.get("/{org_id}", response_model=dict)
async def get_organization(
    org_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    row = execute_one(
        """SELECT o.*, g.GROUP_NAME FROM ADMIN.ORGANIZATIONS o
           LEFT JOIN ADMIN.ORGANIZATION_GROUPS g ON o.GROUP_ID = g.GROUP_ID
           WHERE o.ORG_ID = %s""",
        (org_id,), schema="ADMIN"
    )
    if not row:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {k.lower(): v for k, v in row.items()}


@router.post("", response_model=dict, status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    existing = execute_one(
        "SELECT ORG_ID FROM ADMIN.ORGANIZATIONS WHERE ORG_CODE = %s",
        (payload.org_code,), schema="ADMIN"
    )
    if existing:
        raise HTTPException(status_code=400, detail="Organization code already exists")

    row = execute_one(
        """INSERT INTO ADMIN.ORGANIZATIONS
           (ORG_CODE, ORG_NAME, ORG_SHORT_NAME, GROUP_ID, ORG_TYPE,
            IS_CUSTOMER, IS_VENDOR, IS_AGENT, IS_CARRIER,
            ADDRESS_LINE1, ADDRESS_LINE2, CITY, STATE, COUNTRY, POSTAL_CODE,
            PHONE, EMAIL, WEBSITE, TAX_ID, CREDIT_LIMIT, CREDIT_DAYS, CURRENCY,
            APPROVAL_STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDING',%s)
           RETURNING ORG_ID""",
        (payload.org_code, payload.org_name, payload.org_short_name, payload.group_id,
         payload.org_type, payload.is_customer, payload.is_vendor, payload.is_agent,
         payload.is_carrier, payload.address_line1, payload.address_line2, payload.city,
         payload.state, payload.country, payload.postal_code, payload.phone, payload.email,
         payload.website, payload.tax_id, payload.credit_limit, payload.credit_days,
         payload.currency, current_user.user_id),
        schema="ADMIN"
    )
    return {"org_id": row["ORG_ID"] if row else None, "message": "Organization created successfully"}


@router.put("/{org_id}", response_model=MessageResponse)
async def update_organization(
    org_id: int,
    payload: OrganizationUpdate,
    current_user: UserResponse = Depends(get_current_active_user)
):
    existing = execute_one(
        "SELECT ORG_ID FROM ADMIN.ORGANIZATIONS WHERE ORG_ID = %s", (org_id,), schema="ADMIN"
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Organization not found")

    execute_write(
        """UPDATE ADMIN.ORGANIZATIONS SET
           ORG_NAME=%s, ORG_SHORT_NAME=%s, GROUP_ID=%s, ORG_TYPE=%s,
           IS_CUSTOMER=%s, IS_VENDOR=%s, IS_AGENT=%s, IS_CARRIER=%s,
           ADDRESS_LINE1=%s, ADDRESS_LINE2=%s, CITY=%s, STATE=%s, COUNTRY=%s,
           POSTAL_CODE=%s, PHONE=%s, EMAIL=%s, WEBSITE=%s, TAX_ID=%s,
           CREDIT_LIMIT=%s, CREDIT_DAYS=%s, CURRENCY=%s, UPDATED_AT=CURRENT_TIMESTAMP()
           WHERE ORG_ID=%s""",
        (payload.org_name, payload.org_short_name, payload.group_id, payload.org_type,
         payload.is_customer, payload.is_vendor, payload.is_agent, payload.is_carrier,
         payload.address_line1, payload.address_line2, payload.city, payload.state,
         payload.country, payload.postal_code, payload.phone, payload.email, payload.website,
         payload.tax_id, payload.credit_limit, payload.credit_days, payload.currency, org_id),
        schema="ADMIN"
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
        """UPDATE ADMIN.ORGANIZATIONS SET
           APPROVAL_STATUS=%s, APPROVAL_DATE=CURRENT_TIMESTAMP(), APPROVED_BY=%s,
           UPDATED_AT=CURRENT_TIMESTAMP()
           WHERE ORG_ID=%s""",
        (status_val, current_user.user_id, org_id), schema="ADMIN"
    )
    return MessageResponse(message=f"Organization {status_val.lower()} successfully")


@router.delete("/{org_id}", response_model=MessageResponse)
async def delete_organization(
    org_id: int,
    current_user: UserResponse = Depends(get_current_active_user)
):
    execute_write(
        "UPDATE ADMIN.ORGANIZATIONS SET IS_ACTIVE=FALSE, UPDATED_AT=CURRENT_TIMESTAMP() WHERE ORG_ID=%s",
        (org_id,), schema="ADMIN"
    )
    return MessageResponse(message="Organization deactivated successfully")
