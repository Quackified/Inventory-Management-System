"""
user_model.py — Database operations for user authentication and account management.
"""

from database import get_connection, close_connection
from mysql.connector import Error


def authenticate(username, password):
    """
    Validate user credentials against the users table in the database.

    Args:
        username (str): The username entered by the user.
        password (str): The password entered by the user.

    Returns:
        dict: User info {'user_id', 'username', 'full_name', 'role'} on success,
              or None on failure.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT user_id, username, full_name, role "
            "FROM users WHERE username = %s AND password_hash = %s",
            (username, password)
        )
        user = cur.fetchone()
        cur.close()
        return user
    except Error as e:
        print(f"[UserModel] Auth error: {e}")
        return None
    finally:
        close_connection(conn)


def get_all():
    """
    Fetch all user accounts.

    Returns:
        list[tuple]: Rows of (user_id, username, full_name, role).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, full_name, role "
            "FROM users ORDER BY user_id"
        )
        rows = cur.fetchall()
        cur.close()
        return rows
    except Error as e:
        print(f"[UserModel] Load error: {e}")
        return []
    finally:
        close_connection(conn)


def add(username, password_hash, full_name, role):
    """
    Insert a new user account.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) "
            "VALUES (%s, %s, %s, %s)",
            (username, password_hash, full_name, role)
        )
        conn.commit()
        cur.close()
        return True, f"User '{username}' added."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def update(user_id, username, full_name, role, password_hash=None):
    """
    Update an existing user account. If password_hash is provided,
    update the password too.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        if password_hash:
            cur.execute(
                "UPDATE users SET username=%s, full_name=%s, role=%s, "
                "password_hash=%s WHERE user_id=%s",
                (username, full_name, role, password_hash, user_id)
            )
        else:
            cur.execute(
                "UPDATE users SET username=%s, full_name=%s, role=%s "
                "WHERE user_id=%s",
                (username, full_name, role, user_id)
            )
        conn.commit()
        cur.close()
        return True, f"User #{user_id} updated."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)


def delete(user_id):
    """
    Delete a user by ID.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    if not conn:
        return False, "Could not connect to the database."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        cur.close()
        return True, f"User #{user_id} deleted."
    except Error as e:
        return False, str(e)
    finally:
        close_connection(conn)
