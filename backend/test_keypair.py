"""Test: Generate key-pair JWT for Snowflake SQL API v2."""
import httpx
import time
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt  # PyJWT

ACCOUNT = "FCJPXYK-ZH80005"
USER = "SUSANI"
HOST = f"{ACCOUNT}.snowflakecomputing.com"
BASE = f"https://{HOST}"

# Generate RSA key pair
print("Generating RSA key pair...")
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# Get public key fingerprint (SHA256 of DER)
pub_der = public_key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
sha256 = hashlib.sha256(pub_der).digest()
fingerprint = "SHA256:" + base64.b64encode(sha256).decode("utf-8")
print(f"Public key fingerprint: {fingerprint}")

# Save public key PEM for registering with Snowflake
pub_pem = public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
print(f"\nTo register this key with Snowflake, run in a Worksheet:")
# Extract just the base64 part (no headers)
pub_b64 = pub_pem.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")
print(f"  ALTER USER {USER} SET RSA_PUBLIC_KEY = '{pub_b64}';")

# Generate JWT
account_upper = ACCOUNT.upper().replace("-", "_") if "-" in ACCOUNT else ACCOUNT.upper()
qualified_user = f"{account_upper}.{USER.upper()}"

now = int(time.time())
payload = {
    "iss": f"{qualified_user}.{fingerprint}",
    "sub": qualified_user,
    "iat": now,
    "exp": now + 3600,
}

priv_pem = private_key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
jwt_token = jwt.encode(payload, priv_pem, algorithm="RS256")
print(f"\nJWT token generated ({len(jwt_token)} chars)")

# Test query with JWT
print("\nTesting SQL API v2 with JWT...")
sql = "SELECT CURRENT_VERSION() AS V, CURRENT_USER() AS U"
query_payload = {"statement": sql, "timeout": 60, "database": "CARGOZEN_DB", "schema": "AUTH", "warehouse": "CARGOZEN_WH", "role": "ACCOUNTADMIN"}
headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json", "Accept": "application/json", "X-Snowflake-Authorization-Token-Type": "KEYPAIR_JWT"}
r = httpx.post(f"{BASE}/api/v2/statements", json=query_payload, headers=headers, verify=False, timeout=15)
print(f"Status: {r.status_code}")
d = r.json()
if d.get("resultSetMetaData"):
    cols = [c["name"] for c in d["resultSetMetaData"]["rowType"]]
    rows = d.get("data", [])
    print(f"SUCCESS! Cols={cols} Rows={rows}")
else:
    print(f"Response: code={d.get('code')} message={d.get('message', '')[:200]}")
    if "390144" in str(d.get("code", "")):
        print("\n>>> The key is not registered yet. Run the ALTER USER command above in Snowflake Worksheet first.")
