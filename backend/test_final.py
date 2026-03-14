"""Final test: correct Snowflake SQL API v2 format."""
import httpx

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
BASE = f"https://{HOST}"
c = httpx.Client(verify=False, timeout=30)

# Login
body = {"data": {"ACCOUNT_NAME": "FCJPXYK-ZH80005", "LOGIN_NAME": "SUSANI", "PASSWORD": "LetItSnow123!!", "CLIENT_APP_ID": "CZ", "CLIENT_APP_VERSION": "1.0"}}
r = c.post(f"{BASE}/session/v1/login-request", json=body, params={"warehouse": "CARGOZEN_WH", "databaseName": "CARGOZEN_DB", "roleName": "ACCOUNTADMIN"},
           headers={"Content-Type": "application/json", "Accept": "application/json"})
token = r.json()["data"]["token"]
master = r.json()["data"].get("masterToken", "")
print(f"Session token: {len(token)} chars")

sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U"
payload = {"statement": sql, "timeout": 60, "database": "CARGOZEN_DB", "schema": "AUTH", "warehouse": "CARGOZEN_WH", "role": "ACCOUNTADMIN"}

combos = [
    ("Snowflake Token=\"{t}\"", "SNOWFLAKE"),
    ("Snowflake Token=\"{t}\"", None),
    ("Bearer {t}", "SNOWFLAKE"),
    ("Bearer {t}", None),
    ("Snowflake Token=\"{m}\"", "SNOWFLAKE"),
    ("Snowflake Token=\"{m}\"", None),
]

for auth_fmt, token_type in combos:
    t = token if "{t}" in auth_fmt else master
    auth_val = auth_fmt.replace("{t}", token).replace("{m}", master)
    hdrs = {"Authorization": auth_val, "Content-Type": "application/json", "Accept": "application/json"}
    if token_type:
        hdrs["X-Snowflake-Authorization-Token-Type"] = token_type
    label = f'Auth="{auth_fmt[:30]}..." Type={token_type}'
    try:
        r2 = httpx.post(f"{BASE}/api/v2/statements", json=payload, headers=hdrs, verify=False, timeout=15)
        d = r2.json()
        status = r2.status_code
        success = d.get("statementStatusUrl") or d.get("resultSetMetaData")
        if success:
            cols = [c["name"] for c in d.get("resultSetMetaData", {}).get("rowType", [])]
            rows = d.get("data", [])
            print(f"  *** SUCCESS *** {label}")
            print(f"      Cols={cols} Rows={rows}")
            break
        else:
            msg = d.get("message", "")[:80]
            code = d.get("code", "")
            print(f"  FAIL ({status}) {label} -> code={code} {msg}")
    except Exception as e:
        print(f"  ERROR {label} -> {e}")
else:
    print("\nAll combinations failed.")
