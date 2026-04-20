from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from mysql.connector import Error

from app.api.deps import get_warehouse_scope, require_roles
from app.db.connection import get_connection
from app.schemas.transaction import (
    TransactionListItem,
    TransactionListResponse,
    TransactionMutationResponse,
    TransactionWriteRequest,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _is_expired(expiry_date: date | None) -> bool:
    return expiry_date is not None and expiry_date < date.today()


def _validate_allocation_quantity(allocations, expected_total: int):
    total = sum(int(item.quantity) for item in allocations)
    if total != expected_total:
        raise HTTPException(status_code=400, detail="Allocated batch quantity must match total quantity")


def _upsert_batch_for_stock_in(cur, payload: TransactionWriteRequest):
    batch_number = (payload.batch_number or "").strip() or f"AUTO-{date.today().strftime('%Y%m%d')}-{payload.product_id}"

    if payload.batch_id is not None:
        cur.execute(
            """
            UPDATE product_batches
            SET quantity_on_hand = quantity_on_hand + %s,
                manufactured_date = COALESCE(%s, manufactured_date),
                expiry_date = COALESCE(%s, expiry_date),
                expiry_status = CASE
                    WHEN COALESCE(%s, expiry_date) IS NOT NULL AND COALESCE(%s, expiry_date) < CURDATE() THEN 'Expired'
                    ELSE 'Active'
                END
            WHERE batch_id = %s AND product_id = %s
            """,
            (
                payload.quantity,
                payload.manufactured_date,
                payload.expiry_date,
                payload.expiry_date,
                payload.expiry_date,
                payload.batch_id,
                payload.product_id,
            ),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Batch not found for this product")
        return int(payload.batch_id)

    cur.execute(
        """
        SELECT batch_id
        FROM product_batches
        WHERE product_id = %s
          AND batch_number = %s
          AND (manufactured_date <=> %s)
          AND (expiry_date <=> %s)
        LIMIT 1
        """,
        (
            payload.product_id,
            batch_number,
            payload.manufactured_date,
            payload.expiry_date,
        ),
    )
    existing = cur.fetchone()
    if existing:
        batch_id = int(existing[0])
        cur.execute(
            """
            UPDATE product_batches
            SET quantity_on_hand = quantity_on_hand + %s,
                expiry_status = CASE
                    WHEN expiry_date IS NOT NULL AND expiry_date < CURDATE() THEN 'Expired'
                    ELSE expiry_status
                END
            WHERE batch_id = %s
            """,
            (payload.quantity, batch_id),
        )
        return batch_id

    cur.execute(
        """
        INSERT INTO product_batches
        (product_id, batch_number, manufactured_date, expiry_date, expiry_status, quantity_on_hand)
        VALUES (%s, %s, %s, %s,
                CASE WHEN %s IS NOT NULL AND %s < CURDATE() THEN 'Expired' ELSE 'Active' END,
                %s)
        """,
        (
            payload.product_id,
            batch_number,
            payload.manufactured_date,
            payload.expiry_date,
            payload.expiry_date,
            payload.expiry_date,
            payload.quantity,
        ),
    )
    return int(cur.lastrowid)


def _consume_from_batch(cur, product_id: int, batch_id: int, quantity: int):
    cur.execute(
        """
        SELECT quantity_on_hand, expiry_status, expiry_date
        FROM product_batches
        WHERE batch_id = %s AND product_id = %s
        FOR UPDATE
        """,
        (batch_id, product_id),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Batch #{batch_id} not found")

    available_qty = int(row[0])
    status = str(row[1])
    expiry = row[2]
    if status in {"Disposed", "Quarantined"}:
        raise HTTPException(status_code=400, detail=f"Batch #{batch_id} is not available")
    if _is_expired(expiry):
        raise HTTPException(status_code=400, detail=f"Batch #{batch_id} is expired")
    if available_qty < quantity:
        raise HTTPException(status_code=400, detail=f"Batch #{batch_id} has insufficient quantity")

    cur.execute(
        "UPDATE product_batches SET quantity_on_hand = quantity_on_hand - %s WHERE batch_id = %s",
        (quantity, batch_id),
    )


def _consume_with_explicit_allocations(cur, payload: TransactionWriteRequest):
    allocations = payload.allocations or []
    _validate_allocation_quantity(allocations, payload.quantity)
    consumed: list[tuple[int, int]] = []

    for allocation in allocations:
        if allocation.quantity <= 0:
            raise HTTPException(status_code=400, detail="Allocated quantity must be greater than 0")
        _consume_from_batch(cur, payload.product_id, allocation.batch_id, allocation.quantity)
        consumed.append((allocation.batch_id, allocation.quantity))

    return consumed


def _consume_with_fefo(cur, payload: TransactionWriteRequest):
    remaining = payload.quantity
    consumed: list[tuple[int, int]] = []

    cur.execute(
        """
        SELECT batch_id, quantity_on_hand
        FROM product_batches
        WHERE product_id = %s
          AND quantity_on_hand > 0
          AND expiry_status NOT IN ('Disposed', 'Quarantined')
          AND (expiry_date IS NULL OR expiry_date >= CURDATE())
        ORDER BY CASE WHEN expiry_date IS NULL THEN 1 ELSE 0 END,
                 expiry_date,
                 manufactured_date,
                 batch_id
        FOR UPDATE
        """,
        (payload.product_id,),
    )
    rows = cur.fetchall()

    for row in rows:
        if remaining <= 0:
            break
        batch_id = int(row[0])
        available_qty = int(row[1])
        take_qty = min(available_qty, remaining)
        if take_qty <= 0:
            continue

        cur.execute(
            "UPDATE product_batches SET quantity_on_hand = quantity_on_hand - %s WHERE batch_id = %s",
            (take_qty, batch_id),
        )
        consumed.append((batch_id, take_qty))
        remaining -= take_qty

    if remaining > 0:
        raise HTTPException(
            status_code=400,
            detail="Insufficient non-expired batch stock for FEFO stock-out",
        )

    return consumed


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    warehouse_id: int | None = Query(default=None),
    search: str | None = Query(default=None),
    txn_type: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    current_user: dict = Depends(require_roles("Admin", "Manager")),
):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        warehouse_scope = get_warehouse_scope(current_user)
        effective_warehouse_id = warehouse_scope if warehouse_scope is not None else warehouse_id

        count_query = """
            SELECT COUNT(*)
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE 1=1
        """
        count_params: list[object] = []

        if effective_warehouse_id:
            count_query += " AND t.warehouse_id = %s"
            count_params.append(effective_warehouse_id)
        if search:
            count_query += " AND p.name LIKE %s"
            count_params.append(f"%{search}%")
        if txn_type and txn_type != "All":
            count_query += " AND t.type = %s"
            count_params.append(txn_type)
        if date_from:
            count_query += " AND DATE(t.transaction_date) >= %s"
            count_params.append(date_from)
        if date_to:
            count_query += " AND DATE(t.transaction_date) <= %s"
            count_params.append(date_to)

        cur.execute(count_query, tuple(count_params))
        total = int(cur.fetchone()[0])

        data_query = """
            SELECT t.transaction_id, p.name AS product, t.type, t.quantity,
                   COALESCE(t.unit_cost, p.unit_price) AS unit_cost,
                   ROUND(COALESCE(t.unit_cost, p.unit_price) * t.quantity, 2) AS total_cost,
                   DATE_FORMAT(t.transaction_date, %s),
                   t.remarks,
                   COALESCE(u.username, t.user_id) AS user,
                   COALESCE(w.name, '—') AS warehouse,
                   COALESCE(c.name, '—') AS category,
                   COALESCE(pb.batch_number, p.batch_number, '—') AS batch
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            LEFT JOIN product_batches pb ON t.batch_id = pb.batch_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE 1=1
        """
        data_params: list[object] = ["%Y-%m-%d %H:%i"]

        if effective_warehouse_id:
            data_query += " AND t.warehouse_id = %s"
            data_params.append(effective_warehouse_id)
        if search:
            data_query += " AND p.name LIKE %s"
            data_params.append(f"%{search}%")
        if txn_type and txn_type != "All":
            data_query += " AND t.type = %s"
            data_params.append(txn_type)
        if date_from:
            data_query += " AND DATE(t.transaction_date) >= %s"
            data_params.append(date_from)
        if date_to:
            data_query += " AND DATE(t.transaction_date) <= %s"
            data_params.append(date_to)

        data_query += " ORDER BY t.transaction_date DESC LIMIT %s OFFSET %s"
        data_params.extend([page_size, (page - 1) * page_size])

        cur.execute(data_query, tuple(data_params))
        rows = cur.fetchall()
        cur.close()

        items = [
            TransactionListItem(
                transaction_id=row[0],
                product=row[1],
                type=row[2],
                quantity=row[3],
                unit_cost=float(row[4]) if row[4] is not None else None,
                total_cost=float(row[5]) if row[5] is not None else None,
                transaction_date=row[6],
                remarks=row[7],
                user=str(row[8]),
                warehouse=row[9],
                category=row[10],
                batch=row[11],
            )
            for row in rows
        ]

        return TransactionListResponse(items=items, page=page, page_size=page_size, total=total)
    except Error:
        raise HTTPException(status_code=500, detail="Failed to load transactions")
    finally:
        conn.close()


@router.post("", response_model=TransactionMutationResponse)
def record_transaction(
    payload: TransactionWriteRequest,
    current_user: dict = Depends(require_roles("Admin", "Manager", "Clerk")),
):
    txn_type = payload.type
    if txn_type not in {"Stock-In", "Stock-Out"}:
        raise HTTPException(status_code=400, detail="Invalid transaction type")
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database unavailable")

    try:
        cur = conn.cursor()
        conn.start_transaction()
        warehouse_scope = get_warehouse_scope(current_user)

        warehouse_id = payload.warehouse_id
        if warehouse_scope is not None:
            warehouse_id = warehouse_scope if warehouse_id is None else warehouse_id
            if warehouse_id != warehouse_scope:
                raise HTTPException(status_code=403, detail="Cannot record transactions for another warehouse")

        cur.execute(
            "SELECT current_stock, warehouse_id, unit_price FROM products WHERE product_id = %s AND is_deleted = 0 FOR UPDATE",
            (payload.product_id,),
        )
        product_row = cur.fetchone()
        if not product_row:
            raise HTTPException(status_code=404, detail="Product not found")

        current_stock = int(product_row[0])
        product_warehouse_id = product_row[1]
        current_unit_price = float(product_row[2])

        if warehouse_scope is not None and int(product_warehouse_id) != int(warehouse_scope):
            raise HTTPException(status_code=403, detail="Cannot move stock from another warehouse")

        if txn_type == "Stock-Out" and payload.quantity > current_stock:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        unit_cost = current_unit_price if payload.unit_price is None else float(payload.unit_price)

        transaction_id = None
        if txn_type == "Stock-In":
            stock_in_batch_id = None
            has_batch_input = bool(payload.batch_id) or bool((payload.batch_number or "").strip()) or payload.expiry_date is not None or payload.manufactured_date is not None
            if has_batch_input:
                stock_in_batch_id = _upsert_batch_for_stock_in(cur, payload)

            cur.execute(
                """
                INSERT INTO transactions
                (product_id, user_id, warehouse_id, type, quantity, unit_cost, remarks, batch_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.product_id,
                    current_user["user_id"],
                    warehouse_id,
                    txn_type,
                    payload.quantity,
                    unit_cost,
                    payload.remarks,
                    stock_in_batch_id,
                ),
            )
            transaction_id = int(cur.lastrowid)

            cur.execute(
                "UPDATE products SET current_stock = current_stock + %s WHERE product_id = %s",
                (payload.quantity, payload.product_id),
            )
            if payload.unit_price is not None:
                cur.execute(
                    "UPDATE products SET unit_price = %s WHERE product_id = %s",
                    (payload.unit_price, payload.product_id),
                )
        else:
            consumed_batches: list[tuple[int, int]] = []
            if payload.allocations:
                consumed_batches = _consume_with_explicit_allocations(cur, payload)
            elif payload.batch_id is not None:
                _consume_from_batch(cur, payload.product_id, int(payload.batch_id), payload.quantity)
                consumed_batches = [(int(payload.batch_id), payload.quantity)]
            else:
                consumed_batches = _consume_with_fefo(cur, payload)

            if consumed_batches:
                for batch_id, batch_qty in consumed_batches:
                    cur.execute(
                        """
                        INSERT INTO transactions
                        (product_id, user_id, warehouse_id, type, quantity, unit_cost, remarks, batch_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            payload.product_id,
                            current_user["user_id"],
                            warehouse_id,
                            txn_type,
                            batch_qty,
                            current_unit_price,
                            payload.remarks,
                            batch_id,
                        ),
                    )
                    transaction_id = int(cur.lastrowid)
            else:
                cur.execute(
                    """
                    INSERT INTO transactions
                    (product_id, user_id, warehouse_id, type, quantity, unit_cost, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        payload.product_id,
                        current_user["user_id"],
                        warehouse_id,
                        txn_type,
                        payload.quantity,
                        current_unit_price,
                        payload.remarks,
                    ),
                )
                transaction_id = int(cur.lastrowid)

            cur.execute(
                "UPDATE products SET current_stock = current_stock - %s WHERE product_id = %s",
                (payload.quantity, payload.product_id),
            )

        conn.commit()
        cur.close()
        return TransactionMutationResponse(
            success=True,
            message=f"{txn_type} of {payload.quantity} unit(s) recorded successfully.",
            transaction_id=transaction_id,
        )
    except HTTPException:
        conn.rollback()
        raise
    except Error as exc:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()
