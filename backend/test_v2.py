"""Test v2 API with Bearer token."""
import httpx

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
client = httpx.Client(verify=False, timeout=30, follow_redirects=True)

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "CZ", "CLIENT_APP_VERSION": "1.0"}}
r = client.post(f"{BASE}/session/v1/login-request", json=body, params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
                headers={"Content-Type": "application/json", "Accept": "application/json"})
token = r.json()["data"]["token"]
print(f"Token: {len(token)} chars")

# Query with Bearer token (fresh client)
sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U, CURRENT_ROLE() AS R"
payload = {"statement": sql, "timeout": 60, "database": "CARGOZEN_DB", "schema": "AUTH", "warehouse": "CARGOZEN_WH", "role": "ACCOUNTADMIN"}
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
client2 = httpx.Client(verify=False, timeout=30)
r2 = client2.post(f"{BASE}/api/v2/statements", json=payload, headers=headers)
print(f"Status: {r2.status_code}")
d = r2.json()
if "resultSetMetaData" in d:
    cols = [c["name"] for c in d["resultSetMetaData"].get("rowType", [])]
    rows = d.get("data", [])
    print(f"Columns: {cols}")
    for row in rows:
        print(f"Row: {row}")
elif "message" in d:
    print(f"Message: {d['message'][:300]}")
    print(f"Code: {d.get('code')}")
else:
    print(f"Response: {d}")
