"""Find the correct internal query endpoint."""
import httpx

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
client = httpx.Client(verify=False, timeout=30, follow_redirects=True, headers={"User-Agent": "CargoZen/1.0"})

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "CZ", "CLIENT_APP_VERSION": "1.0"}}
r = client.post(f"{BASE}/session/v1/login-request", json=body, params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
                headers={"Content-Type": "application/json", "Accept": "application/json"})
login = r.json()
token = login["data"]["token"]
master = login["data"].get("masterToken", "")
print(f"Token: {len(token)} chars, Master: {len(master)} chars")

sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U"

# Approach: POST to /queries/v1/query-request with Snowflake Token auth
# The old v1 API used by the native connector
endpoints_to_try = [
    ("/queries/v1/query-request", {"Authorization": f'Snowflake Token="{token}"', "Content-Type": "application/json", "Accept": "application/snowflake"}),
    ("/queries/v1/query-request", {"Authorization": f'Snowflake Token="{token}"', "Content-Type": "application/json", "Accept": "application/json"}),
    ("/session", {"Authorization": f'Snowflake Token="{token}"', "Content-Type": "application/json", "Accept": "application/json"}),
]

for ep, hdrs in endpoints_to_try:
    print(f"\n--- {ep} (Accept: {hdrs.get('Accept','?')}) ---")
    payload = {"sqlText": sql, "sequenceId": 0, "asyncExec": False}
    try:
        r2 = client.post(f"{BASE}{ep}", json=payload, headers=hdrs, params={"requestId": "test-123"})
        print(f"  Status: {r2.status_code}, CT: {r2.headers.get('content-type','?')}")
        if r2.status_code < 400 and ("json" in r2.headers.get("content-type", "") or "snowflake" in r2.headers.get("content-type", "")):
            d = r2.json()
            print(f"  success={d.get('success')}")
            if d.get("data", {}).get("rowtype"):
                cols = [c["name"] for c in d["data"]["rowtype"]]
                rows = d["data"].get("rowset", [])
                print(f"  RESULT: {cols} = {rows}")
            elif d.get("message"):
                print(f"  msg: {d['message'][:200]}")
        else:
            print(f"  Body: {r2.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Last resort: try using cookies from login response
print("\n\n--- Cookie-based approach ---")
# The login response sets cookies
login_resp = client.post(
    f"{BASE}/session/v1/login-request",
    json=body,
    params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
    headers={"Content-Type": "application/json", "Accept": "application/json"},
)
print(f"Login cookies: {dict(login_resp.cookies)}")
# Try query with cookies
r3 = client.post(
    f"{BASE}/queries/v1/query-request",
    json={"sqlText": sql, "sequenceId": 0, "asyncExec": False},
    headers={"Content-Type": "application/json", "Accept": "application/json"},
    params={"requestId": "test-456"},
    cookies=login_resp.cookies,
)
print(f"Status: {r3.status_code}, CT: {r3.headers.get('content-type')}")
if r3.status_code < 400:
    d3 = r3.json()
    print(f"success={d3.get('success')}")
    if d3.get("data", {}).get("rowtype"):
        cols = [c["name"] for c in d3["data"]["rowtype"]]
        rows = d3["data"].get("rowset", [])
        print(f"RESULT: {cols} = {rows}")
    if d3.get("message"):
        print(f"msg: {d3['message'][:200]}")
else:
    print(f"Body: {r3.text[:200]}")
