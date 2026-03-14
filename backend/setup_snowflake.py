"""Create the warehouse, database, and schema if needed."""
import httpx
import uuid

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
c = httpx.Client(verify=False, timeout=30, follow_redirects=True, headers={"User-Agent": "PythonConnector/3.7.0"})

# Login WITHOUT warehouse param (since it doesn't exist yet)
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "PythonConnector", "CLIENT_APP_VERSION": "3.7.0"}}
r = c.post(f"{BASE}/session/v1/login-request", json=body, params={"roleName": "ACCOUNTADMIN"},
           headers={"Content-Type": "application/json", "Accept": "application/json"})
d = r.json()
if not d.get("success"):
    print(f"Login failed: {d.get('message')}")
    exit(1)
token = d["data"]["token"]
print(f"Logged in OK")

def run_sql(sql):
    r2 = c.post(
        f"{BASE}/queries/v1/query-request",
        params={"requestId": str(uuid.uuid4()), "request_guid": str(uuid.uuid4())},
        json={"sqlText": sql, "asyncExec": False, "sequenceId": 1, "isInternal": False},
        headers={"Authorization": f'Snowflake Token="{token}"', "Content-Type": "application/json", "Accept": "application/json"},
    )
    d2 = r2.json()
    ok = d2.get("success", False)
    msg = d2.get("message", "")
    print(f"  {'OK' if ok else 'FAIL'}: {sql[:60]}{'...' if len(sql)>60 else ''}")
    if not ok and msg:
        print(f"       {msg[:150]}")
    return ok

# Setup infrastructure
print("\nCreating warehouse...")
run_sql("CREATE WAREHOUSE IF NOT EXISTS CARGOZEN_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE")
run_sql("USE WAREHOUSE CARGOZEN_WH")

print("\nCreating database & schemas...")
run_sql("CREATE DATABASE IF NOT EXISTS CARGOZEN_DB")
run_sql("USE DATABASE CARGOZEN_DB")
run_sql("CREATE SCHEMA IF NOT EXISTS AUTH")
run_sql("CREATE SCHEMA IF NOT EXISTS ADMIN")
run_sql("CREATE SCHEMA IF NOT EXISTS TXN")

print("\nVerifying...")
run_sql("SELECT CURRENT_WAREHOUSE() AS WH, CURRENT_DATABASE() AS DB, CURRENT_ROLE() AS ROLE")

print("\nDone! Now run the schema SQL (01_schema.sql) and seed (02_seed_data.sql) in Snowflake Worksheet.")
