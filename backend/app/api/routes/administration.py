from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.api.deps import get_current_active_user
from app.core.database import execute_query, execute_one, execute_write
from app.models.schemas import PaginatedResponse, MessageResponse, UserResponse
import math

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
        conditions.append("(GROUP_CODE ILIKE %s OR GROUP_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.ORGANIZATION_GROUPS WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.ORGANIZATION_GROUPS WHERE {where} ORDER BY GROUP_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@org_groups_router.get("/{group_id}")
async def get_org_group(group_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.ORGANIZATION_GROUPS WHERE GROUP_ID = %s",
                      (group_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Group not found")
    return {k.lower(): v for k, v in row.items()}


@org_groups_router.post("", status_code=201)
async def create_org_group(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.ORGANIZATION_GROUPS (GROUP_CODE, GROUP_NAME, GROUP_TYPE, DESCRIPTION, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s) RETURNING GROUP_ID""",
        (payload["group_code"], payload["group_name"], payload.get("group_type"),
         payload.get("description"), payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"group_id": row["GROUP_ID"] if row else None, "message": "Group created"}


@org_groups_router.put("/{group_id}", response_model=MessageResponse)
async def update_org_group(group_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE ADMIN.ORGANIZATION_GROUPS SET GROUP_NAME=%s, GROUP_TYPE=%s, DESCRIPTION=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE GROUP_ID=%s",
        (payload.get("group_name"), payload.get("group_type"), payload.get("description"),
         payload.get("is_active", True), group_id), schema="ADMIN"
    )
    return MessageResponse(message="Group updated")


@org_groups_router.delete("/{group_id}", response_model=MessageResponse)
async def delete_org_group(group_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.ORGANIZATION_GROUPS SET IS_ACTIVE=FALSE WHERE GROUP_ID=%s",
                  (group_id,), schema="ADMIN")
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
        conditions.append("(AIRLINE_CODE ILIKE %s OR AIRLINE_NAME ILIKE %s OR IATA_CODE ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.AIRLINES WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.AIRLINES WHERE {where} ORDER BY AIRLINE_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@airlines_router.get("/search-select", response_model=List[dict])
async def search_airlines(q: Optional[str] = None, current_user: UserResponse = Depends(get_current_active_user)):
    params = []
    conditions = ["IS_ACTIVE = TRUE"]
    if q:
        conditions.append("(AIRLINE_CODE ILIKE %s OR AIRLINE_NAME ILIKE %s OR IATA_CODE ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    rows = execute_query(
        f"SELECT AIRLINE_ID AS id, AIRLINE_CODE AS code, AIRLINE_NAME AS name, IATA_CODE AS iata_code "
        f"FROM ADMIN.AIRLINES WHERE {' AND '.join(conditions)} LIMIT 50",
        tuple(params), schema="ADMIN"
    )
    return [{k.lower(): v for k, v in r.items()} for r in rows]


@airlines_router.get("/{airline_id}")
async def get_airline(airline_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.AIRLINES WHERE AIRLINE_ID = %s", (airline_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Airline not found")
    return {k.lower(): v for k, v in row.items()}


@airlines_router.post("", status_code=201)
async def create_airline(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.AIRLINES (AIRLINE_CODE, IATA_CODE, ICAO_CODE, AIRLINE_NAME, COUNTRY,
           HEADQUARTERS, PHONE, EMAIL, ALLIANCE, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING AIRLINE_ID""",
        (payload["airline_code"], payload.get("iata_code"), payload.get("icao_code"),
         payload["airline_name"], payload.get("country"), payload.get("headquarters"),
         payload.get("phone"), payload.get("email"), payload.get("alliance"),
         payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"airline_id": row["AIRLINE_ID"] if row else None, "message": "Airline created"}


@airlines_router.put("/{airline_id}", response_model=MessageResponse)
async def update_airline(airline_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.AIRLINES SET AIRLINE_CODE=%s, IATA_CODE=%s, AIRLINE_NAME=%s, COUNTRY=%s,
           IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE AIRLINE_ID=%s""",
        (payload.get("airline_code"), payload.get("iata_code"), payload.get("airline_name"),
         payload.get("country"), payload.get("is_active", True), airline_id), schema="ADMIN"
    )
    return MessageResponse(message="Airline updated")


@airlines_router.delete("/{airline_id}", response_model=MessageResponse)
async def delete_airline(airline_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.AIRLINES SET IS_ACTIVE=FALSE WHERE AIRLINE_ID=%s",
                  (airline_id,), schema="ADMIN")
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
        conditions.append("(LINE_CODE ILIKE %s OR LINE_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.SHIPPING_LINES WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.SHIPPING_LINES WHERE {where} ORDER BY LINE_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@shipping_lines_router.get("/{line_id}")
async def get_shipping_line(line_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.SHIPPING_LINES WHERE LINE_ID = %s", (line_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Shipping line not found")
    return {k.lower(): v for k, v in row.items()}


@shipping_lines_router.post("", status_code=201)
async def create_shipping_line(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.SHIPPING_LINES (LINE_CODE, SCAC_CODE, LINE_NAME, COUNTRY,
           HEADQUARTERS, PHONE, EMAIL, WEBSITE, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING LINE_ID""",
        (payload["line_code"], payload.get("scac_code"), payload["line_name"],
         payload.get("country"), payload.get("headquarters"), payload.get("phone"),
         payload.get("email"), payload.get("website"), payload.get("is_active", True),
         current_user.user_id),
        schema="ADMIN"
    )
    return {"line_id": row["LINE_ID"] if row else None, "message": "Shipping line created"}


@shipping_lines_router.put("/{line_id}", response_model=MessageResponse)
async def update_shipping_line(line_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE ADMIN.SHIPPING_LINES SET LINE_NAME=%s, COUNTRY=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE LINE_ID=%s",
        (payload.get("line_name"), payload.get("country"), payload.get("is_active", True), line_id),
        schema="ADMIN"
    )
    return MessageResponse(message="Shipping line updated")


@shipping_lines_router.delete("/{line_id}", response_model=MessageResponse)
async def delete_shipping_line(line_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.SHIPPING_LINES SET IS_ACTIVE=FALSE WHERE LINE_ID=%s",
                  (line_id,), schema="ADMIN")
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
        conditions.append("(CHARGE_CODE ILIKE %s OR CHARGE_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if charge_type:
        conditions.append("CHARGE_TYPE = %s")
        params.append(charge_type)
    if applicable_for:
        conditions.append("(APPLICABLE_FOR = %s OR APPLICABLE_FOR = 'BOTH')")
        params.append(applicable_for)
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.CHARGE_MASTER WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.CHARGE_MASTER WHERE {where} ORDER BY CHARGE_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@charge_master_router.get("/{charge_id}")
async def get_charge(charge_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.CHARGE_MASTER WHERE CHARGE_ID = %s", (charge_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Charge not found")
    return {k.lower(): v for k, v in row.items()}


@charge_master_router.post("", status_code=201)
async def create_charge(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.CHARGE_MASTER (CHARGE_CODE, CHARGE_NAME, CHARGE_TYPE, CHARGE_CATEGORY,
           APPLICABLE_FOR, GL_ACCOUNT_ID, IS_TAXABLE, UNIT_TYPE, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING CHARGE_ID""",
        (payload["charge_code"], payload["charge_name"], payload.get("charge_type"),
         payload.get("charge_category"), payload.get("applicable_for"),
         payload.get("gl_account_id"), payload.get("is_taxable", False),
         payload.get("unit_type"), payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"charge_id": row["CHARGE_ID"] if row else None, "message": "Charge created"}


@charge_master_router.put("/{charge_id}", response_model=MessageResponse)
async def update_charge(charge_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.CHARGE_MASTER SET CHARGE_NAME=%s, CHARGE_TYPE=%s, CHARGE_CATEGORY=%s,
           APPLICABLE_FOR=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE CHARGE_ID=%s""",
        (payload.get("charge_name"), payload.get("charge_type"), payload.get("charge_category"),
         payload.get("applicable_for"), payload.get("is_active", True), charge_id), schema="ADMIN"
    )
    return MessageResponse(message="Charge updated")


@charge_master_router.delete("/{charge_id}", response_model=MessageResponse)
async def delete_charge(charge_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.CHARGE_MASTER SET IS_ACTIVE=FALSE WHERE CHARGE_ID=%s",
                  (charge_id,), schema="ADMIN")
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
        conditions.append("(ACCOUNT_CODE ILIKE %s OR ACCOUNT_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if account_type:
        conditions.append("ACCOUNT_TYPE = %s")
        params.append(account_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.ACCOUNTS WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.ACCOUNTS WHERE {where} ORDER BY ACCOUNT_CODE LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@accounts_router.get("/{account_id}")
async def get_account(account_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.ACCOUNTS WHERE ACCOUNT_ID = %s", (account_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Account not found")
    return {k.lower(): v for k, v in row.items()}


@accounts_router.post("", status_code=201)
async def create_account(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.ACCOUNTS (ACCOUNT_CODE, ACCOUNT_NAME, ACCOUNT_TYPE, ACCOUNT_SUBTYPE,
           PARENT_ACCOUNT_ID, DESCRIPTION, OPENING_BALANCE, CURRENCY, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING ACCOUNT_ID""",
        (payload["account_code"], payload["account_name"], payload["account_type"],
         payload.get("account_subtype"), payload.get("parent_account_id"),
         payload.get("description"), payload.get("opening_balance", 0),
         payload.get("currency", "USD"), payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"account_id": row["ACCOUNT_ID"] if row else None, "message": "Account created"}


@accounts_router.put("/{account_id}", response_model=MessageResponse)
async def update_account(account_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.ACCOUNTS SET ACCOUNT_NAME=%s, ACCOUNT_TYPE=%s, ACCOUNT_SUBTYPE=%s,
           IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE ACCOUNT_ID=%s""",
        (payload.get("account_name"), payload.get("account_type"), payload.get("account_subtype"),
         payload.get("is_active", True), account_id), schema="ADMIN"
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
        conditions.append("(COMMODITY_CODE ILIKE %s OR COMMODITY_NAME ILIKE %s OR HS_CODE ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if is_active is not None:
        conditions.append("IS_ACTIVE = %s")
        params.append(is_active)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.COMMODITIES WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.COMMODITIES WHERE {where} ORDER BY COMMODITY_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@commodities_router.get("/{commodity_id}")
async def get_commodity(commodity_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.COMMODITIES WHERE COMMODITY_ID = %s", (commodity_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Commodity not found")
    return {k.lower(): v for k, v in row.items()}


@commodities_router.post("", status_code=201)
async def create_commodity(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.COMMODITIES (COMMODITY_CODE, COMMODITY_NAME, HS_CODE, COMMODITY_GROUP,
           IS_DANGEROUS, DANGEROUS_CLASS, UN_NUMBER, DESCRIPTION, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING COMMODITY_ID""",
        (payload["commodity_code"], payload["commodity_name"], payload.get("hs_code"),
         payload.get("commodity_group"), payload.get("is_dangerous", False),
         payload.get("dangerous_class"), payload.get("un_number"), payload.get("description"),
         payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"commodity_id": row["COMMODITY_ID"] if row else None, "message": "Commodity created"}


@commodities_router.put("/{commodity_id}", response_model=MessageResponse)
async def update_commodity(commodity_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE ADMIN.COMMODITIES SET COMMODITY_NAME=%s, HS_CODE=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE COMMODITY_ID=%s",
        (payload.get("commodity_name"), payload.get("hs_code"), payload.get("is_active", True), commodity_id),
        schema="ADMIN"
    )
    return MessageResponse(message="Commodity updated")


@commodities_router.delete("/{commodity_id}", response_model=MessageResponse)
async def delete_commodity(commodity_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.COMMODITIES SET IS_ACTIVE=FALSE WHERE COMMODITY_ID=%s",
                  (commodity_id,), schema="ADMIN")
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
        conditions.append("(DIM_CODE ILIKE %s OR DIM_NAME ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    if dim_type:
        conditions.append("DIM_TYPE = %s")
        params.append(dim_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.BUSINESS_DIMENSIONS WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.BUSINESS_DIMENSIONS WHERE {where} ORDER BY DIM_NAME LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@biz_dim_router.get("/{dim_id}")
async def get_biz_dim(dim_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.BUSINESS_DIMENSIONS WHERE DIM_ID = %s", (dim_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return {k.lower(): v for k, v in row.items()}


@biz_dim_router.post("", status_code=201)
async def create_biz_dim(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        "INSERT INTO ADMIN.BUSINESS_DIMENSIONS (DIM_CODE, DIM_NAME, DIM_TYPE, IS_ACTIVE, CREATED_BY) VALUES (%s,%s,%s,%s,%s) RETURNING DIM_ID",
        (payload["dim_code"], payload["dim_name"], payload.get("dim_type"),
         payload.get("is_active", True), current_user.user_id), schema="ADMIN"
    )
    return {"dim_id": row["DIM_ID"] if row else None, "message": "Created"}


@biz_dim_router.put("/{dim_id}", response_model=MessageResponse)
async def update_biz_dim(dim_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        "UPDATE ADMIN.BUSINESS_DIMENSIONS SET DIM_NAME=%s, DIM_TYPE=%s, IS_ACTIVE=%s WHERE DIM_ID=%s",
        (payload.get("dim_name"), payload.get("dim_type"), payload.get("is_active", True), dim_id), schema="ADMIN"
    )
    return MessageResponse(message="Updated")


@biz_dim_router.delete("/{dim_id}", response_model=MessageResponse)
async def delete_biz_dim(dim_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.BUSINESS_DIMENSIONS SET IS_ACTIVE=FALSE WHERE DIM_ID=%s",
                  (dim_id,), schema="ADMIN")
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
        conditions.append("(CONTRACT_NO ILIKE %s)")
        params.append(f"%{search}%")
    if status:
        conditions.append("STATUS = %s")
        params.append(status)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(f"SELECT COUNT(*) AS CNT FROM ADMIN.VENDOR_CONTRACTS WHERE {where}",
                        tuple(params), schema="ADMIN")["CNT"]
    rows = execute_query(
        f"""SELECT vc.*, o.ORG_NAME AS vendor_name FROM ADMIN.VENDOR_CONTRACTS vc
            LEFT JOIN ADMIN.ORGANIZATIONS o ON vc.VENDOR_ID = o.ORG_ID
            WHERE {where} ORDER BY CREATED_AT DESC LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(data=[{k.lower(): v for k, v in r.items()} for r in rows],
                             total=total, page=page, limit=limit,
                             total_pages=math.ceil(total / limit) if total > 0 else 1)


@vendor_contracts_router.get("/{contract_id}")
async def get_vendor_contract(contract_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT vc.*, o.ORG_NAME AS vendor_name FROM ADMIN.VENDOR_CONTRACTS vc
           LEFT JOIN ADMIN.ORGANIZATIONS o ON vc.VENDOR_ID = o.ORG_ID
           WHERE vc.CONTRACT_ID = %s""",
        (contract_id,), schema="ADMIN"
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {k.lower(): v for k, v in row.items()}


@vendor_contracts_router.post("", status_code=201)
async def create_vendor_contract(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.VENDOR_CONTRACTS (CONTRACT_NO, VENDOR_ID, CONTRACT_TYPE, TRANSPORT_MODE,
           START_DATE, END_DATE, CURRENCY, REMARKS, STATUS, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING CONTRACT_ID""",
        (payload["contract_no"], payload["vendor_id"], payload.get("contract_type"),
         payload.get("transport_mode"), payload.get("start_date"), payload.get("end_date"),
         payload.get("currency", "USD"), payload.get("remarks"), payload.get("status", "DRAFT"),
         current_user.user_id),
        schema="ADMIN"
    )
    return {"contract_id": row["CONTRACT_ID"] if row else None, "message": "Contract created"}


@vendor_contracts_router.put("/{contract_id}", response_model=MessageResponse)
async def update_vendor_contract(contract_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.VENDOR_CONTRACTS SET CONTRACT_TYPE=%s, TRANSPORT_MODE=%s, START_DATE=%s,
           END_DATE=%s, STATUS=%s, REMARKS=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE CONTRACT_ID=%s""",
        (payload.get("contract_type"), payload.get("transport_mode"), payload.get("start_date"),
         payload.get("end_date"), payload.get("status"), payload.get("remarks"), contract_id),
        schema="ADMIN"
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
        conditions.append("SETTING_GROUP = %s")
        params.append(group)
    rows = execute_query(
        f"SELECT * FROM ADMIN.SYSTEM_SETTINGS WHERE {' AND '.join(conditions)} ORDER BY SETTING_GROUP, SETTING_KEY",
        tuple(params), schema="ADMIN"
    )
    return [{k.lower(): v for k, v in r.items()} for r in rows]


@system_settings_router.put("/{setting_key}", response_model=MessageResponse)
async def update_setting(
    setting_key: str, payload: dict,
    current_user: UserResponse = Depends(get_current_active_user)
):
    import json
    value = json.dumps(payload.get("value"))
    execute_write(
        "UPDATE ADMIN.SYSTEM_SETTINGS SET SETTING_VALUE=PARSE_JSON(%s), UPDATED_BY=%s, UPDATED_AT=CURRENT_TIMESTAMP() WHERE SETTING_KEY=%s",
        (value, current_user.user_id, setting_key), schema="ADMIN"
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
        conditions.append("dc.JOB_TYPE = %s")
        params.append(job_type)
    if transport_mode:
        conditions.append("dc.TRANSPORT_MODE = %s")
        params.append(transport_mode)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(
        f"SELECT COUNT(*) AS CNT FROM ADMIN.DEFAULT_CHARGES dc WHERE {where}",
        tuple(params), schema="ADMIN"
    )["CNT"]
    rows = execute_query(
        f"""SELECT dc.*, cm.CHARGE_CODE, cm.CHARGE_NAME
            FROM ADMIN.DEFAULT_CHARGES dc
            LEFT JOIN ADMIN.CHARGE_MASTER cm ON dc.CHARGE_ID = cm.CHARGE_ID
            WHERE {where} ORDER BY dc.DEFAULT_ID LIMIT %s OFFSET %s""",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(
        data=[{k.lower(): v for k, v in r.items()} for r in rows],
        total=total, page=page, limit=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 1
    )


@default_charges_router.get("/{default_id}")
async def get_default_charge(default_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """SELECT dc.*, cm.CHARGE_CODE, cm.CHARGE_NAME
           FROM ADMIN.DEFAULT_CHARGES dc
           LEFT JOIN ADMIN.CHARGE_MASTER cm ON dc.CHARGE_ID = cm.CHARGE_ID
           WHERE dc.DEFAULT_ID = %s""",
        (default_id,), schema="ADMIN"
    )
    if not row:
        raise HTTPException(status_code=404, detail="Default charge not found")
    return {k.lower(): v for k, v in row.items()}


@default_charges_router.post("", status_code=201)
async def create_default_charge(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one(
        """INSERT INTO ADMIN.DEFAULT_CHARGES (CHARGE_ID, JOB_TYPE, TRANSPORT_MODE, AMOUNT, CURRENCY, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING DEFAULT_ID""",
        (payload["charge_id"], payload.get("job_type"), payload.get("transport_mode"),
         payload.get("amount", 0), payload.get("currency", "USD"),
         payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"default_id": row["DEFAULT_ID"] if row else None, "message": "Default charge created"}


@default_charges_router.put("/{default_id}", response_model=MessageResponse)
async def update_default_charge(default_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.DEFAULT_CHARGES SET CHARGE_ID=%s, JOB_TYPE=%s, TRANSPORT_MODE=%s,
           AMOUNT=%s, CURRENCY=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP()
           WHERE DEFAULT_ID=%s""",
        (payload.get("charge_id"), payload.get("job_type"), payload.get("transport_mode"),
         payload.get("amount"), payload.get("currency", "USD"),
         payload.get("is_active", True), default_id),
        schema="ADMIN"
    )
    return MessageResponse(message="Default charge updated")


@default_charges_router.delete("/{default_id}", response_model=MessageResponse)
async def delete_default_charge(default_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.DEFAULT_CHARGES SET IS_ACTIVE=FALSE WHERE DEFAULT_ID=%s",
                  (default_id,), schema="ADMIN")
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
        conditions.append("(PORT_CODE ILIKE %s OR PORT_NAME ILIKE %s OR CUSTOMS_AUTHORITY ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if clearing_type:
        conditions.append("CLEARING_TYPE = %s")
        params.append(clearing_type)
    where = " AND ".join(conditions)
    offset = (page - 1) * limit
    total = execute_one(
        f"SELECT COUNT(*) AS CNT FROM ADMIN.CUSTOM_CLEARING_SETUP WHERE {where}",
        tuple(params), schema="ADMIN"
    )["CNT"]
    rows = execute_query(
        f"SELECT * FROM ADMIN.CUSTOM_CLEARING_SETUP WHERE {where} ORDER BY CLEARING_TYPE, PORT_CODE LIMIT %s OFFSET %s",
        tuple(params + [limit, offset]), schema="ADMIN"
    )
    return PaginatedResponse(
        data=[{k.lower(): v for k, v in r.items()} for r in rows],
        total=total, page=page, limit=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 1
    )


@custom_clearing_router.get("/{setup_id}")
async def get_custom_clearing(setup_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    row = execute_one("SELECT * FROM ADMIN.CUSTOM_CLEARING_SETUP WHERE SETUP_ID = %s",
                      (setup_id,), schema="ADMIN")
    if not row:
        raise HTTPException(status_code=404, detail="Setup not found")
    return {k.lower(): v for k, v in row.items()}


@custom_clearing_router.post("", status_code=201)
async def create_custom_clearing(payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    import json
    row = execute_one(
        """INSERT INTO ADMIN.CUSTOM_CLEARING_SETUP (CLEARING_TYPE, PORT_CODE, PORT_NAME,
           CUSTOMS_AUTHORITY, BROKER_ORG_ID, PROCEDURES, REQUIRED_DOCS, IS_ACTIVE, CREATED_BY)
           VALUES (%s,%s,%s,%s,%s,PARSE_JSON(%s),PARSE_JSON(%s),%s,%s) RETURNING SETUP_ID""",
        (payload["clearing_type"], payload.get("port_code"), payload.get("port_name"),
         payload.get("customs_authority"), payload.get("broker_org_id"),
         json.dumps(payload.get("procedures", [])),
         json.dumps(payload.get("required_docs", [])),
         payload.get("is_active", True), current_user.user_id),
        schema="ADMIN"
    )
    return {"setup_id": row["SETUP_ID"] if row else None, "message": "Custom clearing setup created"}


@custom_clearing_router.put("/{setup_id}", response_model=MessageResponse)
async def update_custom_clearing(setup_id: int, payload: dict, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write(
        """UPDATE ADMIN.CUSTOM_CLEARING_SETUP SET CLEARING_TYPE=%s, PORT_CODE=%s, PORT_NAME=%s,
           CUSTOMS_AUTHORITY=%s, IS_ACTIVE=%s, UPDATED_AT=CURRENT_TIMESTAMP()
           WHERE SETUP_ID=%s""",
        (payload.get("clearing_type"), payload.get("port_code"), payload.get("port_name"),
         payload.get("customs_authority"), payload.get("is_active", True), setup_id),
        schema="ADMIN"
    )
    return MessageResponse(message="Setup updated")


@custom_clearing_router.delete("/{setup_id}", response_model=MessageResponse)
async def delete_custom_clearing(setup_id: int, current_user: UserResponse = Depends(get_current_active_user)):
    execute_write("UPDATE ADMIN.CUSTOM_CLEARING_SETUP SET IS_ACTIVE=FALSE WHERE SETUP_ID=%s",
                  (setup_id,), schema="ADMIN")
    return MessageResponse(message="Setup deactivated")
