from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import Error

from app.api.deps import require_roles
from app.core.security import hash_password
from app.db.connection import get_connection
from app.schemas.account import (
    AccountCreateRequest,
    AccountItem,
    AccountListResponse,
    AccountMutationResponse,
    AccountUpdateRequest,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=AccountListResponse)
def list_accounts(
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT u.user_id, u.username, u.full_name, u.role, u.email, u.is_active,
                   u.profile_image_url, u.assigned_warehouse_id, w.name AS assigned_warehouse_name
            FROM users u
            LEFT JOIN warehouses w ON w.warehouse_id = u.assigned_warehouse_id
            ORDER BY user_id
            """
        )
        rows = cur.fetchall()
        cur.close()

        return AccountListResponse(
            items=[
                AccountItem(
                    user_id=row[0],
                    username=row[1],
                    full_name=row[2],
                    role=row[3],
                    email=row[4],
                    is_active=int(row[5]),
                    profile_image_url=row[6],
                    assigned_warehouse_id=row[7],
                    assigned_warehouse_name=row[8],
                )
                for row in rows
            ]
        )
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load accounts")
    finally:
        conn.close()


@router.post("", response_model=AccountMutationResponse)
def create_account(
    payload: AccountCreateRequest,
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, password_hash, full_name, role, email, profile_image_url, assigned_warehouse_id, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payload.username,
                hash_password(payload.password),
                payload.full_name,
                payload.role,
                payload.email,
                payload.profile_image_url,
                payload.assigned_warehouse_id,
                payload.is_active,
            ),
        )
        user_id = cur.lastrowid
        conn.commit()
        cur.close()
        return AccountMutationResponse(success=True, message="Account created.", user_id=user_id)
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.put("/{user_id}", response_model=AccountMutationResponse)
def update_account(
    user_id: int,
    payload: AccountUpdateRequest,
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        if payload.password:
            cur.execute(
                """
                UPDATE users
                SET username = %s,
                    full_name = %s,
                    role = %s,
                    email = %s,
                    profile_image_url = %s,
                    assigned_warehouse_id = %s,
                    is_active = %s,
                    password_hash = %s
                WHERE user_id = %s
                """,
                (
                    payload.username,
                    payload.full_name,
                    payload.role,
                    payload.email,
                    payload.profile_image_url,
                    payload.assigned_warehouse_id,
                    payload.is_active,
                    hash_password(payload.password),
                    user_id,
                ),
            )
        else:
            cur.execute(
                """
                UPDATE users
                SET username = %s,
                    full_name = %s,
                    role = %s,
                    email = %s,
                    profile_image_url = %s,
                    assigned_warehouse_id = %s,
                    is_active = %s
                WHERE user_id = %s
                """,
                (
                    payload.username,
                    payload.full_name,
                    payload.role,
                    payload.email,
                    payload.profile_image_url,
                    payload.assigned_warehouse_id,
                    payload.is_active,
                    user_id,
                ),
            )
        affected = cur.rowcount
        conn.commit()
        cur.close()

        if affected == 0:
            raise HTTPException(status_code=404, detail="Account not found")

        return AccountMutationResponse(success=True, message="Account updated.", user_id=user_id)
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{user_id}", response_model=AccountMutationResponse)
def delete_account(
    user_id: int,
    _: dict = Depends(require_roles("Admin")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        affected = cur.rowcount
        conn.commit()
        cur.close()

        if affected == 0:
            raise HTTPException(status_code=404, detail="Account not found")

        return AccountMutationResponse(success=True, message="Account deleted.", user_id=user_id)
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
