"""
warehouse_model.py — Database operations for warehouse management.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all():
    """
    Fetch all warehouses.

    Returns:
        list[tuple]: Rows of (warehouse_id, name, location, is_active).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT warehouse_id, name, location, is_active "
            "FROM warehouses ORDER BY name"
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[WarehouseModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def get_all_active():
    """Fetch only active warehouses (for dropdowns)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT warehouse_id, name FROM warehouses "
            "WHERE is_active = 1 ORDER BY name"
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[WarehouseModel] Active load error: {e}")
        return []
    finally:
        close_connection(conn)


def add(name, location):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO warehouses (name, location) VALUES (%s, %s)",
            (name, location)
        )
        conn.commit()
        cur.close()
        return True, f"Warehouse '{name}' added."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def update(warehouse_id, name, location, is_active):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE warehouses SET name=%s, location=%s, is_active=%s "
            "WHERE warehouse_id=%s",
            (name, location, is_active, warehouse_id)
        )
        conn.commit()
        cur.close()
        return True, f"Warehouse #{warehouse_id} updated."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def delete(warehouse_id):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM warehouses WHERE warehouse_id=%s",
                    (warehouse_id,))
        conn.commit()
        cur.close()
        return True, f"Warehouse #{warehouse_id} deleted."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)
