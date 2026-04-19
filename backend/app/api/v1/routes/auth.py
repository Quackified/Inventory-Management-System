from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from mysql.connector import Error

from app.api.deps import get_current_user, require_roles
from app.core.security import create_access_token, hash_password, verify_password
from app.core.storage import AVATARS_DIR
from app.db.connection import get_connection
from app.schemas.auth import AvatarUploadResponse, LoginRequest, LoginResponse, ProfileUpdateRequest, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_user_public(user: dict) -> UserPublic:
    return UserPublic(
        user_id=user["user_id"],
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        email=user.get("email"),
        profile_image_url=user.get("profile_image_url"),
        assigned_warehouse_id=user.get("assigned_warehouse_id"),
        assigned_warehouse_name=user.get("assigned_warehouse_name"),
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT u.user_id, u.username, u.full_name, u.role, u.email, u.profile_image_url, "
            "u.assigned_warehouse_id, w.name AS assigned_warehouse_name, u.password_hash, u.is_active "
            "FROM users u "
            "LEFT JOIN warehouses w ON w.warehouse_id = u.assigned_warehouse_id "
            "WHERE u.username = %s",
            (payload.username,),
        )
        user = cur.fetchone()
        cur.close()

        if not user or int(user.get("is_active", 0)) != 1:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not verify_password(payload.password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        access_token = create_access_token(subject=str(user["user_id"]))
        return LoginResponse(access_token=access_token, user=_build_user_public(user))
    except Error:
        raise HTTPException(status_code=500, detail="Failed to authenticate user")
    finally:
        conn.close()


@router.get("/me", response_model=UserPublic)
def get_me(current_user: dict = Depends(get_current_user)):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT u.user_id, u.username, u.full_name, u.role, u.email, u.profile_image_url, "
            "u.assigned_warehouse_id, w.name AS assigned_warehouse_name "
            "FROM users u "
            "LEFT JOIN warehouses w ON w.warehouse_id = u.assigned_warehouse_id "
            "WHERE u.user_id = %s",
            (current_user["user_id"],),
        )
        user = cur.fetchone()
        cur.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return _build_user_public(user)
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load user profile")
    finally:
        conn.close()


@router.put("/profile", response_model=UserPublic)
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            UPDATE users
            SET username = %s,
                full_name = %s,
                email = %s,
                profile_image_url = %s,
                assigned_warehouse_id = %s
            WHERE user_id = %s
            """,
            (
                payload.username,
                payload.full_name,
                payload.email,
                payload.profile_image_url,
                payload.assigned_warehouse_id,
                current_user["user_id"],
            ),
        )
        conn.commit()

        cur.execute(
            "SELECT u.user_id, u.username, u.full_name, u.role, u.email, u.profile_image_url, "
            "u.assigned_warehouse_id, w.name AS assigned_warehouse_name "
            "FROM users u "
            "LEFT JOIN warehouses w ON w.warehouse_id = u.assigned_warehouse_id "
            "WHERE u.user_id = %s",
            (current_user["user_id"],),
        )
        user = cur.fetchone()
        cur.close()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return _build_user_public(user)
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.post("/avatar", response_model=AvatarUploadResponse)
def upload_avatar(
    file: UploadFile = File(...),
    user_id: int | None = Form(default=None),
    current_user: dict = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file")

    AVATARS_DIR.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}:
        suffix = ".png"

    target_prefix = f"user_{user_id}" if user_id is not None else f"upload_{current_user['user_id']}"
    file_name = f"{target_prefix}_{uuid4().hex}{suffix}"
    file_path = AVATARS_DIR / file_name

    try:
        with file_path.open("wb") as buffer:
            buffer.write(file.file.read())
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to store avatar")

    profile_image_url = f"/uploads/avatars/{file_name}"

    if user_id is not None:
        if current_user.get("role") != "Admin" and int(current_user.get("user_id", 0)) != user_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        conn = get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database unavailable")

        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET profile_image_url = %s WHERE user_id = %s",
                (profile_image_url, user_id),
            )
            conn.commit()
            cur.close()
        except Error:
            raise HTTPException(status_code=500, detail="Failed to update avatar")
        finally:
            conn.close()

    return AvatarUploadResponse(success=True, profile_image_url=profile_image_url)


@router.post("/migrate-legacy-passwords")
def migrate_legacy_passwords(
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, password_hash FROM users")
        users = cur.fetchall()

        migrated = 0
        for user in users:
            stored = user.get("password_hash") or ""
            if stored and not stored.startswith("$"):
                cur.execute(
                    "UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (hash_password(stored), user["user_id"]),
                )
                migrated += 1

        conn.commit()
        cur.close()
        return {"success": True, "migrated_users": migrated}
    except Error:
        raise HTTPException(status_code=500, detail="Failed to migrate passwords")
    finally:
        conn.close()


@router.get("/migration-status")
def migration_status(
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT COUNT(*) AS remaining FROM users WHERE password_hash IS NOT NULL AND password_hash <> '' AND password_hash NOT LIKE '$%'"
        )
        row = cur.fetchone() or {"remaining": 0}
        cur.close()
        remaining = int(row.get("remaining", 0))
        return {
            "success": True,
            "remaining_legacy_passwords": remaining,
            "is_fully_migrated": remaining == 0,
        }
    except Error:
        raise HTTPException(status_code=500, detail="Failed to check migration status")
    finally:
        conn.close()
