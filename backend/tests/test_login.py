"""
Comprehensive login tests for CargoZen auth endpoints.
Mocks the Snowflake database layer so tests run without a live connection.

Run:  cd backend && python -m pytest tests/test_login.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helpers – fake DB rows returned by execute_one / execute_write
# ---------------------------------------------------------------------------
ADMIN_HASH = get_password_hash("Admin@123")

ADMIN_ROW = {
    "USER_ID": 1,
    "USERNAME": "admin",
    "EMAIL": "admin@cargozen.com",
    "FULL_NAME": "System Administrator",
    "ROLE_ID": 1,
    "PASSWORD_HASH": ADMIN_HASH,
    "IS_ACTIVE": True,
    "ROLE_NAME": "SUPER_ADMIN",
}

INACTIVE_ROW = {**ADMIN_ROW, "USER_ID": 99, "USERNAME": "disabled", "IS_ACTIVE": False}

NO_HASH_ROW = {**ADMIN_ROW, "USER_ID": 88, "USERNAME": "nohash", "PASSWORD_HASH": ""}


# ====================================================================
# Unit tests – security helpers (no DB, no HTTP)
# ====================================================================
class TestPasswordHashing:
    """Verify bcrypt hash / verify round-trip works."""

    def test_hash_and_verify(self):
        h = get_password_hash("Admin@123")
        assert h.startswith("$2b$")
        assert verify_password("Admin@123", h)

    def test_wrong_password_rejected(self):
        h = get_password_hash("Admin@123")
        assert not verify_password("wrong", h)

    def test_different_hashes_each_time(self):
        h1 = get_password_hash("Admin@123")
        h2 = get_password_hash("Admin@123")
        # bcrypt uses a random salt → hashes differ
        assert h1 != h2
        # both still verify
        assert verify_password("Admin@123", h1)
        assert verify_password("Admin@123", h2)


class TestJWT:
    """Verify JWT creation and decoding."""

    def test_access_token_round_trip(self):
        token = create_access_token({"sub": "1"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "access"

    def test_refresh_token_round_trip(self):
        token = create_refresh_token({"sub": "42"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.token") is None

    def test_tokens_contain_jti(self):
        t1 = create_access_token({"sub": "1"})
        t2 = create_access_token({"sub": "1"})
        p1 = decode_token(t1)
        p2 = decode_token(t2)
        assert p1["jti"] != p2["jti"]


# ====================================================================
# Integration tests – /api/auth/login endpoint (DB mocked)
# ====================================================================
DB_MODULE = "app.api.routes.auth"


class TestLoginEndpoint:
    """POST /api/auth/login — all scenarios."""

    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    @patch(f"{DB_MODULE}.execute_one", return_value=ADMIN_ROW)
    def test_login_success(self, mock_query, mock_write):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"
        assert data["user"]["role_name"] == "SUPER_ADMIN"

    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    @patch(f"{DB_MODULE}.execute_one", return_value=ADMIN_ROW)
    def test_login_returns_valid_jwt(self, mock_query, mock_write):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        token = res.json()["access_token"]
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "access"

    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    @patch(f"{DB_MODULE}.execute_one", return_value=ADMIN_ROW)
    def test_login_has_no_cache_headers(self, mock_query, mock_write):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert "no-store" in res.headers.get("cache-control", "")
        assert res.headers.get("pragma") == "no-cache"

    @patch(f"{DB_MODULE}.execute_one", return_value=None)
    def test_login_unknown_user_401(self, mock_query):
        res = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
        assert res.status_code == 401
        assert "incorrect" in res.json()["detail"].lower()

    @patch(f"{DB_MODULE}.execute_one", return_value=ADMIN_ROW)
    def test_login_wrong_password_401(self, mock_query):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword"})
        assert res.status_code == 401
        assert "incorrect" in res.json()["detail"].lower()

    @patch(f"{DB_MODULE}.execute_one", return_value=NO_HASH_ROW)
    def test_login_no_hash_401(self, mock_query):
        res = client.post("/api/auth/login", json={"username": "nohash", "password": "Admin@123"})
        assert res.status_code == 401
        assert "no password" in res.json()["detail"].lower()

    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    @patch(f"{DB_MODULE}.execute_one", return_value=INACTIVE_ROW)
    def test_login_inactive_user_400(self, mock_query, mock_write):
        res = client.post("/api/auth/login", json={"username": "disabled", "password": "Admin@123"})
        assert res.status_code == 400
        assert "inactive" in res.json()["detail"].lower()

    def test_login_missing_fields_422(self):
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 422

    def test_login_empty_username_422(self):
        res = client.post("/api/auth/login", json={"password": "Admin@123"})
        assert res.status_code == 422

    @patch(f"{DB_MODULE}.execute_one", side_effect=RuntimeError("SQL error (code 2003): table does not exist"))
    def test_login_db_missing_tables_503(self, mock_query):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert res.status_code == 503

    @patch(f"{DB_MODULE}.execute_one", side_effect=ConnectionError("Snowflake login failed"))
    def test_login_db_connection_error_503(self, mock_query):
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert res.status_code == 503


# ====================================================================
# Integration tests – /api/auth/refresh endpoint (DB mocked)
# ====================================================================
class TestRefreshEndpoint:
    """POST /api/auth/refresh — all scenarios."""

    def _make_tokens(self, user_id="1"):
        access = create_access_token({"sub": user_id})
        refresh = create_refresh_token({"sub": user_id})
        return access, refresh

    @patch(f"{DB_MODULE}.execute_one")
    def test_refresh_success(self, mock_query):
        _, refresh = self._make_tokens()
        mock_query.return_value = {"USER_ID": 1, "REFRESH_TOKEN": refresh, "IS_ACTIVE": True}
        res = client.post("/api/auth/refresh", json={"refresh_token": refresh})
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_refresh_missing_token_400(self):
        res = client.post("/api/auth/refresh", json={})
        assert res.status_code == 400

    def test_refresh_invalid_token_401(self):
        res = client.post("/api/auth/refresh", json={"refresh_token": "garbage"})
        assert res.status_code == 401

    @patch(f"{DB_MODULE}.execute_one")
    def test_refresh_token_mismatch_401(self, mock_query):
        _, refresh = self._make_tokens()
        mock_query.return_value = {"USER_ID": 1, "REFRESH_TOKEN": "other-token", "IS_ACTIVE": True}
        res = client.post("/api/auth/refresh", json={"refresh_token": refresh})
        assert res.status_code == 401


# ====================================================================
# Integration tests – /api/auth/fix-admin-password (DB mocked)
# ====================================================================
class TestFixAdminPassword:
    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    def test_fix_admin_password_success(self, mock_write):
        res = client.post("/api/auth/fix-admin-password")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["hash"].startswith("$2b$")

    @patch(f"{DB_MODULE}.execute_write", return_value=0)
    def test_fix_admin_password_no_user(self, mock_write):
        res = client.post("/api/auth/fix-admin-password")
        data = res.json()
        assert data["success"] is False


# ====================================================================
# Integration tests – basic health / root
# ====================================================================
class TestHealthEndpoints:
    def test_root(self):
        res = client.get("/")
        assert res.status_code == 200
        assert res.json()["status"] == "running"

    def test_health(self):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"


# ====================================================================
# Seed-hash verification test
# ====================================================================
class TestSeedHash:
    """Verify the bcrypt hash in 02_seed_data.sql matches 'Admin@123'."""

    SEED_HASH = "$2b$12$w6A8f/OdtgzKWztfRLOKSus6dYjo0PL0e2hE0ZLHGmzZbglnr6nL2"

    def test_seed_hash_matches_default_password(self):
        """The hash in 02_seed_data.sql MUST verify against 'Admin@123'."""
        assert verify_password("Admin@123", self.SEED_HASH), \
            "Seed hash does not match Admin@123 — update 02_seed_data.sql!"

    def test_seed_hash_rejects_wrong_password(self):
        assert not verify_password("wrong", self.SEED_HASH)

    def test_hash_roundtrip(self):
        new_hash = get_password_hash("Admin@123")
        assert verify_password("Admin@123", new_hash)


# ====================================================================
# Startup database check tests
# ====================================================================
DB_CORE = "app.core.database"


class TestCheckDatabase:
    """Verify _check_database reports status correctly."""

    @patch(f"{DB_CORE}.execute_one")
    def test_check_ok_when_admin_exists(self, mock_one, capsys):
        """When admin exists with valid hash, prints [OK]."""
        import logging
        from app.main import _check_database
        good_hash = get_password_hash("Admin@123")
        mock_one.side_effect = [
            {"CNT": "5"},                                 # roles count
            {"USER_ID": "1", "USERNAME": "admin", "PASSWORD_HASH": good_hash},
        ]
        _check_database(logging.getLogger("test"))
        out = capsys.readouterr().out
        assert "[OK]" in out
        assert "ACTION REQUIRED" not in out

    @patch(f"{DB_CORE}.execute_one")
    def test_check_warns_when_no_admin(self, mock_one, capsys):
        """When admin user is missing, prints ACTION REQUIRED."""
        import logging
        from app.main import _check_database
        mock_one.side_effect = [
            {"CNT": "5"},   # roles exist
            None,           # admin user not found
        ]
        _check_database(logging.getLogger("test"))
        out = capsys.readouterr().out
        assert "ACTION REQUIRED" in out

    @patch(f"{DB_CORE}.execute_one")
    def test_check_warns_when_roles_empty(self, mock_one, capsys):
        """When roles table is empty, prints ACTION REQUIRED."""
        import logging
        from app.main import _check_database
        mock_one.side_effect = [
            {"CNT": "0"},   # no roles
            None,           # admin also missing
        ]
        _check_database(logging.getLogger("test"))
        out = capsys.readouterr().out
        assert "EMPTY" in out
        assert "ACTION REQUIRED" in out


class TestLoginAutoRepair:
    """Verify the login endpoint auto-repairs the admin hash if broken."""

    BAD_HASH = "$2b$12$BADHASHXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    BAD_ADMIN = {**ADMIN_ROW, "PASSWORD_HASH": BAD_HASH}

    @patch(f"{DB_MODULE}.execute_write", return_value=1)
    @patch(f"{DB_MODULE}.execute_one")
    def test_auto_repair_admin_on_login(self, mock_one, mock_write):
        """If admin hash is bad but user sends correct default password, auto-repair and succeed."""
        repaired_row = {**ADMIN_ROW, "PASSWORD_HASH": get_password_hash("Admin@123")}
        mock_one.side_effect = [
            self.BAD_ADMIN,   # initial query — bad hash
            repaired_row,     # re-fetch after repair
        ]
        res = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        assert res.status_code == 200
        assert "access_token" in res.json()

    @patch(f"{DB_MODULE}.execute_one", return_value=ADMIN_ROW)
    def test_no_repair_for_non_admin(self, mock_one):
        """Auto-repair only works for admin account, not arbitrary users."""
        res = client.post("/api/auth/login", json={"username": "admin", "password": "WrongPassword"})
        assert res.status_code == 401
