"""Test the /session endpoint for query execution - this is the internal API the web UI uses."""
import httpx
import json

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
c = httpx.Client(verify=False, timeout=30, follow_redirects=True)

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "CZ", "CLIENT_APP_VERSION": "1.0"}}
r = c.post(f"{BASE}/session/v1/login-request", json=body, params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
           headers={"Content-Type": "application/json", "Accept": "application/json"})
token = r.json()["data"]["token"]
print(f"Token OK ({len(token)} chars)")

# The Snowflake Worksheet/UI uses a POST to an internal endpoint
# Let's try the actual query path used by SnowSQL and connectors
sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U"

# Try /api/statements (without v2)
endpoints = [
    "/api/statements",
    "/api/v2/statements?requestId=test1",
]

auth_header = f'Snowflake Token="{token}"'

# The key insight: the native connector POSTs queries to a different URL
# Let's try posting SQL directly as the connector would
print("\n--- Testing query via session token ---")
query_body = {
    "sqlText": sql,
    "asyncExec": False,
    "sequenceId": 1,
    "isInternal": False,
}
query_headers = {
    "Authorization": auth_header,
    "Content-Type": "application/json",
    "Accept": "application/snowflake",
    "CLIENT_RESULT_CHUNK_SIZE": "48",
}

# The native Python connector uses this URL pattern:
# POST /queries/v1/query-request?requestId=<uuid>&request_guid=<uuid>
# But that returned 400. The connector might be using a different base URL.

# Actually - check if there's a /session/v1/query-request or similar
test_paths = [
    "/session/v1/query-request",
    "/api/v1/query-request",
    "/queries/v1/query-request",  
]

for path in test_paths:
    print(f"\n{path}...")
    try:
        r2 = c.post(f"{BASE}{path}", json=query_body, headers=query_headers, params={"requestId": "cz-test"})
        print(f"  Status: {r2.status_code}")
        ct = r2.headers.get("content-type", "")
        if "json" in ct or "snowflake" in ct:
            d = r2.json()
            print(f"  success={d.get('success')}")
            if d.get("data") and isinstance(d["data"], dict):
                if "rowtype" in d["data"]:
                    cols = [col["name"] for col in d["data"]["rowtype"]]
                    rows = d["data"].get("rowset", [])
                    print(f"  *** QUERY RESULT: {cols} = {rows} ***")
                else:
                    print(f"  data keys: {list(d['data'].keys())[:10]}")
            if d.get("message"):
                print(f"  msg: {d['message'][:150]}")
            if d.get("code"):
                print(f"  code: {d['code']}")
        else:
            print(f"  CT: {ct}")
            print(f"  Body: {r2.text[:150]}")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone.")
