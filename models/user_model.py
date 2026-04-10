"""
user_model.py — Database operations for user authentication.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def authenticate(username, password):
    """
    Validate user credentials against the database.

    For now uses a simple plaintext check (dummy).
    In production, use hashed passwords.

    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.

    Returns:
        dict: User info {'user_id', 'username', 'role'} on success, or None.
    """
    # --- Dummy credential check (no DB call) ---
    # Replace this block with the DB query below once you have
    # real hashed passwords in the users table.
    if username == "admin" and password == "password":
        return {"user_id": 1, "username": username, "role": "Admin"}
    return None

    # --- Future: real DB authentication ---
    # conn = get_connection()
    # if not conn:
    #     return None
    # try:
    #     cur = conn.cursor(dictionary=True)
    #     cur.execute(
    #         "SELECT user_id, username, full_name, role "
    #         "FROM users WHERE username = %s AND password_hash = %s",
    #         (username, password)
    #     )
    #     user = cur.fetchone()
    #     cur.close()
    #     return user
    # except Error as e:
    #     print(f"[UserModel] Auth error: {e}")
    #     return None
    # finally:
    #     close_connection(conn)
