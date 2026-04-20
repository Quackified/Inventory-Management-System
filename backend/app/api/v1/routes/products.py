from fastapi import APIRouter, Depends, HTTPException, Query
from mysql.connector import Error

from app.api.deps import get_warehouse_scope, require_roles
from app.db.connection import get_connection
from app.schemas.product import (
    BatchActionRequest,
    BatchActionResponse,
    ExpiryActionItem,
    ExpiryActionListResponse,
    ProductBatchItem,
    ProductBatchListResponse,
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
                                     p.expiry_date,
                                     CASE
                                         WHEN p.expiry_date IS NOT NULL AND p.expiry_date < CURDATE() THEN 'Expired'
                                         ELSE 'Active'
                                     END AS expiry_status,
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


@router.get("/batches/expiry-actions", response_model=ExpiryActionListResponse)
def list_expiry_actions(
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)

        query = """
            SELECT pb.batch_id,
                   pb.product_id,
                   p.name,
                   COALESCE(w.name, '—') AS warehouse,
                   pb.batch_number,
                   pb.expiry_date,
                   CASE
                     WHEN pb.expiry_status IN ('Quarantined', 'Disposed') THEN pb.expiry_status
                     WHEN pb.expiry_date IS NOT NULL AND pb.expiry_date < CURDATE() THEN 'Expired'
                     ELSE 'Active'
                   END AS live_status,
                   pb.quantity_on_hand,
                   CASE
                     WHEN pb.expiry_date IS NULL THEN 0
                     WHEN pb.expiry_date < CURDATE() THEN DATEDIFF(CURDATE(), pb.expiry_date)
                     ELSE 0
                   END AS days_overdue
            FROM product_batches pb
            JOIN products p ON p.product_id = pb.product_id AND p.is_deleted = 0
            LEFT JOIN warehouses w ON w.warehouse_id = p.warehouse_id
            WHERE pb.quantity_on_hand > 0
              AND (
                    pb.expiry_status = 'Quarantined'
                    OR (pb.expiry_date IS NOT NULL AND pb.expiry_date < CURDATE())
                  )
        """
        params: list[object] = []
        if warehouse_scope is not None:
            query += " AND p.warehouse_id = %s"
            params.append(warehouse_scope)

        query += " ORDER BY days_overdue DESC, pb.expiry_date, pb.batch_id"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        items = [
            ExpiryActionItem(
                batch_id=row[0],
                product_id=row[1],
                product_name=row[2],
                warehouse=row[3],
                batch_number=row[4],
                expiry_date=row[5],
                expiry_status=row[6],
                quantity_on_hand=row[7],
                days_overdue=int(row[8] or 0),
            )
            for row in rows
        ]
        return ExpiryActionListResponse(items=items)
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load expiry action queue")
    finally:
        conn.close()


@router.post("/batches/{batch_id}/action", response_model=BatchActionResponse)
def handle_batch_action(
    batch_id: int,
    payload: BatchActionRequest,
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        conn.start_transaction()
        warehouse_scope = get_warehouse_scope(current_user)

        cur.execute(
            """
            SELECT pb.batch_id,
                   pb.product_id,
                   pb.quantity_on_hand,
                   pb.expiry_status,
                   pb.batch_number,
                   p.warehouse_id,
                   p.unit_price
            FROM product_batches pb
            JOIN products p ON p.product_id = pb.product_id
            WHERE pb.batch_id = %s
              AND p.is_deleted = 0
            FOR UPDATE
            """,
            (batch_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Batch not found")

        product_id = int(row[1])
        quantity_on_hand = int(row[2])
        current_status = str(row[3])
        batch_number = str(row[4])
        warehouse_id = row[5]
        unit_price = float(row[6])

        if warehouse_scope is not None and int(warehouse_id) != int(warehouse_scope):
            raise HTTPException(status_code=403, detail="Cannot manage another warehouse")

        if payload.action == "Quarantine":
            if current_status == "Disposed":
                raise HTTPException(status_code=400, detail="Disposed batch cannot be quarantined")

            cur.execute(
                "UPDATE product_batches SET expiry_status = 'Quarantined' WHERE batch_id = %s",
                (batch_id,),
            )
            conn.commit()
            cur.close()
            return BatchActionResponse(
                success=True,
                message=f"Batch {batch_number} moved to quarantine.",
                batch_id=batch_id,
                product_id=product_id,
                quantity_disposed=0,
            )

        if quantity_on_hand <= 0:
            raise HTTPException(status_code=400, detail="Batch has no quantity to dispose")

        cur.execute(
            """
            UPDATE product_batches
            SET expiry_status = 'Disposed',
                quantity_on_hand = 0
            WHERE batch_id = %s
            """,
            (batch_id,),
        )
        cur.execute(
            """
            UPDATE products
            SET current_stock = GREATEST(current_stock - %s, 0)
            WHERE product_id = %s
            """,
            (quantity_on_hand, product_id),
        )
        cur.execute(
            """
            INSERT INTO transactions
            (product_id, user_id, warehouse_id, type, quantity, unit_cost, remarks, batch_id)
            VALUES (%s, %s, %s, 'Stock-Out', %s, %s, %s, %s)
            """,
            (
                product_id,
                current_user["user_id"],
                warehouse_id,
                quantity_on_hand,
                unit_price,
                payload.remarks or f"Disposed expired/quarantined batch {batch_number}",
                batch_id,
            ),
        )

        conn.commit()
        cur.close()
        return BatchActionResponse(
            success=True,
            message=f"Batch {batch_number} disposed ({quantity_on_hand} unit(s)).",
            batch_id=batch_id,
            product_id=product_id,
            quantity_disposed=quantity_on_hand,
        )
    except HTTPException:
        conn.rollback()
        raise
    except Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.get("/{product_id}/batches", response_model=ProductBatchListResponse)
def list_product_batches(
    product_id: int,
    only_available: bool = Query(default=True),
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)
        cur.execute(
            """
            SELECT p.product_id
            FROM products p
            WHERE p.product_id = %s AND p.is_deleted = 0
            """
            + (" AND p.warehouse_id = %s" if warehouse_scope is not None else ""),
            (product_id, warehouse_scope) if warehouse_scope is not None else (product_id,),
        )
        target_product = cur.fetchone()
        if not target_product:
            raise HTTPException(status_code=404, detail="Product not found")

        query = """
            SELECT pb.batch_id,
                   pb.product_id,
                   pb.batch_number,
                   pb.manufactured_date,
                   pb.expiry_date,
                   CASE
                     WHEN pb.expiry_status IN ('Quarantined', 'Disposed') THEN pb.expiry_status
                     WHEN pb.expiry_date IS NOT NULL AND pb.expiry_date < CURDATE() THEN 'Expired'
                     ELSE 'Active'
                   END AS live_status,
                   pb.quantity_on_hand
            FROM product_batches pb
            WHERE pb.product_id = %s
        """
        params: list[object] = [product_id]
        if only_available:
            query += " AND pb.quantity_on_hand > 0"

        query += " ORDER BY CASE WHEN pb.expiry_date IS NULL THEN 1 ELSE 0 END, pb.expiry_date, pb.manufactured_date, pb.batch_id"
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()

        items = [
            ProductBatchItem(
                batch_id=row[0],
                product_id=row[1],
                batch_number=row[2],
                manufactured_date=row[3],
                expiry_date=row[4],
                expiry_status=row[5],
                quantity_on_hand=row[6],
            )
            for row in rows
        ]
        return ProductBatchListResponse(items=items)
    except HTTPException:
        raise
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load product batches")
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
