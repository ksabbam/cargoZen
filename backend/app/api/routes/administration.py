from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_current_active_user
from app.core.database import execute_query, execute_one, execute_write
from app.models.schemas import PaginatedResponse, MessageResponse, UserResponse
import math
import json

router = APIRouter(tags=["Administration"])

# ========================
# Organization Groups
# ========================
org_groups_router = APIRouter(prefix="/org-groups")


@org_groups_router.get("", response_model=PaginatedResponse)
async def list_org_groups(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, is_active: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(group_code ILIKE %s OR group_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    total = execute_one(f"SELECT COUNT(*) AS cnt FROM organization_groups WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM organization_groups WHERE {where} ORDER BY group_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@org_groups_router.get("/{group_id}")
async def get_org_group(group_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM organization_groups WHERE group_id = %s", (group_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Group not found")
    return row


@org_groups_router.post("", status_code=201)
async def create_org_group(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO organization_groups (group_code, group_name, group_type, description, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s) RETURNING group_id""",
        (payload["group_code"], payload["group_name"], payload.get("group_type"),
         payload.get("description"), payload.get("is_active", True), current_user.user_id)
    )
    return {"group_id": row["group_id"] if row else None, "message": "Group created"}


@org_groups_router.put("/{group_id}", response_model=MessageResponse)
async def update_org_group(group_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE organization_groups SET group_name=%s, group_type=%s, description=%s, is_active=%s, updated_at=NOW() WHERE group_id=%s",
        (payload.get("group_name"), payload.get("group_type"), payload.get("description"),
         payload.get("is_active", True), group_id)
    )
    return MessageResponse(message="Group updated")


@org_groups_router.delete("/{group_id}", response_model=MessageResponse)
async def delete_org_group(group_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE organization_groups SET is_active=FALSE WHERE group_id=%s", (group_id,))
    return MessageResponse(message="Group deactivated")


# ========================
# Airlines
# ========================
airlines_router = APIRouter(prefix="/airlines")


@airlines_router.get("", response_model=PaginatedResponse)
async def list_airlines(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, is_active: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(airline_code ILIKE %s OR airline_name ILIKE %s OR iata_code ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    total = execute_one(f"SELECT COUNT(*) AS cnt FROM airlines WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM airlines WHERE {where} ORDER BY airline_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@airlines_router.get("/search-select", response_model=List[dict])
async def search_airlines(q: Optional[str] = None, current_user: UserResponse = Depends(get_current_active_user)):
    params = []
    conditions = ["is_active = TRUE"]
    if q:
        conditions.append("(airline_code ILIKE %s OR airline_name ILIKE %s OR iata_code ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    rows = execute_query(
        f"SELECT airline_id AS id, airline_code AS code, airline_name AS name, iata_code "
        f"FROM airlines WHERE {' AND '.join(conditions)} LIMIT 50",
        tuple(params)
    )
    return rows


@airlines_router.get("/{airline_id}")
async def get_airline(airline_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM airlines WHERE airline_id = %s", (airline_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Airline not found")
    return row


@airlines_router.post("", status_code=201)
async def create_airline(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO airlines (airline_code, iata_code, icao_code, airline_name, country,
           headquarters, phone, email, alliance, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING airline_id""",
        (payload["airline_code"], payload.get("iata_code"), payload.get("icao_code"),
         payload["airline_name"], payload.get("country"), payload.get("headquarters"),
         payload.get("phone"), payload.get("email"), payload.get("alliance"),
         payload.get("is_active", True), current_user.user_id)
    )
    return {"airline_id": row["airline_id"] if row else None, "message": "Airline created"}


@airlines_router.put("/{airline_id}", response_model=MessageResponse)
async def update_airline(airline_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE airlines SET airline_code=%s, iata_code=%s, airline_name=%s, country=%s,
           is_active=%s, updated_at=NOW() WHERE airline_id=%s""",
        (payload.get("airline_code"), payload.get("iata_code"), payload.get("airline_name"),
         payload.get("country"), payload.get("is_active", True), airline_id)
    )
    return MessageResponse(message="Airline updated")


@airlines_router.delete("/{airline_id}", response_model=MessageResponse)
async def delete_airline(airline_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE airlines SET is_active=FALSE WHERE airline_id=%s", (airline_id,))
    return MessageResponse(message="Airline deactivated")


# ========================
# Shipping Lines
# ========================
shipping_lines_router = APIRouter(prefix="/shipping-lines")


@shipping_lines_router.get("", response_model=PaginatedResponse)
async def list_shipping_lines(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, is_active: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(line_code ILIKE %s OR line_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM shipping_lines WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM shipping_lines WHERE {where} ORDER BY line_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@shipping_lines_router.get("/{line_id}")
async def get_shipping_line(line_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM shipping_lines WHERE line_id = %s", (line_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Shipping line not found")
    return row


@shipping_lines_router.post("", status_code=201)
async def create_shipping_line(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO shipping_lines (line_code, scac_code, line_name, country,
           headquarters, phone, email, website, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING line_id""",
        (payload["line_code"], payload.get("scac_code"), payload["line_name"],
         payload.get("country"), payload.get("headquarters"), payload.get("phone"),
         payload.get("email"), payload.get("website"), payload.get("is_active", True),
         current_user.user_id)
    )
    return {"line_id": row["line_id"] if row else None, "message": "Shipping line created"}


@shipping_lines_router.put("/{line_id}", response_model=MessageResponse)
async def update_shipping_line(line_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE shipping_lines SET line_name=%s, country=%s, is_active=%s, updated_at=NOW() WHERE line_id=%s",
        (payload.get("line_name"), payload.get("country"), payload.get("is_active", True), line_id)
    )
    return MessageResponse(message="Shipping line updated")


@shipping_lines_router.delete("/{line_id}", response_model=MessageResponse)
async def delete_shipping_line(line_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE shipping_lines SET is_active=FALSE WHERE line_id=%s", (line_id,))
    return MessageResponse(message="Shipping line deactivated")


# ========================
# Charge Master
# ========================
charge_master_router = APIRouter(prefix="/charge-master")


@charge_master_router.get("", response_model=PaginatedResponse)
async def list_charges(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, charge_type: Optional[str] = None,
    applicable_for: Optional[str] = None, is_active: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(charge_code ILIKE %s OR charge_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if charge_type:
        conditions.append("charge_type = %s")
        params.append(charge_type)
    if applicable_for:
        conditions.append("(applicable_for = %s OR applicable_for = 'BOTH')")
        params.append(applicable_for)
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM charge_master WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM charge_master WHERE {where} ORDER BY charge_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@charge_master_router.get("/{charge_id}")
async def get_charge(charge_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM charge_master WHERE charge_id = %s", (charge_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Charge not found")
    return row


@charge_master_router.post("", status_code=201)
async def create_charge(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO charge_master (charge_code, charge_name, charge_type, charge_category,
           applicable_for, gl_account_id, is_taxable, unit_type, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING charge_id""",
        (payload["charge_code"], payload["charge_name"], payload.get("charge_type"),
         payload.get("charge_category"), payload.get("applicable_for"),
         payload.get("gl_account_id"), payload.get("is_taxable", False),
         payload.get("unit_type"), payload.get("is_active", True), current_user.user_id)
    )
    return {"charge_id": row["charge_id"] if row else None, "message": "Charge created"}


@charge_master_router.put("/{charge_id}", response_model=MessageResponse)
async def update_charge(charge_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE charge_master SET charge_name=%s, charge_type=%s, charge_category=%s,
           applicable_for=%s, is_active=%s, updated_at=NOW() WHERE charge_id=%s""",
        (payload.get("charge_name"), payload.get("charge_type"), payload.get("charge_category"),
         payload.get("applicable_for"), payload.get("is_active", True), charge_id)
    )
    return MessageResponse(message="Charge updated")


@charge_master_router.delete("/{charge_id}", response_model=MessageResponse)
async def delete_charge(charge_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE charge_master SET is_active=FALSE WHERE charge_id=%s", (charge_id,))
    return MessageResponse(message="Charge deactivated")


# ========================
# Accounts
# ========================
accounts_router = APIRouter(prefix="/accounts")


@accounts_router.get("", response_model=PaginatedResponse)
async def list_accounts(
    page: int = Query(1, ge=1), limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None, account_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(account_code ILIKE %s OR account_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if account_type:
        conditions.append("account_type = %s")
        params.append(account_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM accounts WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM accounts WHERE {where} ORDER BY account_code LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@accounts_router.get("/{account_id}")
async def get_account(account_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM accounts WHERE account_id = %s", (account_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")
    return row


@accounts_router.post("", status_code=201)
async def create_account(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO accounts (account_code, account_name, account_type, account_subtype,
           parent_account_id, description, opening_balance, currency, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING account_id""",
        (payload["account_code"], payload["account_name"], payload["account_type"],
         payload.get("account_subtype"), payload.get("parent_account_id"),
         payload.get("description"), payload.get("opening_balance", 0),
         payload.get("currency", "USD"), payload.get("is_active", True), current_user.user_id)
    )
    return {"account_id": row["account_id"] if row else None, "message": "Account created"}


@accounts_router.put("/{account_id}", response_model=MessageResponse)
async def update_account(account_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE accounts SET account_name=%s, account_type=%s, account_subtype=%s,
           is_active=%s, updated_at=NOW() WHERE account_id=%s""",
        (payload.get("account_name"), payload.get("account_type"), payload.get("account_subtype"),
         payload.get("is_active", True), account_id)
    )
    return MessageResponse(message="Account updated")


# ========================
# Commodities
# ========================
commodities_router = APIRouter(prefix="/commodities")


@commodities_router.get("", response_model=PaginatedResponse)
async def list_commodities(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, is_active: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(commodity_code ILIKE %s OR commodity_name ILIKE %s OR hs_code ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM commodities WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM commodities WHERE {where} ORDER BY commodity_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@commodities_router.get("/{commodity_id}")
async def get_commodity(commodity_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM commodities WHERE commodity_id = %s", (commodity_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Commodity not found")
    return row


@commodities_router.post("", status_code=201)
async def create_commodity(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO commodities (commodity_code, commodity_name, hs_code, commodity_group,
           is_dangerous, dangerous_class, un_number, description, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING commodity_id""",
        (payload["commodity_code"], payload["commodity_name"], payload.get("hs_code"),
         payload.get("commodity_group"), payload.get("is_dangerous", False),
         payload.get("dangerous_class"), payload.get("un_number"), payload.get("description"),
         payload.get("is_active", True), current_user.user_id)
    )
    return {"commodity_id": row["commodity_id"] if row else None, "message": "Commodity created"}


@commodities_router.put("/{commodity_id}", response_model=MessageResponse)
async def update_commodity(commodity_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE commodities SET commodity_name=%s, hs_code=%s, is_active=%s, updated_at=NOW() WHERE commodity_id=%s",
        (payload.get("commodity_name"), payload.get("hs_code"), payload.get("is_active", True), commodity_id)
    )
    return MessageResponse(message="Commodity updated")


@commodities_router.delete("/{commodity_id}", response_model=MessageResponse)
async def delete_commodity(commodity_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE commodities SET is_active=FALSE WHERE commodity_id=%s", (commodity_id,))
    return MessageResponse(message="Commodity deactivated")


# ========================
# Business Dimensions
# ========================
biz_dim_router = APIRouter(prefix="/business-dimensions")


@biz_dim_router.get("", response_model=PaginatedResponse)
async def list_biz_dims(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, dim_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(dim_code ILIKE %s OR dim_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if dim_type:
        conditions.append("dim_type = %s")
        params.append(dim_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM business_dimensions WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"SELECT * FROM business_dimensions WHERE {where} ORDER BY dim_name LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@biz_dim_router.get("/{dim_id}")
async def get_biz_dim(dim_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM business_dimensions WHERE dim_id = %s", (dim_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row


@biz_dim_router.post("", status_code=201)
async def create_biz_dim(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        "INSERT INTO business_dimensions (dim_code, dim_name, dim_type, is_active, created_by) VALUES (%s,%s,%s,%s,%s) RETURNING dim_id",
        (payload["dim_code"], payload["dim_name"], payload.get("dim_type"),
         payload.get("is_active", True), current_user.user_id)
    )
    return {"dim_id": row["dim_id"] if row else None, "message": "Created"}


@biz_dim_router.put("/{dim_id}", response_model=MessageResponse)
async def update_biz_dim(dim_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE business_dimensions SET dim_name=%s, dim_type=%s, is_active=%s WHERE dim_id=%s",
        (payload.get("dim_name"), payload.get("dim_type"), payload.get("is_active", True), dim_id)
    )
    return MessageResponse(message="Updated")


@biz_dim_router.delete("/{dim_id}", response_model=MessageResponse)
async def delete_biz_dim(dim_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE business_dimensions SET is_active=FALSE WHERE dim_id=%s", (dim_id,))
    return MessageResponse(message="Deactivated")


# ========================
# Vendor Contracts
# ========================
vendor_contracts_router = APIRouter(prefix="/vendor-contracts")


@vendor_contracts_router.get("", response_model=PaginatedResponse)
async def list_vendor_contracts(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(contract_no ILIKE %s)")
        params.append(f"%{search}%")
    if status:
        conditions.append("vc.status = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS cnt FROM vendor_contracts vc WHERE {where}",
                        tuple(params))["cnt"]
    rows = execute_query(
        f"""SELECT vc.*, o.org_name AS vendor_name FROM vendor_contracts vc
            LEFT JOIN organizations o ON vc.vendor_id = o.org_id
            WHERE {where} ORDER BY vc.created_at DESC LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@vendor_contracts_router.get("/{contract_id}")
async def get_vendor_contract(contract_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT vc.*, o.org_name AS vendor_name FROM vendor_contracts vc
           LEFT JOIN organizations o ON vc.vendor_id = o.org_id
           WHERE vc.contract_id = %s""",
        (contract_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contract not found")
    return row


@vendor_contracts_router.post("", status_code=201)
async def create_vendor_contract(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO vendor_contracts (contract_no, vendor_id, contract_type, transport_mode,
           start_date, end_date, currency, remarks, status, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING contract_id""",
        (payload["contract_no"], payload["vendor_id"], payload.get("contract_type"),
         payload.get("transport_mode"), payload.get("start_date"), payload.get("end_date"),
         payload.get("currency", "USD"), payload.get("remarks"), payload.get("status", "DRAFT"),
         current_user.user_id)
    )
    return {"contract_id": row["contract_id"] if row else None, "message": "Contract created"}


@vendor_contracts_router.put("/{contract_id}", response_model=MessageResponse)
async def update_vendor_contract(contract_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE vendor_contracts SET contract_type=%s, transport_mode=%s, start_date=%s,
           end_date=%s, status=%s, remarks=%s, updated_at=NOW() WHERE contract_id=%s""",
        (payload.get("contract_type"), payload.get("transport_mode"), payload.get("start_date"),
         payload.get("end_date"), payload.get("status"), payload.get("remarks"), contract_id)
    )
    return MessageResponse(message="Contract updated")


# ========================
# System Settings
# ========================
system_settings_router = APIRouter(prefix="/system-settings")


@system_settings_router.get("")
async def get_settings(
    group: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if group:
        conditions.append("setting_group = %s")
        params.append(group)
    rows = execute_query(
        f"SELECT * FROM system_settings WHERE {' AND '.join(conditions)} ORDER BY setting_group, setting_key",
        tuple(params)
    )
    return rows


@system_settings_router.put("/{setting_key}", response_model=MessageResponse)
async def update_setting(
    setting_key: str, payload: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    value = json.dumps(payload.get("value"))
    execute_write(
        "UPDATE system_settings SET setting_value=%s::jsonb, updated_by=%s, updated_at=NOW() WHERE setting_key=%s",
        (value, current_user.user_id, setting_key)
    )
    return MessageResponse(message="Setting updated")


# ========================
# Default Charges
# ========================
default_charges_router = APIRouter(prefix="/default-charges")


@default_charges_router.get("", response_model=PaginatedResponse)
async def list_default_charges(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    job_type: Optional[str] = None, transport_mode: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if job_type:
        conditions.append("dc.job_type = %s")
        params.append(job_type)
    if transport_mode:
        conditions.append("dc.transport_mode = %s")
        params.append(transport_mode)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(
        f"SELECT COUNT(*) AS cnt FROM default_charges dc WHERE {where}",
        tuple(params)
    )["cnt"]
    rows = execute_query(
        f"""SELECT dc.*, cm.charge_code, cm.charge_name
            FROM default_charges dc
            LEFT JOIN charge_master cm ON dc.charge_id = cm.charge_id
            WHERE {where} ORDER BY dc.default_id LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@default_charges_router.get("/{default_id}")
async def get_default_charge(default_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT dc.*, cm.charge_code, cm.charge_name
           FROM default_charges dc
           LEFT JOIN charge_master cm ON dc.charge_id = cm.charge_id
           WHERE dc.default_id = %s""",
        (default_id,)
    )
    if not row:
        raise HTTPException(status_code=404, detail="Default charge not found")
    return row


@default_charges_router.post("", status_code=201)
async def create_default_charge(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO default_charges (charge_id, job_type, transport_mode, amount, currency, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING default_id""",
        (payload["charge_id"], payload.get("job_type"), payload.get("transport_mode"),
         payload.get("amount", 0), payload.get("currency", "USD"),
         payload.get("is_active", True), current_user.user_id)
    )
    return {"default_id": row["default_id"] if row else None, "message": "Default charge created"}


@default_charges_router.put("/{default_id}", response_model=MessageResponse)
async def update_default_charge(default_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE default_charges SET charge_id=%s, job_type=%s, transport_mode=%s,
           amount=%s, currency=%s, is_active=%s, updated_at=NOW()
           WHERE default_id=%s""",
        (payload.get("charge_id"), payload.get("job_type"), payload.get("transport_mode"),
         payload.get("amount"), payload.get("currency", "USD"),
         payload.get("is_active", True), default_id)
    )
    return MessageResponse(message="Default charge updated")


@default_charges_router.delete("/{default_id}", response_model=MessageResponse)
async def delete_default_charge(default_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE default_charges SET is_active=FALSE WHERE default_id=%s", (default_id,))
    return MessageResponse(message="Default charge deactivated")


# ========================
# Custom Clearing Setup
# ========================
custom_clearing_router = APIRouter(prefix="/custom-clearing")


@custom_clearing_router.get("", response_model=PaginatedResponse)
async def list_custom_clearing(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None, clearing_type: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_active_user)
):
    conditions = ["1=1"]
    params = []
    if search:
        conditions.append("(port_code ILIKE %s OR port_name ILIKE %s OR customs_authority ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if clearing_type:
        conditions.append("clearing_type = %s")
        params.append(clearing_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(
        f"SELECT COUNT(*) AS cnt FROM custom_clearing_setup WHERE {where}",
        tuple(params)
    )["cnt"]
    rows = execute_query(
        f"SELECT * FROM custom_clearing_setup WHERE {where} ORDER BY clearing_type, port_code LIMIT %s OFFSET %s",
        tuple(params + [limit, offset])
    )
    return PaginatedResponse(data=rows, total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@custom_clearing_router.get("/{setup_id}")
async def get_custom_clearing(setup_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM custom_clearing_setup WHERE setup_id = %s", (setup_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Setup not found")
    return row


@custom_clearing_router.post("", status_code=201)
async def create_custom_clearing(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO custom_clearing_setup (clearing_type, port_code, port_name,
           customs_authority, broker_org_id, procedures, required_docs, is_active, created_by)
           VALUES (%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s) RETURNING setup_id""",
        (payload["clearing_type"], payload.get("port_code"), payload.get("port_name"),
         payload.get("customs_authority"), payload.get("broker_org_id"),
         json.dumps(payload.get("procedures", [])),
         json.dumps(payload.get("required_docs", [])),
         payload.get("is_active", True), current_user.user_id)
    )
    return {"setup_id": row["setup_id"] if row else None, "message": "Custom clearing setup created"}


@custom_clearing_router.put("/{setup_id}", response_model=MessageResponse)
async def update_custom_clearing(setup_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE custom_clearing_setup SET clearing_type=%s, port_code=%s, port_name=%s,
           customs_authority=%s, is_active=%s, updated_at=NOW()
           WHERE setup_id=%s""",
        (payload.get("clearing_type"), payload.get("port_code"), payload.get("port_name"),
         payload.get("customs_authority"), payload.get("is_active", True), setup_id)
    )
    return MessageResponse(message="Setup updated")


@custom_clearing_router.delete("/{setup_id}", response_model=MessageResponse)
async def delete_custom_clearing(setup_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE custom_clearing_setup SET is_active=FALSE WHERE setup_id=%s", (setup_id,))
    return MessageResponse(message="Setup deactivated")