-- ============================================================
-- Inventory Management System — Migration v2
-- Run this on an existing inventory_db to add:
--   - warehouses table
--   - categories table
--   - new columns on products (warehouse, category, metadata, expiry)
--   - warehouse_id on transactions
-- ============================================================

USE inventory_db;

-- ============================================================
-- 4. WAREHOUSES (parent entity)
-- ============================================================
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id   INT            AUTO_INCREMENT,
    name           VARCHAR(120)   NOT NULL UNIQUE,
    location       VARCHAR(255)   NULL,
    is_active      TINYINT(1)     NOT NULL DEFAULT 1,
    created_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (warehouse_id)
) ENGINE=InnoDB;

-- ============================================================
-- 5. CATEGORIES (product type grouping)
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    category_id    INT            AUTO_INCREMENT,
    name           VARCHAR(120)   NOT NULL UNIQUE,
    description    TEXT           NULL,
    created_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (category_id)
) ENGINE=InnoDB;

-- ============================================================
-- ALTER products — add warehouse, category, metadata columns
-- ============================================================
-- Each ALTER is wrapped so re-running won't fail if column exists.

-- warehouse_id
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'warehouse_id');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN warehouse_id INT NULL AFTER unit',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- category_id
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'category_id');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN category_id INT NULL AFTER warehouse_id',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- low_stock_threshold
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'low_stock_threshold');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN low_stock_threshold INT NOT NULL DEFAULT 10 AFTER category_id',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- expiry_date
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'expiry_date');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN expiry_date DATE NULL AFTER low_stock_threshold',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- expiry_status
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'expiry_status');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN expiry_status ENUM(''Active'',''Expired'') NOT NULL DEFAULT ''Active'' AFTER expiry_date',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- manufactured_date
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'manufactured_date');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN manufactured_date DATE NULL AFTER expiry_status',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- batch_number
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND COLUMN_NAME = 'batch_number');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE products ADD COLUMN batch_number VARCHAR(100) NULL AFTER manufactured_date',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Foreign keys for products (only if not existing)
SET @fk_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND CONSTRAINT_NAME = 'fk_product_warehouse');
SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE products ADD CONSTRAINT fk_product_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @fk_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'products' AND CONSTRAINT_NAME = 'fk_product_category');
SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE products ADD CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(category_id)',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ============================================================
-- ALTER transactions — add warehouse_id
-- ============================================================
SET @col_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'transactions' AND COLUMN_NAME = 'warehouse_id');
SET @sql = IF(@col_exists = 0,
    'ALTER TABLE transactions ADD COLUMN warehouse_id INT NULL AFTER user_id',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @fk_exists = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_SCHEMA = 'inventory_db' AND TABLE_NAME = 'transactions' AND CONSTRAINT_NAME = 'fk_txn_warehouse');
SET @sql = IF(@fk_exists = 0,
    'ALTER TABLE transactions ADD CONSTRAINT fk_txn_warehouse FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Done
SELECT 'Migration v2 complete.' AS status;
