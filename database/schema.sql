-- ============================================================
-- Inventory Management System — Database Schema
-- DBMS   : MySQL 8.0+
-- Author : Auto-generated
-- Date   : 2026-04-14 (Updated)
-- ============================================================

-- Create the database (idempotent)
CREATE DATABASE IF NOT EXISTS inventory_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE inventory_db;

-- ============================================================
-- 1. USERS  (Authentication module)
--    Roles: Admin, Manager, Clerk
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id       INT            AUTO_INCREMENT,
    username      VARCHAR(50)    NOT NULL UNIQUE,
    password_hash VARCHAR(255)   NOT NULL,
    full_name     VARCHAR(100)   NOT NULL,
    role          ENUM('Admin', 'Manager', 'Clerk') NOT NULL DEFAULT 'Clerk',
    email         VARCHAR(100)   NULL,
    profile_image_url VARCHAR(255) NULL,
    assigned_warehouse_id INT NULL,
    is_active     TINYINT(1)     NOT NULL DEFAULT 1,
    created_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    INDEX idx_users_assigned_warehouse (assigned_warehouse_id)
) ENGINE=InnoDB;

-- ============================================================
-- 2. WAREHOUSES
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
-- 3. CATEGORIES
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    category_id    INT            AUTO_INCREMENT,
    name           VARCHAR(120)   NOT NULL UNIQUE,
    description    TEXT           NULL,
    created_at     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (category_id)
) ENGINE=InnoDB;

-- ============================================================
-- 4. PRODUCTS
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    product_id          INT            AUTO_INCREMENT,
    name                VARCHAR(120)   NOT NULL,
    description         TEXT           NULL,
    current_stock       INT            NOT NULL DEFAULT 0,
    unit_price          DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    unit                VARCHAR(30)    NOT NULL DEFAULT 'pcs',
    warehouse_id        INT            NULL,
    category_id         INT            NULL,
    low_stock_threshold INT            NOT NULL DEFAULT 10,
    expiry_date         DATE           NULL,
    expiry_status       ENUM('Active','Expired') NOT NULL DEFAULT 'Active',
    manufactured_date   DATE           NULL,
    batch_number        VARCHAR(100)   NULL,
    is_deleted          TINYINT(1)     NOT NULL DEFAULT 0,
    created_at          DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (product_id),

    CONSTRAINT chk_stock_non_negative CHECK (current_stock >= 0),
    CONSTRAINT chk_unit_price_non_negative CHECK (unit_price >= 0),

    CONSTRAINT fk_product_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- 5. PRODUCT_BATCHES  (Batch-level stock and expiry tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS product_batches (
    batch_id           INT            AUTO_INCREMENT,
    product_id         INT            NOT NULL,
    batch_number       VARCHAR(100)   NOT NULL,
    manufactured_date  DATE           NULL,
    expiry_date        DATE           NULL,
    expiry_status      ENUM('Active','Expired','Quarantined','Disposed') NOT NULL DEFAULT 'Active',
    quantity_on_hand   INT            NOT NULL DEFAULT 0,
    created_at         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (batch_id),

    CONSTRAINT chk_batch_quantity_non_negative CHECK (quantity_on_hand >= 0),

    CONSTRAINT fk_batch_product
        FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    UNIQUE KEY uq_batch_identity (product_id, batch_number, manufactured_date, expiry_date),

    INDEX idx_batch_product (product_id),
    INDEX idx_batch_expiry (expiry_date)
) ENGINE=InnoDB;

-- ============================================================
-- 6. TRANSACTIONS  (Stock-In / Stock-Out ledger)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   INT            AUTO_INCREMENT,
    product_id       INT            NOT NULL,
    user_id          INT            NOT NULL,
    warehouse_id     INT            NULL,
    type             ENUM('Stock-In', 'Stock-Out') NOT NULL,
    quantity         INT            NOT NULL,
    unit_cost        DECIMAL(10,2)  NULL,
    remarks          VARCHAR(255)   NULL,
    batch_id         INT            NULL,
    transaction_date DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (transaction_id),

    CONSTRAINT chk_quantity_positive CHECK (quantity > 0),

    CONSTRAINT fk_txn_product
        FOREIGN KEY (product_id) REFERENCES products (product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_txn_user
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_txn_warehouse
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT fk_txn_batch
        FOREIGN KEY (batch_id) REFERENCES product_batches (batch_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    INDEX idx_txn_product (product_id),
    INDEX idx_txn_user    (user_id),
    INDEX idx_txn_warehouse (warehouse_id),
    INDEX idx_txn_batch   (batch_id),
    INDEX idx_txn_date    (transaction_date)
) ENGINE=InnoDB;
