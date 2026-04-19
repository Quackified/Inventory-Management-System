from mysql.connector import Error, connect

from app.core.config import settings


def get_connection():
    return connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        autocommit=False,
    )


def check_db_connection() -> bool:
    conn = None
    try:
        conn = get_connection()
        return conn.is_connected()
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def ensure_user_profile_columns() -> bool:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'profile_image_url'
            """
        )
        has_profile_image_url = int(cur.fetchone()[0]) > 0
        if not has_profile_image_url:
            cur.execute("ALTER TABLE users ADD COLUMN profile_image_url VARCHAR(255) NULL AFTER email")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND COLUMN_NAME = 'assigned_warehouse_id'
            """
        )
        has_assigned_warehouse_id = int(cur.fetchone()[0]) > 0
        if not has_assigned_warehouse_id:
            cur.execute("ALTER TABLE users ADD COLUMN assigned_warehouse_id INT NULL AFTER profile_image_url")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'users'
              AND INDEX_NAME = 'idx_users_assigned_warehouse'
            """
        )
        has_warehouse_index = int(cur.fetchone()[0]) > 0
        if not has_warehouse_index:
            cur.execute("CREATE INDEX idx_users_assigned_warehouse ON users (assigned_warehouse_id)")

        conn.commit()
        cur.close()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def ensure_transaction_cost_column() -> bool:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND COLUMN_NAME = 'unit_cost'
            """
        )
        has_unit_cost = int(cur.fetchone()[0]) > 0
        if not has_unit_cost:
            cur.execute("ALTER TABLE transactions ADD COLUMN unit_cost DECIMAL(10,2) NULL AFTER quantity")

        conn.commit()
        cur.close()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()
