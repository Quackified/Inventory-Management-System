from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import Error

from app.api.deps import require_roles
from app.db.connection import get_connection
from app.schemas.category import (
    CategoryItem,
    CategoryListResponse,
    CategoryMutationResponse,
    CategoryWriteRequest,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryListResponse)
def list_categories(
    _: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute("SELECT category_id, name, description FROM categories ORDER BY name")
        rows = cur.fetchall()
        cur.close()
        return CategoryListResponse(
            items=[
                CategoryItem(
                    category_id=row[0],
                    name=row[1],
                    description=row[2],
                )
                for row in rows
            ]
        )
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load categories")
    finally:
        conn.close()


@router.post("", response_model=CategoryMutationResponse)
def create_category(
    payload: CategoryWriteRequest,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (payload.name, payload.description),
        )
        category_id = cur.lastrowid
        conn.commit()
        cur.close()
        return CategoryMutationResponse(
            success=True,
            message=f"Category '{payload.name}' added.",
            category_id=category_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.put("/{category_id}", response_model=CategoryMutationResponse)
def update_category(
    category_id: int,
    payload: CategoryWriteRequest,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE categories SET name=%s, description=%s WHERE category_id=%s",
            (payload.name, payload.description, category_id),
        )
        affected = cur.rowcount
        conn.commit()
        cur.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryMutationResponse(
            success=True,
            message=f"Category #{category_id} updated.",
            category_id=category_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{category_id}", response_model=CategoryMutationResponse)
def delete_category(
    category_id: int,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        affected = cur.rowcount
        conn.commit()
        cur.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryMutationResponse(
            success=True,
            message=f"Category #{category_id} deleted.",
            category_id=category_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
