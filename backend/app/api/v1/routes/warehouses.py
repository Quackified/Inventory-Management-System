from fastapi import APIRouter, Depends, HTTPException
from mysql.connector import Error

from app.api.deps import require_roles
from app.db.connection import get_connection
from app.schemas.warehouse import (
    WarehouseItem,
    WarehouseListResponse,
    WarehouseMutationResponse,
    WarehouseWriteRequest,
)

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("", response_model=WarehouseListResponse)
def list_warehouses(
    _: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT warehouse_id, name, location, is_active FROM warehouses ORDER BY name"
        )
        rows = cur.fetchall()
        cur.close()
        return WarehouseListResponse(
            items=[
                WarehouseItem(
                    warehouse_id=row[0],
                    name=row[1],
                    location=row[2],
                    is_active=int(row[3]),
                )
                for row in rows
            ]
        )
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load warehouses")
    finally:
        conn.close()


@router.post("", response_model=WarehouseMutationResponse)
def create_warehouse(
    payload: WarehouseWriteRequest,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO warehouses (name, location, is_active) VALUES (%s, %s, %s)",
            (payload.name, payload.location, payload.is_active),
        )
        warehouse_id = cur.lastrowid
        conn.commit()
        cur.close()
        return WarehouseMutationResponse(
            success=True,
            message=f"Warehouse '{payload.name}' added.",
            warehouse_id=warehouse_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.put("/{warehouse_id}", response_model=WarehouseMutationResponse)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseWriteRequest,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE warehouses SET name=%s, location=%s, is_active=%s WHERE warehouse_id=%s",
            (payload.name, payload.location, payload.is_active, warehouse_id),
        )
        affected = cur.rowcount
        conn.commit()
        cur.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        return WarehouseMutationResponse(
            success=True,
            message=f"Warehouse #{warehouse_id} updated.",
            warehouse_id=warehouse_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{warehouse_id}", response_model=WarehouseMutationResponse)
def delete_warehouse(
    warehouse_id: int,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM warehouses WHERE warehouse_id=%s", (warehouse_id,))
        affected = cur.rowcount
        conn.commit()
        cur.close()
        if affected == 0:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        return WarehouseMutationResponse(
            success=True,
            message=f"Warehouse #{warehouse_id} deleted.",
            warehouse_id=warehouse_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
