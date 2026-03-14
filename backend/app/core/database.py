"""
Snowflake database layer — Session token auth via internal query API.
Uses /session/v1/login-request + /queries/v1/query-request.
"""
from contextlib import contextmanager
from typing import Generator, Optional
from app.core.config import settings
import httpx
import time
import uuid
import logging

logger = logging.getLogger("cargozen.db")


class SnowflakeClient:
    """Connects to Snowflake via password auth + internal query API."""

    def __init__(self):
        self.account = settings.SNOWFLAKE_ACCOUNT
        self.user = settings.SNOWFLAKE_USER
        self.warehouse = settings.SNOWFLAKE_WAREHOUSE
        self.database = settings.SNOWFLAKE_DATABASE
        self.role = settings.SNOWFLAKE_ROLE
        self.base = f"https://{self.account}.snowflakecomputing.com"
        self._http = httpx.Client(
            verify=False, timeout=30, follow_redirects=True,
            headers={"User-Agent": "PythonConnector/3.7.0 (CargoZen)"},
        )
        self._token: Optional[str] = None
        self._token_expires = 0.0
        self._seq = 0

    @property
    def user_display(self):
        return f"{self.user}@{self.account}"

    def is_closed(self):
        return self._token is None

    # ─── Auth ────────────────────────────────────────────────
    def _ensure_auth(self):
        if self._token and time.time() < self._token_expires:
            return
        self._login()

    def _login(self):
        body = {
            "data": {
                "ACCOUNT_NAME": self.account,
                "LOGIN_NAME": self.user,
                "PASSWORD": settings.SNOWFLAKE_PASSWORD,
                "CLIENT_APP_ID": "PythonConnector",
                "CLIENT_APP_VERSION": "3.7.0",
            }
        }
        r = self._http.post(
            f"{self.base}/session/v1/login-request",
            json=body,
            params={
                "warehouse": self.warehouse,
                "databaseName": self.database,
                "roleName": self.role,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        data = r.json()
        if not data.get("success"):
            code = data.get("code", "")
            msg = data.get("message", r.text[:300])
            raise ConnectionError(f"Snowflake login failed (code {code}): {msg}")
        self._token = data["data"]["token"]
        self._token_expires = time.time() + 12600  # ~3.5 hours
        logger.info("Snowflake session authenticated OK")

    # ─── SQL Execution ───────────────────────────────────────
    def execute(self, sql: str, params: tuple = None, schema: str = "AUTH") -> list[dict]:
        self._ensure_auth()

        stmt = sql
        if params:
            for p in params:
                if p is None:
                    stmt = stmt.replace("%s", "NULL", 1)
                elif isinstance(p, (int, float)):
                    stmt = stmt.replace("%s", str(p), 1)
                else:
                    escaped = str(p).replace("'", "''")
                    stmt = stmt.replace("%s", f"'{escaped}'", 1)

        self._seq += 1
        r = self._http.post(
            f"{self.base}/queries/v1/query-request",
            params={
                "requestId": str(uuid.uuid4()),
                "request_guid": str(uuid.uuid4()),
            },
            json={
                "sqlText": stmt,
                "asyncExec": False,
                "sequenceId": self._seq,
                "isInternal": False,
            },
            headers={
                "Authorization": f'Snowflake Token="{self._token}"',
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            body = r.json()
        except Exception:
            raise RuntimeError(f"Non-JSON response (HTTP {r.status_code}): {r.text[:200]}")

        if not body.get("success"):
            code = body.get("code", "")
            msg = body.get("message", "Unknown error")
            if code in ("390103", "390104"):
                # Session expired, re-login
                self._token = None
                self._ensure_auth()
                return self.execute(sql, params, schema)
            raise RuntimeError(f"SQL error (code {code}): {msg}")

        rd = body.get("data", {})
        cols = [c["name"] for c in rd.get("rowtype", [])]
        rows_raw = rd.get("rowset", [])

        result = []
        for row in rows_raw:
            rec = {}
            for i, col in enumerate(cols):
                val = row[i] if i < len(row) else None
                if isinstance(val, str):
                    vl = val.lower()
                    if vl == "true":
                        val = True
                    elif vl == "false":
                        val = False
                rec[col] = val
            result.append(rec)
        return result


# ═══════════════════════════════════════════════════
# Singleton + cursor
# ═══════════════════════════════════════════════════
_client: Optional[SnowflakeClient] = None


def get_connection() -> SnowflakeClient:
    global _client
    if not _client:
        _client = SnowflakeClient()
    return _client


class _Cursor:
    def __init__(self, client: SnowflakeClient, schema: str = None):
        self._c = client
        self._s = schema or "AUTH"
        self._r: list = []

    def execute(self, sql: str, params: tuple = None):
        if sql.strip().upper().startswith("USE SCHEMA"):
            return
        self._r = self._c.execute(sql, params, self._s)

    def fetchall(self):
        return self._r

    def fetchone(self):
        return self._r[0] if self._r else None

    @property
    def rowcount(self):
        return len(self._r)

    def close(self):
        pass


@contextmanager
def get_cursor(schema: str = None) -> Generator:
    yield _Cursor(get_connection(), schema)


def execute_query(sql: str, params: tuple = None, schema: str = "AUTH"):
    with get_cursor(schema) as c:
        c.execute(sql, params)
        return c.fetchall()


def execute_one(sql: str, params: tuple = None, schema: str = "AUTH"):
    with get_cursor(schema) as c:
        c.execute(sql, params)
        return c.fetchone()


def execute_write(sql: str, params: tuple = None, schema: str = "AUTH"):
    with get_cursor(schema) as c:
        c.execute(sql, params)
        return c.rowcount


def execute_insert_returning_id(sql: str, params: tuple = None, schema: str = "AUTH"):
    with get_cursor(schema) as c:
        c.execute(sql, params)
        row = c.fetchone()
        return list(row.values())[0] if row else None
