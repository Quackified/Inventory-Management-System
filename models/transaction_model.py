"""
transaction_model.py — Database operations for inventory transactions.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all(warehouse_id=None, search_term=None, txn_type=None,
            date_from=None, date_to=None, page=None, page_size=None):
    """
    Fetch transactions with optional filters and pagination.

    Args:
        warehouse_id (int, optional): Filter by warehouse.
        search_term (str, optional): Filter by product name.
        txn_type (str, optional): 'Stock-In' or 'Stock-Out'.
        date_from (str, optional): Start date (YYYY-MM-DD).
        date_to (str, optional): End date (YYYY-MM-DD).
        page (int, optional): 1-based page number.
        page_size (int, optional): Rows per page.

    Returns:
        list[tuple]: Rows of (id, product_name, type, qty, date, remarks,
                     username, warehouse_name, category_name, batch).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        query = """
            SELECT t.transaction_id, p.name AS product, t.type, t.quantity,
                   DATE_FORMAT(t.transaction_date, %s),
                   t.remarks,
                   COALESCE(u.username, t.user_id) AS user,
                   COALESCE(w.name, '—') AS warehouse,
                   COALESCE(c.name, '—') AS category,
                   COALESCE(p.batch_number, '—') AS batch
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE 1=1
        """
        params = ["%Y-%m-%d %H:%i"]

        if warehouse_id:
            query += " AND t.warehouse_id = %s"
            params.append(warehouse_id)

        if search_term:
            query += " AND p.name LIKE %s"
            params.append(f"%{search_term}%")

        if txn_type and txn_type != "All":
            query += " AND t.type = %s"
            params.append(txn_type)

        if date_from:
            query += " AND DATE(t.transaction_date) >= %s"
            params.append(date_from)

        if date_to:
            query += " AND DATE(t.transaction_date) <= %s"
            params.append(date_to)

        query += " ORDER BY t.transaction_date DESC"

        if page and page_size:
            query += " LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])
        else:
            query += " LIMIT 500"

        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[TransactionModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def get_total_count(warehouse_id=None, search_term=None, txn_type=None,
                    date_from=None, date_to=None):
    """
    Count total transactions matching filters (for pagination).

    Returns:
        int: Total matching row count.
    """
    conn = get_connection()
    if not conn:
        return 0
    try:
        cur = conn.cursor()
        query = """
            SELECT COUNT(*)
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            WHERE 1=1
        """
        params = []

        if warehouse_id:
            query += " AND t.warehouse_id = %s"
            params.append(warehouse_id)

        if search_term:
            query += " AND p.name LIKE %s"
            params.append(f"%{search_term}%")

        if txn_type and txn_type != "All":
            query += " AND t.type = %s"
            params.append(txn_type)

        if date_from:
            query += " AND DATE(t.transaction_date) >= %s"
            params.append(date_from)

        if date_to:
            query += " AND DATE(t.transaction_date) <= %s"
            params.append(date_to)

        cur.execute(query, tuple(params))
        count = cur.fetchone()[0]
        cur.close()
        return count
    except Error as e:
        print(f"[TransactionModel] Count error: {e}")
        return 0
    finally:
        close_connection(conn)


def record(product_id, user_id, txn_type, quantity, remarks,
           warehouse_id=None):
    """
    Record a transaction and update the product stock level.

    Args:
        product_id (int): ID of the product.
        user_id (int): ID of the user recording this.
        txn_type (str): 'Stock-In' or 'Stock-Out'.
        quantity (int): Number of units.
        remarks (str): Optional notes.
        warehouse_id (int, optional): Warehouse for this transaction.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()

        # 1) Insert the transaction record
        cur.execute(
            "INSERT INTO transactions "
            "(product_id, user_id, warehouse_id, type, quantity, remarks) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (product_id, user_id, warehouse_id, txn_type, quantity, remarks)
        )

        # 2) Update product stock level
        if txn_type == "Stock-In":
            cur.execute(
                "UPDATE products SET current_stock = current_stock + %s "
                "WHERE product_id = %s",
                (quantity, product_id)
            )
        else:
            cur.execute(
                "UPDATE products SET current_stock = current_stock - %s "
                "WHERE product_id = %s",
                (quantity, product_id)
            )

        conn.commit()
        cur.close()
        return True, f"{txn_type} of {quantity} unit(s) recorded successfully."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)
