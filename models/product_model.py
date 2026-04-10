"""
product_model.py — Database operations for product management.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all(search_term=None):
    """
    Fetch all products, optionally filtered by name.

    Args:
        search_term (str, optional): Filter products whose name contains this.

    Returns:
        list[tuple]: Rows of (product_id, name, description, current_stock, unit).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        if search_term:
            cur.execute(
                "SELECT product_id, name, description, current_stock, unit "
                "FROM products WHERE name LIKE %s ORDER BY product_id",
                (f"%{search_term}%",)
            )
        else:
            cur.execute(
                "SELECT product_id, name, description, current_stock, unit "
                "FROM products ORDER BY product_id"
            )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[ProductModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def add(name, description, stock, unit):
    """
    Insert a new product into the database.

    Args:
        name (str): Product name.
        description (str): Product description.
        stock (int): Initial stock level.
        unit (str): Unit of measurement (e.g. 'pcs').

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products (name, description, current_stock, unit) "
            "VALUES (%s, %s, %s, %s)",
            (name, description, stock, unit)
        )
        conn.commit()
        cur.close()
        return True, f"Product '{name}' added."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def update(product_id, name, description, stock, unit):
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
            "UPDATE products "
            "SET name=%s, description=%s, current_stock=%s, unit=%s "
            "WHERE product_id=%s",
            (name, description, stock, unit, product_id)
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
