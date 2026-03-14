from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_token
from app.core.database import execute_one
from app.models.schemas import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Check token blacklist
    jti = payload.get("jti")
    if jti:
        blacklisted = execute_one(
            "SELECT TOKEN_JTI FROM AUTH.TOKEN_BLACKLIST WHERE TOKEN_JTI = %s",
            (jti,), schema="AUTH"
        )
        if blacklisted:
            raise credentials_exception

    # Fetch user
    user = execute_one(
        """SELECT u.USER_ID, u.USERNAME, u.EMAIL, u.FULL_NAME, u.ROLE_ID,
                  r.ROLE_NAME, u.IS_ACTIVE
           FROM AUTH.USERS u
           LEFT JOIN AUTH.ROLES r ON u.ROLE_ID = r.ROLE_ID
           WHERE u.USER_ID = %s AND u.IS_ACTIVE = TRUE""",
        (int(user_id),), schema="AUTH"
    )
    if user is None:
        raise credentials_exception

    return UserResponse(**{k.lower(): v for k, v in user.items()})


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*roles: str):
    async def role_checker(current_user: UserResponse = Depends(get_current_active_user)):
        if current_user.role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
