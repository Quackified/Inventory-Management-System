"""
database.py — Database connection module for Inventory Management System.

Provides a reusable MySQL connection helper with basic error handling
and a lightweight context-manager wrapper for safe cursor usage.

Usage:
    from database import get_connection

    conn = get_connection()
    if conn and conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
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
            server_info = connection.get_server_info()
            print(f"[✔] Connected to MySQL Server version {server_info}")
            print(f"[✔] Database: {DB_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"[✖] MySQL Connection Error: {e}")
        return None


def close_connection(connection):
    """Safely close an existing MySQL connection."""
    if connection and connection.is_connected():
        connection.close()
        print("[✔] MySQL connection closed.")


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
            print(f"[✔] Active database: {db_name[0]}")

            # List existing tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if tables:
                print(f"[✔] Tables found: {', '.join(t[0] for t in tables)}")
            else:
                print("[!] No tables found — run schema.sql first.")

            cursor.close()
        except Error as e:
            print(f"[✖] Query error: {e}")
        finally:
            close_connection(conn)
    else:
        print("[✖] Could not establish a database connection.")
        print("    → Make sure MySQL is running and DB_CONFIG is correct.")
