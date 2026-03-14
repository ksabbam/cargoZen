"""Test: Exactly replicate what the native Snowflake Python connector does."""
import httpx
import uuid

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
c = httpx.Client(verify=False, timeout=30, follow_redirects=True)

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "PythonConnector", "CLIENT_APP_VERSION": "3.7.0", "CLIENT_ENVIRONMENT": {"APPLICATION": "PythonConnector", "OS": "Windows", "OS_VERSION": "10"}}}
params = {"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"}
r = c.post(f"{BASE}/session/v1/login-request", json=body, params=params, headers={"Content-Type": "application/json", "Accept": "application/json"})
d = r.json()
token = d["data"]["token"]
print(f"Token: {len(token)} chars")
print(f"masterToken: {len(d['data'].get('masterToken',''))} chars")
print(f"sessionId: {d['data'].get('sessionId', 'N/A')}")

# The connector sends queries to /queries/v1/query-request
# with specific parameters and headers
sql = "SELECT CURRENT_VERSION()"
request_id = str(uuid.uuid4())

# Replicate exact connector request
query_body = {
    "sqlText": sql,
    "asyncExec": False,
    "sequenceId": 1,
    "isInternal": False,
}

headers = {
    "Authorization": f'Snowflake Token="{token}"',
    "Content-Type": "application/json",
    "Accept": "application/snowflake",
    "User-Agent": "PythonConnector/3.7.0 (Windows; x86_64) Python/3.14",
}

query_params = {
    "requestId": request_id,
    "request_guid": str(uuid.uuid4()),
}

# Try the exact connector URL
url = f"{BASE}/queries/v1/query-request"
print(f"\nPOST {url}")
print(f"  Params: {query_params}")
print(f"  Headers: Authorization=Snowflake Token=\"...{token[-20:]}\"")
r2 = c.post(url, json=query_body, headers=headers, params=query_params)
print(f"  Status: {r2.status_code}")
ct = r2.headers.get("content-type", "")
print(f"  Content-Type: {ct}")

if "json" in ct or "snowflake" in ct:
    d2 = r2.json()
    print(f"  success: {d2.get('success')}")
    if d2.get("data") and isinstance(d2["data"], dict):
        if "rowtype" in d2["data"]:
            cols = [c["name"] for c in d2["data"]["rowtype"]]
            rows = d2["data"].get("rowset", [])
            print(f"  RESULT: {cols} = {rows}")
        else:
            print(f"  data keys: {list(d2['data'].keys())}")
    if d2.get("message"):
        print(f"  message: {d2['message'][:200]}")
    if d2.get("code"):
        print(f"  code: {d2['code']}")
else:
    print(f"  Body (first 300): {r2.text[:300]}")

# Also try with the "application/json" Accept header instead  
print(f"\nRetry with Accept: application/json...")
headers2 = dict(headers)
headers2["Accept"] = "application/json"
r3 = c.post(url, json=query_body, headers=headers2, params=query_params)
print(f"  Status: {r3.status_code}")
ct3 = r3.headers.get("content-type", "")
print(f"  Content-Type: {ct3}")
if ct3:
    try:
        d3 = r3.json()
        print(f"  success: {d3.get('success')}, code: {d3.get('code')}, msg: {d3.get('message','')[:100]}")
    except Exception:
        print(f"  Body: {r3.text[:200]}")
else:
    print(f"  Body: {r3.text[:200]}")
