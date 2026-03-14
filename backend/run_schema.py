"""Execute schema and seed SQL files against Snowflake."""
import httpx
import uuid
import os

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
c = httpx.Client(verify=False, timeout=60, follow_redirects=True, headers={"User-Agent": "PythonConnector/3.7.0"})

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "PythonConnector", "CLIENT_APP_VERSION": "3.7.0"}}
r = c.post(f"{BASE}/session/v1/login-request", json=body, params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
           headers={"Content-Type": "application/json", "Accept": "application/json"})
token = r.json()["data"]["token"]
print("Logged in OK")

seq = [0]

def run_sql(sql):
    sql = sql.strip()
    if not sql or sql.startswith("--"):
        return True
    seq[0] += 1
    r2 = c.post(
        f"{BASE}/queries/v1/query-request",
        params={"requestId": str(uuid.uuid4()), "request_guid": str(uuid.uuid4())},
        json={"sqlText": sql, "asyncExec": False, "sequenceId": seq[0], "isInternal": False},
        headers={"Authorization": f'Snowflake Token="{token}"', "Content-Type": "application/json", "Accept": "application/json"},
    )
    d = r2.json()
    ok = d.get("success", False)
    label = sql[:70].replace("\n", " ")
    if ok:
        print(f"  OK: {label}")
    else:
        msg = d.get("message", "")[:120]
        print(f"  FAIL: {label}")
        print(f"        {msg}")
    return ok

def run_file(path):
    print(f"\nExecuting {os.path.basename(path)}...")
    with open(path, "r") as f:
        content = f.read()
    
    # Split on semicolons, but handle multi-line statements
    statements = []
    current = []
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip().rstrip(";")
            if stmt:
                statements.append(stmt)
            current = []
    if current:
        stmt = "\n".join(current).strip().rstrip(";")
        if stmt:
            statements.append(stmt)
    
    ok_count = 0
    fail_count = 0
    for stmt in statements:
        if run_sql(stmt):
            ok_count += 1
        else:
            fail_count += 1
    print(f"  Summary: {ok_count} OK, {fail_count} failed")

db_dir = os.path.join(os.path.dirname(__file__), "..", "database")
run_file(os.path.join(db_dir, "01_schema.sql"))
run_file(os.path.join(db_dir, "02_seed_data.sql"))

print("\n=== ALL DONE ===")

# Verify
print("\nVerification:")
run_sql("SELECT COUNT(*) AS cnt FROM CARGOZEN_DB.AUTH.USERS")
run_sql("SELECT USERNAME, FULL_NAME, ROLE_ID FROM CARGOZEN_DB.AUTH.USERS")
