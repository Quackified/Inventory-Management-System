"""
dashboard_model.py — Database operations for the dashboard screen.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_summary():
    """
    Fetch summary stats for the dashboard.

    Returns:
        dict: {total_products, total_stock, low_stock_count, expired_count}
    """
    conn = get_connection()
    if not conn:
        return {"total_products": 0, "total_stock": 0,
                "low_stock_count": 0, "expired_count": 0}
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) AS total FROM products")
        total = cur.fetchone()["total"]

        cur.execute("SELECT COALESCE(SUM(current_stock), 0) AS total_stock FROM products")
        total_stock = cur.fetchone()["total_stock"]

        # Low stock: per-product threshold
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM products "
            "WHERE current_stock < low_stock_threshold"
        )
        low_stock = cur.fetchone()["cnt"]

        # Expired count
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM products "
            "WHERE expiry_status = 'Expired'"
        )
        expired = cur.fetchone()["cnt"]

        cur.close()
        return {
            "total_products": total,
            "total_stock": total_stock,
            "low_stock_count": low_stock,
            "expired_count": expired,
        }
    except Error as e:
        print(f"[DashboardModel] Summary error: {e}")
        return {"total_products": 0, "total_stock": 0,
                "low_stock_count": 0, "expired_count": 0}
    finally:
        close_connection(conn)


def get_recent_transactions(limit=10):
    """
    Fetch the most recent transactions with product names.

    Returns:
        list[tuple]: Rows of (id, product_name, type, qty, date).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT t.transaction_id, p.name, t.type, t.quantity,
                   DATE_FORMAT(t.transaction_date, '%Y-%m-%d %H:%i')
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            ORDER BY t.transaction_date DESC
            LIMIT {int(limit)}
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[DashboardModel] Recent txn error: {e}")
        return []
    finally:
        close_connection(conn)
