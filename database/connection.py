"""
connection.py — MySQL connection helper for the Inventory Management System.

Provides a reusable connection helper with basic error handling.

Usage:
    from database import get_connection, close_connection

    conn = get_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        cursor.close()
        close_connection(conn)
"""

import mysql.connector
from mysql.connector import Error


# ── Configuration ────────────────────────────────────────────
# Update these values to match your local MySQL setup.
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",          # ← set your MySQL root/user password here
    "database": "inventory_db",
}


# ── Connection Helper ────────────────────────────────────────
def get_connection():
    """
    Create and return a new MySQL connection using DB_CONFIG.

    Returns:
        mysql.connector.connection.MySQLConnection on success, or None on failure.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[DB] Connection Error: {e}")
        return None


def close_connection(connection):
    """Safely close an existing MySQL connection."""
    if connection and connection.is_connected():
        connection.close()


# ── Quick Verification ───────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Inventory Management System — DB Check")
    print("=" * 50)

    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"[OK] Active database: {db_name[0]}")

            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if tables:
                print(f"[OK] Tables found: {', '.join(t[0] for t in tables)}")
            else:
                print("[!] No tables found — run schema.sql first.")

            cursor.close()
        except Error as e:
            print(f"[ERROR] Query error: {e}")
        finally:
            close_connection(conn)
    else:
        print("[ERROR] Could not establish a database connection.")
        print("    -> Make sure MySQL is running and DB_CONFIG is correct.")
