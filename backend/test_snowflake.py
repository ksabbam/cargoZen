"""Snowflake connectivity diagnostic."""
import socket
import time
import ssl

HOST = "FCJPXYK-ZH80005.snowflakecomputing.com"
URL_BASE = f"https://{HOST}"
LOGIN_URL = f"{URL_BASE}/session/v1/login-request"

print("=" * 50)
print("  Snowflake Connectivity Test")
print("=" * 50)

# 1. DNS
print("\n[1] DNS Resolution...")
try:
    ip = socket.getaddrinfo(HOST, 443)[0][4][0]
    print(f"    OK -> {ip}")
except Exception as e:
    print(f"    FAILED -> {e}")

# 2. TCP
print("\n[2] TCP Port 443...")
try:
    s = socket.create_connection((HOST, 443), timeout=5)
    s.close()
    print("    OK")
except Exception as e:
    print(f"    FAILED -> {e}")
    print("    >>> Firewall or proxy may be blocking outbound HTTPS")

# 3. TLS Handshake
print("\n[3] TLS Handshake...")
try:
    ctx = ssl.create_default_context()
    with socket.create_connection((HOST, 443), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=HOST) as ssock:
            print(f"    OK (protocol={ssock.version()}, cipher={ssock.cipher()[0]})")
except ssl.SSLCertVerificationError as e:
    print(f"    SSL CERT ERROR -> {e}")
    print("    >>> Corporate proxy may be intercepting SSL. Trying without verify...")
    try:
        ctx2 = ssl._create_unverified_context()
        with socket.create_connection((HOST, 443), timeout=10) as sock2:
            with ctx2.wrap_socket(sock2, server_hostname=HOST) as ssock2:
                print(f"    OK (unverified, protocol={ssock2.version()})")
    except Exception as e2:
        print(f"    FAILED even without verify -> {e2}")
except Exception as e:
    print(f"    FAILED -> {type(e).__name__}: {e}")

# 4. HTTP GET
print("\n[4] HTTPS GET (health check)...")
import httpx
try:
    r = httpx.get(URL_BASE + "/", verify=False, timeout=10)
    print(f"    OK (status={r.status_code}, len={len(r.content)})")
except Exception as e:
    print(f"    FAILED -> {type(e).__name__}: {e}")

# 5. Login Request
print("\n[5] Login API (password auth)...")
try:
    body = {
        "data": {
            "ACCOUNT_NAME": "FCJPXYK-ZH80005",
            "LOGIN_NAME": "SUSANI",
            "PASSWORD": "LetItSnow123!!",
            "CLIENT_APP_ID": "CargoZen",
            "CLIENT_APP_VERSION": "1.0",
        }
    }
    params = {
        "warehouse": "CARGOZEN_WH",
        "databaseName": "CARGOZEN_DB",
        "roleName": "ACCOUNTADMIN",
    }
    t0 = time.time()
    r = httpx.post(
        LOGIN_URL,
        json=body,
        params=params,
        verify=False,
        timeout=20,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    elapsed = time.time() - t0
    print(f"    Status: {r.status_code} ({elapsed:.1f}s)")
    
    try:
        d = r.json()
        success = d.get("success")
        code = d.get("code", "")
        msg = d.get("message", "")
        print(f"    success={success}  code={code}")
        if msg:
            print(f"    message={msg[:200]}")
        if success and "data" in d:
            token = d["data"].get("token", "")
            print(f"    TOKEN: {'YES (' + str(len(token)) + ' chars)' if token else 'MISSING'}")
    except Exception:
        print(f"    Raw response: {r.text[:300]}")
except httpx.TimeoutException as e:
    print(f"    TIMEOUT -> {e}")
    print("    >>> The request to Snowflake timed out. Check firewall/proxy.")
except Exception as e:
    print(f"    FAILED -> {type(e).__name__}: {e}")

print("\n" + "=" * 50)
print("  Done")
print("=" * 50)
