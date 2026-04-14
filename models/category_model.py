"""
category_model.py — Database operations for category management.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def get_all():
    """
    Fetch all categories.

    Returns:
        list[tuple]: Rows of (category_id, name, description).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT category_id, name, description "
            "FROM categories ORDER BY name"
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[CategoryModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def add(name, description):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO categories (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()
        cur.close()
        return True, f"Category '{name}' added."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def update(category_id, name, description):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE categories SET name=%s, description=%s "
            "WHERE category_id=%s",
            (name, description, category_id)
        )
        conn.commit()
        cur.close()
        return True, f"Category #{category_id} updated."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def delete(category_id):
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE category_id=%s",
                    (category_id,))
        conn.commit()
        cur.close()
        return True, f"Category #{category_id} deleted."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)
