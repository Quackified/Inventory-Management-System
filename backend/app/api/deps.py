from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from mysql.connector import Error

from app.core.config import settings
from app.db.connection import get_connection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
        user_id = int(user_id_raw)
    except (JWTError, ValueError):
        raise credentials_exception

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT user_id, username, full_name, role, is_active, assigned_warehouse_id FROM users WHERE user_id = %s",
            (user_id,),
        )
        user = cur.fetchone()
        cur.close()

        if not user or int(user.get("is_active", 0)) != 1:
            raise credentials_exception

        return user
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load user")
    finally:
        conn.close()


def get_warehouse_scope(user: dict) -> int | None:
    if user.get("role") == "Admin":
        return None

    warehouse_id = user.get("assigned_warehouse_id")
    if warehouse_id is None:
        raise HTTPException(status_code=403, detail="No warehouse assigned")
    return int(warehouse_id)


def require_roles(*allowed_roles: str):
    def role_dependency(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return role_dependency
