"""
product_model.py — Database operations for product management.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all(search_term=None):
    """
    Fetch all products with warehouse and category names.

    Args:
        search_term (str, optional): Filter by product name.

    Returns:
        list[tuple]: Rows of (product_id, name, description, current_stock,
                     unit, warehouse_name, category_name, low_stock_threshold,
                     expiry_date, expiry_status, manufactured_date, batch_number).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        base = """
            SELECT p.product_id, p.name, p.description, p.current_stock,
                   p.unit,
                   COALESCE(w.name, '—') AS warehouse,
                   COALESCE(c.name, '—') AS category,
                   p.low_stock_threshold,
                   p.expiry_date, p.expiry_status,
                   p.manufactured_date, p.batch_number
            FROM products p
            LEFT JOIN warehouses w ON p.warehouse_id = w.warehouse_id
            LEFT JOIN categories c ON p.category_id = c.category_id
        """
        if search_term:
            base += " WHERE p.name LIKE %s"
            base += " ORDER BY p.product_id"
            cur.execute(base, (f"%{search_term}%",))
        else:
            base += " ORDER BY p.product_id"
            cur.execute(base)

        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[ProductModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def get_by_id(product_id):
    """Fetch a single product by ID (dictionary result)."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM products WHERE product_id = %s",
                    (product_id,))
        row = cur.fetchone()
        cur.close()
        return row
    except Error as e:
        print(f"[ProductModel] Get by ID error: {e}")
        return None
    finally:
        close_connection(conn)


def add(name, description, stock, unit, warehouse_id=None, category_id=None,
        low_stock_threshold=10, expiry_date=None, manufactured_date=None,
        batch_number=None):
    """
    Insert a new product.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products "
            "(name, description, current_stock, unit, warehouse_id, category_id, "
            " low_stock_threshold, expiry_date, manufactured_date, batch_number) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (name, description, stock, unit,
             warehouse_id or None, category_id or None,
             low_stock_threshold,
             expiry_date or None, manufactured_date or None,
             batch_number or None)
        )
        conn.commit()
        cur.close()
        return True, f"Product '{name}' added."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def update(product_id, name, description, stock, unit,
           warehouse_id=None, category_id=None, low_stock_threshold=10,
           expiry_date=None, manufactured_date=None, batch_number=None):
    """
    Update an existing product.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE products SET name=%s, description=%s, current_stock=%s, "
            "unit=%s, warehouse_id=%s, category_id=%s, low_stock_threshold=%s, "
            "expiry_date=%s, manufactured_date=%s, batch_number=%s "
            "WHERE product_id=%s",
            (name, description, stock, unit,
             warehouse_id or None, category_id or None,
             low_stock_threshold,
             expiry_date or None, manufactured_date or None,
             batch_number or None, product_id)
        )
        conn.commit()
        cur.close()
        return True, f"Product #{product_id} updated."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def delete(product_id):
    """
    Delete a product by ID.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE product_id=%s",
                    (product_id,))
        conn.commit()
        cur.close()
        return True, f"Product #{product_id} deleted."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def check_expired():
    """
    Auto-set expiry_status='Expired' for products whose expiry_date <= today.
    Called on app startup.
    """
    conn = get_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE products SET expiry_status='Expired' "
            "WHERE expiry_date IS NOT NULL "
            "AND expiry_date <= CURDATE() "
            "AND expiry_status = 'Active'"
        )
        affected = cur.rowcount
        conn.commit()
        cur.close()
        if affected > 0:
            print(f"[ProductModel] Marked {affected} product(s) as Expired.")
    except Error as e:
        print(f"[ProductModel] Expiry check error: {e}")
    finally:
        close_connection(conn)


def get_current_stock(product_id):
    """Get the current stock level of a single product."""
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
        print(f"[ProductModel] Stock check error: {e}")
        return None
    finally:
        close_connection(conn)
