from fastapi import APIRouter, HTTPException, status, Response
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token, get_password_hash
from app.core.database import execute_one, execute_write, get_connection
from app.models.schemas import LoginRequest, TokenResponse, UserResponse, MessageResponse
import traceback

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/health")
async def auth_health():
    """Test Snowflake connection, database, schemas, and tables."""
    checks = {
        "snowflake_connection": False,
        "database_exists": False,
        "auth_schema": False,
        "users_table": False,
        "admin_user": False,
        "details": [],
    }
    try:
        conn = get_connection()
        checks["snowflake_connection"] = True
        user_info = getattr(conn, 'user_display', f"{getattr(conn, 'user', '?')}@{getattr(conn, 'account', '?')}")
        checks["details"].append(f"Connected as {user_info}")
    except Exception as e:
        err = str(e)
        checks["details"].append(f"Connection failed: {err}")
        if "password" in err.lower() or "SNOWFLAKE_PASSWORD" in err:
            checks["details"].append(
                "ACTION: Set SNOWFLAKE_PASSWORD in backend/.env. "
                "In Snowflake Worksheet run: ALTER USER SUSANI SET PASSWORD = 'YourPassword';"
            )
        return checks

    try:
        row = execute_one("SELECT CURRENT_DATABASE() AS DB, CURRENT_WAREHOUSE() AS WH, CURRENT_ROLE() AS ROLE")
        checks["details"].append(f"DB={row['DB']}, WH={row['WH']}, ROLE={row['ROLE']}")
        checks["database_exists"] = True
    except Exception as e:
        checks["details"].append(f"Database check failed: {str(e)}")
        return checks

    try:
        execute_one("SELECT 1 FROM CARGOZEN_DB.AUTH.USERS LIMIT 1")
        checks["auth_schema"] = True
        checks["users_table"] = True
    except Exception as e:
        checks["details"].append(f"AUTH.USERS check failed: {str(e)}")
        # Try to see if the schema exists at least
        try:
            execute_one("SELECT 1 FROM CARGOZEN_DB.INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'AUTH'")
            checks["auth_schema"] = True
            checks["details"].append("AUTH schema exists, but USERS table is missing. Run database/01_schema.sql first.")
        except Exception:
            checks["details"].append("AUTH schema does not exist. Run database/01_schema.sql first.")
        return checks

    try:
        user = execute_one(
            "SELECT USER_ID, USERNAME, PASSWORD_HASH FROM CARGOZEN_DB.AUTH.USERS WHERE USERNAME = 'admin'",
            schema="AUTH"
        )
        if user:
            checks["admin_user"] = True
            checks["details"].append(f"Admin user found (USER_ID={user['USER_ID']})")
            # Check if the password hash is valid bcrypt
            ph = user.get("PASSWORD_HASH", "")
            if not ph or not ph.startswith("$2"):
                checks["details"].append("WARNING: admin PASSWORD_HASH is not a valid bcrypt hash!")
            else:
                # Test the default password
                if verify_password("Admin@123", ph):
                    checks["details"].append("Default password 'Admin@123' is VALID")
                else:
                    checks["details"].append("WARNING: Default password 'Admin@123' does NOT match the stored hash.")
                    checks["details"].append(f"Hash starts with: {ph[:20]}...")
                    # Generate correct hash for reference
                    correct_hash = get_password_hash("Admin@123")
                    checks["details"].append(f"Correct hash for 'Admin@123': {correct_hash}")
        else:
            checks["details"].append("No admin user found. Run database/02_seed_data.sql first.")
    except Exception as e:
        checks["details"].append(f"Admin user check failed: {str(e)}")

    return checks


@router.post("/fix-admin-password")
async def fix_admin_password():
    """Emergency: regenerate the admin password hash for 'Admin@123'."""
    correct_hash = get_password_hash("Admin@123")
    try:
        rows = execute_write(
            "UPDATE CARGOZEN_DB.AUTH.USERS SET PASSWORD_HASH = %s WHERE USERNAME = 'admin'",
            (correct_hash,), schema="AUTH"
        )
        if rows and rows > 0:
            return {"message": "Admin password reset to 'Admin@123'", "success": True, "hash": correct_hash}
        else:
            return {"message": "Admin user not found. Run seed data first.", "success": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, response: Response):
    # Prevent 304 Not Modified – auth responses must never be cached
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # First check if we can connect to Snowflake at all
    try:
        user = execute_one(
            """SELECT u.USER_ID, u.USERNAME, u.EMAIL, u.FULL_NAME, u.ROLE_ID,
                      u.PASSWORD_HASH, u.IS_ACTIVE, r.ROLE_NAME
               FROM AUTH.USERS u
               LEFT JOIN AUTH.ROLES r ON u.ROLE_ID = r.ROLE_ID
               WHERE u.USERNAME = %s""",
            (credentials.username,), schema="AUTH"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "does not exist" in error_msg or "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database tables not found. Please run the SQL setup scripts (database/01_schema.sql and 02_seed_data.sql) in Snowflake first."
            )
        if "authentication" in error_msg or "browser" in error_msg or "token" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Snowflake authentication required. A browser window should have opened — please complete SSO login and try again."
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)[:200]}"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.get("PASSWORD_HASH"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account has no password set. Contact administrator."
        )

    if not verify_password(credentials.password, user["PASSWORD_HASH"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user["IS_ACTIVE"]:
        raise HTTPException(status_code=400, detail="Account is inactive. Contact administrator.")

    token_data = {"sub": str(user["USER_ID"])}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    try:
        execute_write(
            "UPDATE AUTH.USERS SET REFRESH_TOKEN = %s, LAST_LOGIN = CURRENT_TIMESTAMP() WHERE USER_ID = %s",
            (refresh_token, user["USER_ID"]), schema="AUTH"
        )
    except Exception:
        pass  # Non-critical — login still succeeds

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": user["USER_ID"],
            "username": user["USERNAME"],
            "email": user["EMAIL"],
            "full_name": user["FULL_NAME"],
            "role_name": user["ROLE_NAME"],
        }
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(body: dict, response: Response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Refresh token required")

    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = execute_one(
        "SELECT USER_ID, REFRESH_TOKEN, IS_ACTIVE FROM AUTH.USERS WHERE USER_ID = %s",
        (int(user_id),), schema="AUTH"
    )

    if not user or user["REFRESH_TOKEN"] != token or not user["IS_ACTIVE"]:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": str(user_id)})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout", response_model=MessageResponse)
async def logout(body: dict):
    token = body.get("access_token")
    if token:
        payload = decode_token(token)
        if payload:
            jti = payload.get("jti")
            if jti:
                try:
                    execute_write(
                        "INSERT INTO AUTH.TOKEN_BLACKLIST (TOKEN_JTI, EXPIRES_AT) VALUES (%s, %s)",
                        (jti, payload.get("exp")), schema="AUTH"
                    )
                except Exception:
                    pass
    return MessageResponse(message="Logged out successfully")