"""
transaction_model.py — Database operations for inventory transactions.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all():
    """
    Fetch all transactions joined with product names.

    Returns:
        list[tuple]: Rows of (id, product_name, type, qty, date, remarks, user_id).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT t.transaction_id, p.name, t.type, t.quantity,
                   DATE_FORMAT(t.transaction_date, '%%Y-%%m-%%d %%H:%%i'),
                   t.remarks, t.user_id
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            ORDER BY t.transaction_date DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[TransactionModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def get_products_for_dropdown():
    """
    Fetch product list for the transaction form dropdown.

    Returns:
        list[tuple]: Rows of (product_id, name, current_stock).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT product_id, name, current_stock FROM products ORDER BY name"
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[TransactionModel] Product load error: {e}")
        return []
    finally:
        close_connection(conn)


def get_current_stock(product_id):
    """
    Get the current stock level of a single product.

    Returns:
        int or None: Current stock, or None if not found.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT current_stock FROM products WHERE product_id = %s",
                    (product_id,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None
    except Error as e:
        print(f"[TransactionModel] Stock check error: {e}")
        return None
    finally:
        close_connection(conn)


def record(product_id, user_id, txn_type, quantity, remarks):
    """
    Record a transaction and update the product stock level.

    Args:
        product_id (int): ID of the product.
        user_id (int): ID of the user recording this.
        txn_type (str): 'Stock-In' or 'Stock-Out'.
        quantity (int): Number of units.
        remarks (str): Optional notes.

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
            "(product_id, user_id, type, quantity, remarks) "
            "VALUES (%s, %s, %s, %s, %s)",
            (product_id, user_id, txn_type, quantity, remarks)
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
