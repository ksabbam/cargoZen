"""Test Snowflake query after authentication."""
import httpx
import time
import secrets

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"

# Step 1: Login
print("Logging in...")
body = {
    "data": {
        "ACCOUNT_NAME": "FCJPXYK-ZH80005",
        "LOGIN_NAME": "SUSANI",
        "PASSWORD": "LetItSnow123!!",
        "CLIENT_APP_ID": "CargoZen",
        "CLIENT_APP_VERSION": "1.0",
    }
}
params = {"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"}
client = httpx.Client(verify=False, timeout=30, follow_redirects=True)
r = client.post(f"{BASE}/session/v1/login-request", json=body, params=params,
                headers={"Content-Type": "application/json", "Accept": "application/json"})
data = r.json()
token = data["data"]["token"]
print(f"Login OK, token={len(token)} chars")

# Step 2: Try different query endpoints
sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U, CURRENT_ROLE() AS R"

endpoints = [
    "/queries/v1/query-request",
    "/api/v2/statements",
]

for ep in endpoints:
    print(f"\nTesting {ep}...")
    
    if "v2/statements" in ep:
        payload = {
            "statement": sql,
            "timeout": 60,
            "database": "CARGOZEN_DB",
            "schema": "AUTH",
            "warehouse": "CARGOZEN_WH",
            "role": "ACCOUNTADMIN",
        }
        headers = {
            "Authorization": f'Snowflake Token="{token}"',
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Snowflake-Authorization-Token-Type": "",
        }
        try:
            r2 = client.post(f"{BASE}{ep}", json=payload, headers=headers)
            print(f"  Status: {r2.status_code}")
            if r2.headers.get("content-type", "").startswith("application/json"):
                d = r2.json()
                print(f"  Success: {d.get('success', 'N/A')}")
                if d.get("data"):
                    print(f"  Data keys: {list(d['data'].keys()) if isinstance(d['data'], dict) else 'list'}")
                    if isinstance(d.get("data"), list):
                        print(f"  First row: {d['data'][0] if d['data'] else 'empty'}")
                if d.get("message"):
                    print(f"  Message: {d['message'][:200]}")
            else:
                print(f"  Content-Type: {r2.headers.get('content-type')}")
                print(f"  Body: {r2.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        payload = {
            "sqlText": sql,
            "sequenceId": 0,
            "asyncExec": False,
        }
        headers = {
            "Authorization": f'Snowflake Token="{token}"',
            "Content-Type": "application/json",
            "Accept": "application/snowflake",
        }
        req_id = f"cz-{int(time.time()*1000)}-{secrets.token_hex(4)}"
        try:
            r2 = client.post(f"{BASE}{ep}", json=payload, params={"requestId": req_id}, headers=headers)
            print(f"  Status: {r2.status_code}")
            ct = r2.headers.get("content-type", "")
            print(f"  Content-Type: {ct}")
            if "json" in ct or "snowflake" in ct:
                d = r2.json()
                print(f"  Success: {d.get('success')}")
                if d.get("data"):
                    rd = d["data"]
                    if "rowtype" in rd:
                        cols = [c["name"] for c in rd["rowtype"]]
                        rows = rd.get("rowset", [])
                        print(f"  Cols: {cols}")
                        print(f"  Rows: {rows[:3]}")
                if d.get("message"):
                    print(f"  Message: {d['message'][:200]}")
            else:
                print(f"  Body: {r2.text[:300]}")
        except Exception as e:
            print(f"  Error: {e}")

print("\nDone")
