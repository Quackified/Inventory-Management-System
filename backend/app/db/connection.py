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


def ensure_transaction_warehouse_support() -> bool:
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
              AND COLUMN_NAME = 'warehouse_id'
            """
        )
        has_warehouse_column = int(cur.fetchone()[0]) > 0
        if not has_warehouse_column:
            cur.execute("ALTER TABLE transactions ADD COLUMN warehouse_id INT NULL AFTER user_id")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND INDEX_NAME = 'idx_txn_warehouse'
            """
        )
        has_warehouse_index = int(cur.fetchone()[0]) > 0
        if not has_warehouse_index:
            cur.execute("CREATE INDEX idx_txn_warehouse ON transactions (warehouse_id)")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND COLUMN_NAME = 'warehouse_id'
              AND REFERENCED_TABLE_NAME = 'warehouses'
            """
        )
        has_warehouse_fk = int(cur.fetchone()[0]) > 0
        if not has_warehouse_fk:
            cur.execute(
                """
                ALTER TABLE transactions
                ADD CONSTRAINT fk_txn_warehouse
                FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
                """
            )

        conn.commit()
        cur.close()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def ensure_batch_tracking_support() -> bool:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'product_batches'
            """
        )
        has_batch_table = int(cur.fetchone()[0]) > 0
        if not has_batch_table:
            cur.execute(
                """
                CREATE TABLE product_batches (
                    batch_id           INT AUTO_INCREMENT,
                    product_id         INT NOT NULL,
                    batch_number       VARCHAR(100) NOT NULL,
                    manufactured_date  DATE NULL,
                    expiry_date        DATE NULL,
                    expiry_status      ENUM('Active','Expired','Quarantined','Disposed') NOT NULL DEFAULT 'Active',
                    quantity_on_hand   INT NOT NULL DEFAULT 0,
                    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (batch_id),
                    CONSTRAINT chk_batch_quantity_non_negative CHECK (quantity_on_hand >= 0),
                    CONSTRAINT fk_batch_product
                        FOREIGN KEY (product_id) REFERENCES products (product_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                    UNIQUE KEY uq_batch_identity (product_id, batch_number, manufactured_date, expiry_date),
                    INDEX idx_batch_product (product_id),
                    INDEX idx_batch_expiry (expiry_date)
                ) ENGINE=InnoDB
                """
            )

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND COLUMN_NAME = 'batch_id'
            """
        )
        has_batch_id_column = int(cur.fetchone()[0]) > 0
        if not has_batch_id_column:
            cur.execute("ALTER TABLE transactions ADD COLUMN batch_id INT NULL AFTER remarks")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND INDEX_NAME = 'idx_txn_batch'
            """
        )
        has_batch_index = int(cur.fetchone()[0]) > 0
        if not has_batch_index:
            cur.execute("CREATE INDEX idx_txn_batch ON transactions (batch_id)")

        cur.execute(
            """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'transactions'
              AND COLUMN_NAME = 'batch_id'
              AND REFERENCED_TABLE_NAME = 'product_batches'
            """
        )
        has_batch_fk = int(cur.fetchone()[0]) > 0
        if not has_batch_fk:
            cur.execute(
                """
                ALTER TABLE transactions
                ADD CONSTRAINT fk_txn_batch
                FOREIGN KEY (batch_id) REFERENCES product_batches (batch_id)
                ON UPDATE CASCADE
                ON DELETE SET NULL
                """
            )

        conn.commit()
        cur.close()
        return True
    except Error:
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()


def recalculate_product_summary(cur, product_id: int) -> None:
    cur.execute(
        """
        UPDATE products p
        LEFT JOIN (
            SELECT
                product_id,
                SUM(quantity_on_hand) AS total_stock,
                SUM(
                    CASE
                        WHEN expiry_status = 'Active'
                             AND (expiry_date IS NULL OR expiry_date > CURDATE()) THEN 1
                        ELSE 0
                    END
                ) AS active_batches,
                SUM(
                    CASE
                        WHEN expiry_status = 'Expired'
                             OR (expiry_date IS NOT NULL AND expiry_date <= CURDATE()) THEN 1
                        ELSE 0
                    END
                ) AS expired_batches,
                SUM(CASE WHEN expiry_status = 'Quarantined' THEN 1 ELSE 0 END) AS quarantined_batches,
                SUM(CASE WHEN expiry_status = 'Disposed' THEN 1 ELSE 0 END) AS disposed_batches,
                MIN(
                    CASE
                        WHEN expiry_status <> 'Disposed'
                             AND quantity_on_hand > 0
                             AND (expiry_date IS NULL OR expiry_date > CURDATE()) THEN expiry_date
                    END
                ) AS next_expiry_date,
                SUBSTRING_INDEX(
                    GROUP_CONCAT(
                        CASE
                            WHEN expiry_status <> 'Disposed'
                                 AND quantity_on_hand > 0
                                 AND (expiry_date IS NULL OR expiry_date > CURDATE()) THEN batch_number
                        END
                        ORDER BY CASE WHEN expiry_date IS NULL THEN 1 ELSE 0 END, expiry_date, batch_id
                        SEPARATOR ','
                    ),
                    ',',
                    1
                ) AS primary_batch_number
            FROM product_batches
            WHERE product_id = %s
            GROUP BY product_id
        ) batch_stats ON batch_stats.product_id = p.product_id
        SET p.current_stock = COALESCE(batch_stats.total_stock, 0),
            p.expiry_date = batch_stats.next_expiry_date,
            p.batch_number = batch_stats.primary_batch_number,
            p.expiry_status = CASE
                WHEN COALESCE(batch_stats.total_stock, 0) <= 0
                     AND COALESCE(batch_stats.disposed_batches, 0) > 0 THEN 'Disposed'
                WHEN COALESCE(batch_stats.active_batches, 0) > 0
                     AND (
                         COALESCE(batch_stats.expired_batches, 0) > 0
                         OR COALESCE(batch_stats.quarantined_batches, 0) > 0
                         OR COALESCE(batch_stats.disposed_batches, 0) > 0
                     ) THEN 'At Risk'
                WHEN COALESCE(batch_stats.active_batches, 0) > 0 THEN 'Active'
                WHEN COALESCE(batch_stats.quarantined_batches, 0) > 0
                     AND COALESCE(batch_stats.active_batches, 0) = 0 THEN 'Quarantined'
                WHEN COALESCE(batch_stats.expired_batches, 0) > 0
                     AND COALESCE(batch_stats.active_batches, 0) = 0 THEN 'Expired'
                ELSE 'Active'
            END
        WHERE p.product_id = %s
        """,
        (product_id, product_id),
    )


def recalculate_all_product_summaries(cur) -> None:
    cur.execute("SELECT product_id FROM products WHERE is_deleted = 0")
    product_ids = [int(row[0]) for row in cur.fetchall()]
    for product_id in product_ids:
        recalculate_product_summary(cur, product_id)
