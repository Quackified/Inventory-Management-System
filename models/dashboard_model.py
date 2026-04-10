"""
dashboard_model.py — Database operations for the dashboard summary.
"""

from database import get_connection, close_connection
from mysql.connector import Error
from datetime import date


def get_summary():
    """
    Fetch aggregate stats for the dashboard cards.

    Returns:
        dict: {'total_products': int, 'low_stock': int, 'txn_today': int}
    """
    stats = {"total_products": 0, "low_stock": 0, "txn_today": 0}

    conn = get_connection()
    if not conn:
        return stats
    try:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM products")
        stats["total_products"] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM products WHERE current_stock < 10")
        stats["low_stock"] = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE DATE(transaction_date) = %s",
            (date.today(),)
        )
        stats["txn_today"] = cur.fetchone()[0]

        cur.close()
    except Error as e:
        print(f"[DashboardModel] Stats error: {e}")
    finally:
        close_connection(conn)

    return stats


def get_recent_transactions(limit=10):
    """
    Fetch the most recent transactions for the dashboard table.

    Returns:
        list[tuple]: Rows of (id, product_name, type, qty, date, user_id).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.transaction_id, p.name, t.type, t.quantity,
                   DATE_FORMAT(t.transaction_date, '%%Y-%%m-%%d'), t.user_id
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            ORDER BY t.transaction_date DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[DashboardModel] Recent txn error: {e}")
        return []
    finally:
        close_connection(conn)
