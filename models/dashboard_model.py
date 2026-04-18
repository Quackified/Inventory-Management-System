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

        cur.execute("SELECT COUNT(*) AS total FROM products WHERE is_deleted = 0")
        total = cur.fetchone()["total"]

        cur.execute("SELECT COALESCE(SUM(current_stock), 0) AS total_stock FROM products WHERE is_deleted = 0")
        total_stock = cur.fetchone()["total_stock"]

        # Low stock: per-product threshold
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM products "
            "WHERE current_stock < low_stock_threshold AND is_deleted = 0"
        )
        low_stock = cur.fetchone()["cnt"]

        # Expired count
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM products "
            "WHERE expiry_status = 'Expired' AND is_deleted = 0"
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


def get_warehouse_summary():
    """
    Per-warehouse tally for the dashboard warehouse panel.

    Returns:
        list[dict]: [{name, product_count, total_stock, expired_count, low_stock_count}]
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT w.name,
                   COUNT(p.product_id) AS product_count,
                   COALESCE(SUM(p.current_stock), 0) AS total_stock,
                   SUM(CASE WHEN p.expiry_status = 'Expired' THEN 1 ELSE 0 END) AS expired_count,
                   SUM(CASE WHEN p.current_stock < p.low_stock_threshold THEN 1 ELSE 0 END) AS low_stock_count
            FROM warehouses w
            LEFT JOIN products p ON w.warehouse_id = p.warehouse_id AND p.is_deleted = 0
            WHERE w.is_active = 1
            GROUP BY w.warehouse_id, w.name
            ORDER BY w.name
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[DashboardModel] Warehouse summary error: {e}")
        return []
    finally:
        close_connection(conn)


def get_chart_data(period="weekly"):
    """
    Transaction volume by day for the analytics bar chart.

    Args:
        period: 'weekly' (last 7 days) or 'monthly' (last 30 days).

    Returns:
        list[dict]: [{label, stock_in, stock_out}]
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        days = 7 if period == "weekly" else 30
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT DATE(transaction_date) AS day,
                   DAYNAME(DATE(transaction_date)) AS day_name,
                   SUM(CASE WHEN type = 'Stock-In' THEN quantity ELSE 0 END) AS stock_in,
                   SUM(CASE WHEN type = 'Stock-Out' THEN quantity ELSE 0 END) AS stock_out
            FROM transactions
            WHERE transaction_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(transaction_date), DAYNAME(DATE(transaction_date))
            ORDER BY day
        """, (days,))
        rows = cur.fetchall()
        cur.close()

        result = []
        for row in rows:
            if period == "weekly":
                label = row["day_name"][:3]  # Mon, Tue, ...
            else:
                label = str(row["day"].day)  # Day number
            result.append({
                "label": label,
                "stock_in": int(row["stock_in"]),
                "stock_out": int(row["stock_out"]),
            })
        return result
    except Error as e:
        print(f"[DashboardModel] Chart data error: {e}")
        return []
    finally:
        close_connection(conn)
