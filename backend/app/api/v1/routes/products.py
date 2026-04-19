from fastapi import APIRouter, Depends, HTTPException, Query
from mysql.connector import Error

from app.api.deps import get_warehouse_scope, require_roles
from app.db.connection import get_connection
from app.schemas.product import (
    ProductListItem,
    ProductListResponse,
    ProductMutationResponse,
    ProductWriteRequest,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)

        count_query = "SELECT COUNT(*) FROM products WHERE is_deleted = 0"
        count_params: list[object] = []
        if warehouse_scope is not None:
            count_query += " AND warehouse_id = %s"
            count_params.append(warehouse_scope)
        if search:
            count_query += " AND name LIKE %s"
            count_params.append(f"%{search}%")
        cur.execute(count_query, tuple(count_params))
        total = int(cur.fetchone()[0])

        data_query = """
            SELECT p.product_id, p.name, p.description, p.current_stock,
                   p.unit_price, p.unit,
                   COALESCE(w.name, '—') AS warehouse,
                   COALESCE(c.name, '—') AS category,
                   p.low_stock_threshold,
                   p.expiry_date, p.expiry_status,
                   p.manufactured_date, p.batch_number
            FROM products p
            LEFT JOIN warehouses w ON p.warehouse_id = w.warehouse_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_deleted = 0
        """
        data_params: list[object] = []
        if warehouse_scope is not None:
            data_query += " AND p.warehouse_id = %s"
            data_params.append(warehouse_scope)
        if search:
            data_query += " AND p.name LIKE %s"
            data_params.append(f"%{search}%")

        data_query += " ORDER BY p.product_id LIMIT %s OFFSET %s"
        data_params.extend([page_size, (page - 1) * page_size])
        cur.execute(data_query, tuple(data_params))
        rows = cur.fetchall()
        cur.close()

        items = [
            ProductListItem(
                product_id=row[0],
                name=row[1],
                description=row[2],
                current_stock=row[3],
                unit_price=float(row[4]),
                unit=row[5],
                warehouse=row[6],
                category=row[7],
                low_stock_threshold=row[8],
                expiry_date=row[9],
                expiry_status=row[10],
                manufactured_date=row[11],
                batch_number=row[12],
            )
            for row in rows
        ]

        return ProductListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
        )
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load products")
    finally:
        conn.close()


@router.post("", response_model=ProductMutationResponse)
def create_product(
    payload: ProductWriteRequest,
    current_user: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_id = payload.warehouse_id
        if warehouse_scope is not None:
            warehouse_id = warehouse_scope if warehouse_id is None else warehouse_id
            if warehouse_id != warehouse_scope:
                raise HTTPException(status_code=403, detail="Cannot manage another warehouse")
        cur.execute(
            """
            INSERT INTO products
            (name, description, current_stock, unit_price, unit, warehouse_id, category_id,
             low_stock_threshold, expiry_date, manufactured_date, batch_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payload.name,
                payload.description,
                payload.current_stock,
                payload.unit_price,
                payload.unit,
                warehouse_id,
                payload.category_id,
                payload.low_stock_threshold,
                payload.expiry_date,
                payload.manufactured_date,
                payload.batch_number,
            ),
        )
        product_id = cur.lastrowid
        conn.commit()
        cur.close()
        return ProductMutationResponse(
            success=True,
            message=f"Product '{payload.name}' added.",
            product_id=product_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.put("/{product_id}", response_model=ProductMutationResponse)
def update_product(
    product_id: int,
    payload: ProductWriteRequest,
    current_user: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)
        warehouse_id = payload.warehouse_id
        if warehouse_scope is not None:
            warehouse_id = warehouse_scope if warehouse_id is None else warehouse_id
            if warehouse_id != warehouse_scope:
                raise HTTPException(status_code=403, detail="Cannot manage another warehouse")
        cur.execute(
            """
            UPDATE products
            SET name = %s,
                description = %s,
                current_stock = %s,
                unit_price = %s,
                unit = %s,
                warehouse_id = %s,
                category_id = %s,
                low_stock_threshold = %s,
                expiry_date = %s,
                manufactured_date = %s,
                batch_number = %s
            WHERE product_id = %s AND is_deleted = 0
            """,
            (
                payload.name,
                payload.description,
                payload.current_stock,
                payload.unit_price,
                payload.unit,
                warehouse_id,
                payload.category_id,
                payload.low_stock_threshold,
                payload.expiry_date,
                payload.manufactured_date,
                payload.batch_number,
                product_id,
            ),
        )
        affected = cur.rowcount
        conn.commit()
        cur.close()

        if affected == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductMutationResponse(
            success=True,
            message=f"Product #{product_id} updated.",
            product_id=product_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.delete("/{product_id}", response_model=ProductMutationResponse)
def soft_delete_product(
    product_id: int,
    _: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE products SET is_deleted = 1 WHERE product_id = %s AND is_deleted = 0",
            (product_id,),
        )
        affected = cur.rowcount
        conn.commit()
        cur.close()

        if affected == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        return ProductMutationResponse(
            success=True,
            message=f"Product #{product_id} deleted.",
            product_id=product_id,
        )
    except Error as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
