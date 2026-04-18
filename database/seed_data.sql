-- ============================================================
-- Reset & Seed — Inventory Management System
-- Truncates all tables and re-populates with clean demo data.
-- ============================================================

USE inventory_db;

-- ── Migration: add is_deleted column if missing ─────────────
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS _migrate_add_is_deleted()
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME   = 'products'
          AND COLUMN_NAME  = 'is_deleted'
    ) THEN
        ALTER TABLE products
            ADD COLUMN is_deleted TINYINT(1) NOT NULL DEFAULT 0
            AFTER batch_number;
    END IF;
END //
DELIMITER ;
CALL _migrate_add_is_deleted();
DROP PROCEDURE IF EXISTS _migrate_add_is_deleted;

-- ── Truncate everything (FK-safe order) ─────────────────────
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transactions;
TRUNCATE TABLE products;
TRUNCATE TABLE warehouses;
TRUNCATE TABLE categories;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- ── 0. USERS ────────────────────────────────────────────────
INSERT INTO users (username, password_hash, full_name, role, email, is_active) VALUES
    ('admin', 'password', 'Admin', 'Admin', 'admin@example.com', 1),
    ('manager', 'password', 'Manager', 'Manager', 'manager@example.com', 1),
    ('clerk', 'password', 'Clerk', 'Clerk', 'clerk@example.com', 1);


-- ── 1. WAREHOUSES ───────────────────────────────────────────
INSERT INTO warehouses (name, location, is_active) VALUES
    ('Main Warehouse',   'Block A, Industrial Zone',    1),
    ('Branch A Storage', '123 Rizal Ave, Makati',       1),
    ('Branch B Storage', '456 Mabini St, Quezon City',  1);


-- ── 2. CATEGORIES ───────────────────────────────────────────
INSERT INTO categories (name, description) VALUES
    ('Canned Goods',  'Canned food products — sardines, corned beef, etc.'),
    ('Beverages',     'Drinks — juice, soda, coffee, water'),
    ('Snacks',        'Packaged snacks — chips, crackers, biscuits'),
    ('Dairy',         'Milk, cheese, yogurt, butter'),
    ('Frozen',        'Frozen meats, vegetables, and ready-to-eat meals');


-- ── Resolve IDs ─────────────────────────────────────────────
SET @wh_main = (SELECT warehouse_id FROM warehouses WHERE name = 'Main Warehouse'   LIMIT 1);
SET @wh_a    = (SELECT warehouse_id FROM warehouses WHERE name = 'Branch A Storage' LIMIT 1);
SET @wh_b    = (SELECT warehouse_id FROM warehouses WHERE name = 'Branch B Storage' LIMIT 1);

SET @cat_can = (SELECT category_id FROM categories WHERE name = 'Canned Goods' LIMIT 1);
SET @cat_bev = (SELECT category_id FROM categories WHERE name = 'Beverages'    LIMIT 1);
SET @cat_snk = (SELECT category_id FROM categories WHERE name = 'Snacks'       LIMIT 1);
SET @cat_dry = (SELECT category_id FROM categories WHERE name = 'Dairy'        LIMIT 1);
SET @cat_frz = (SELECT category_id FROM categories WHERE name = 'Frozen'       LIMIT 1);


-- ── 3. PRODUCTS ─────────────────────────────────────────────
INSERT INTO products
    (name, description, current_stock, unit, warehouse_id, category_id,
     low_stock_threshold, expiry_date, expiry_status, manufactured_date, batch_number, is_deleted)
VALUES
    -- Canned Goods
    ('Century Tuna Flakes',      'Century tuna in oil 155g',            120, 'pcs', @wh_main, @cat_can, 20, '2027-06-15', 'Active',  '2025-06-15', 'B-CT-001',  0),
    ('Argentina Corned Beef',    'Argentina corned beef 260g',            3, 'pcs', @wh_main, @cat_can, 10, '2027-03-01', 'Active',  '2025-03-01', 'B-ACB-001', 0),
    ('Mega Sardines',            'Mega sardines in tomato sauce 155g',   85, 'pcs', @wh_a,    @cat_can, 15, '2027-08-20', 'Active',  '2025-08-20', 'B-MS-001',  0),
    ('555 Fried Sardines',       '555 fried sardines hot 155g',          45, 'pcs', @wh_b,    @cat_can, 10, '2026-01-10', 'Expired', '2024-01-10', 'B-555-001', 0),

    -- Beverages
    ('Nescafe 3-in-1',           'Nescafe original 3-in-1 28g sachet', 200, 'pcs', @wh_main, @cat_bev, 30, '2027-12-01', 'Active',  '2025-12-01', 'B-NC-001',  0),
    ('C2 Apple Green Tea',       'C2 green tea apple 500ml',            60, 'btl', @wh_a,    @cat_bev, 20, '2027-04-15', 'Active',  '2026-04-15', 'B-C2-001',  0),
    ('Summit Drinking Water',    'Summit purified water 500ml',        300, 'btl', @wh_main, @cat_bev, 50,  NULL,        'Active',   NULL,          NULL,       0),
    ('Kopiko Brown Coffee',      'Kopiko brown coffee mix 25g',          8, 'pcs', @wh_b,    @cat_bev, 15, '2027-09-30', 'Active',  '2025-09-30', 'B-KB-001',  0),

    -- Snacks
    ('Oishi Prawn Crackers',     'Oishi prawn crackers original 60g',   90, 'pcs', @wh_a,    @cat_snk, 15, '2027-02-28', 'Active',  '2026-02-28', 'B-OP-001',  0),
    ('Piattos Cheese',           'Piattos cheese flavored 85g',         35, 'pcs', @wh_main, @cat_snk, 10, '2027-05-15', 'Active',  '2026-05-15', 'B-PC-001',  0),
    ('SkyFlakes Crackers',       'SkyFlakes saltine crackers 250g',     50, 'pcs', @wh_b,    @cat_snk, 10, '2027-07-01', 'Active',  '2026-01-01', 'B-SF-001',  0),

    -- Dairy
    ('Alaska Evaporada',         'Alaska evaporated milk 370ml',         5, 'pcs', @wh_main, @cat_dry, 12, '2026-11-30', 'Active',  '2025-05-30', 'B-AE-001',  0),
    ('Nestle All-Purpose Cream', 'Nestle cream 250ml',                  40, 'pcs', @wh_a,    @cat_dry, 10, '2027-01-15', 'Active',  '2026-01-15', 'B-NAP-001', 0),
    ('Eden Cheese',              'Eden original cheese 160g',           18, 'pcs', @wh_main, @cat_dry, 10, '2026-02-01', 'Expired', '2025-02-01', 'B-EC-001',  0),

    -- Frozen
    ('CDO Juicy Hotdog',         'CDO regular hotdog 500g',             25, 'pcs', @wh_b,    @cat_frz, 10, '2027-03-15', 'Active',  '2026-03-15', 'B-CDO-001', 0),
    ('Purefoods Corned Beef',    'Purefoods corned beef loaf 350g',      7, 'pcs', @wh_main, @cat_frz, 10, '2027-06-01', 'Active',  '2026-06-01', 'B-PF-001',  0),
    ('Virginia Longganisa',      'Virginia brand longganisa 500g',      30, 'pcs', @wh_a,    @cat_frz, 10, '2027-09-01', 'Active',  '2026-03-01', 'B-VL-001',  0);


-- ── Resolve product IDs ─────────────────────────────────────
SET @uid = (SELECT user_id FROM users WHERE username = 'admin' LIMIT 1);

SET @p1  = (SELECT product_id FROM products WHERE name = 'Century Tuna Flakes'      LIMIT 1);
SET @p2  = (SELECT product_id FROM products WHERE name = 'Argentina Corned Beef'     LIMIT 1);
SET @p3  = (SELECT product_id FROM products WHERE name = 'Mega Sardines'             LIMIT 1);
SET @p4  = (SELECT product_id FROM products WHERE name = '555 Fried Sardines'        LIMIT 1);
SET @p5  = (SELECT product_id FROM products WHERE name = 'Nescafe 3-in-1'            LIMIT 1);
SET @p6  = (SELECT product_id FROM products WHERE name = 'C2 Apple Green Tea'        LIMIT 1);
SET @p7  = (SELECT product_id FROM products WHERE name = 'Summit Drinking Water'     LIMIT 1);
SET @p8  = (SELECT product_id FROM products WHERE name = 'Kopiko Brown Coffee'       LIMIT 1);
SET @p9  = (SELECT product_id FROM products WHERE name = 'Oishi Prawn Crackers'      LIMIT 1);
SET @p10 = (SELECT product_id FROM products WHERE name = 'Piattos Cheese'            LIMIT 1);
SET @p11 = (SELECT product_id FROM products WHERE name = 'SkyFlakes Crackers'        LIMIT 1);
SET @p12 = (SELECT product_id FROM products WHERE name = 'Alaska Evaporada'          LIMIT 1);
SET @p13 = (SELECT product_id FROM products WHERE name = 'Nestle All-Purpose Cream'  LIMIT 1);
SET @p14 = (SELECT product_id FROM products WHERE name = 'Eden Cheese'               LIMIT 1);
SET @p15 = (SELECT product_id FROM products WHERE name = 'CDO Juicy Hotdog'          LIMIT 1);
SET @p16 = (SELECT product_id FROM products WHERE name = 'Purefoods Corned Beef'     LIMIT 1);
SET @p17 = (SELECT product_id FROM products WHERE name = 'Virginia Longganisa'       LIMIT 1);


-- ── 4. TRANSACTIONS ─────────────────────────────────────────
INSERT INTO transactions (product_id, user_id, warehouse_id, type, quantity, remarks, transaction_date) VALUES
    (@p1,  @uid, @wh_main, 'Stock-In',  150, 'Initial delivery',        '2026-04-01 08:30:00'),
    (@p1,  @uid, @wh_main, 'Stock-Out',  30, 'Sold to retailer',        '2026-04-03 10:15:00'),
    (@p2,  @uid, @wh_main, 'Stock-In',   50, 'Supplier restock',        '2026-04-02 09:00:00'),
    (@p2,  @uid, @wh_main, 'Stock-Out',  47, 'Bulk order fulfillment',  '2026-04-05 14:00:00'),
    (@p3,  @uid, @wh_a,    'Stock-In',  100, 'New batch arrival',       '2026-04-01 07:45:00'),
    (@p3,  @uid, @wh_a,    'Stock-Out',  15, 'Store display restock',   '2026-04-07 11:30:00'),
    (@p4,  @uid, @wh_b,    'Stock-In',   60, 'Bulk purchase',           '2026-03-15 08:00:00'),
    (@p4,  @uid, @wh_b,    'Stock-Out',  15, 'Outlet transfer',         '2026-04-10 13:00:00'),
    (@p5,  @uid, @wh_main, 'Stock-In',  250, 'Monthly supply',          '2026-04-01 08:00:00'),
    (@p5,  @uid, @wh_main, 'Stock-Out',  50, 'Canteen order',           '2026-04-08 09:30:00'),
    (@p6,  @uid, @wh_a,    'Stock-In',   80, 'Beverage restock',        '2026-04-04 10:00:00'),
    (@p6,  @uid, @wh_a,    'Stock-Out',  20, 'Event supply',            '2026-04-12 15:00:00'),
    (@p7,  @uid, @wh_main, 'Stock-In',  500, 'Bulk water delivery',     '2026-04-01 06:30:00'),
    (@p7,  @uid, @wh_main, 'Stock-Out', 200, 'Office distribution',     '2026-04-09 08:00:00'),
    (@p8,  @uid, @wh_b,    'Stock-In',   30, 'Small batch',             '2026-04-06 09:15:00'),
    (@p8,  @uid, @wh_b,    'Stock-Out',  22, 'Sold at counter',         '2026-04-14 16:00:00'),
    (@p9,  @uid, @wh_a,    'Stock-In',  100, 'Snack supply',            '2026-04-02 10:30:00'),
    (@p9,  @uid, @wh_a,    'Stock-Out',  10, 'Pantry restock',          '2026-04-11 12:00:00'),
    (@p10, @uid, @wh_main, 'Stock-In',   50, 'From distributor',        '2026-04-03 08:45:00'),
    (@p10, @uid, @wh_main, 'Stock-Out',  15, 'Vending machine fill',    '2026-04-13 14:30:00'),
    (@p11, @uid, @wh_b,    'Stock-In',   60, 'Cracker delivery',        '2026-04-05 07:30:00'),
    (@p11, @uid, @wh_b,    'Stock-Out',  10, 'Break room supply',       '2026-04-15 10:00:00'),
    (@p12, @uid, @wh_main, 'Stock-In',   25, 'Dairy restock',           '2026-04-04 09:00:00'),
    (@p12, @uid, @wh_main, 'Stock-Out',  20, 'Kitchen use',             '2026-04-16 11:00:00'),
    (@p14, @uid, @wh_main, 'Stock-In',   30, 'Cheese delivery',         '2026-03-20 08:00:00'),
    (@p14, @uid, @wh_main, 'Stock-Out',  12, 'Clearance sale',          '2026-04-17 09:00:00'),
    (@p15, @uid, @wh_b,    'Stock-In',   40, 'Frozen goods delivery',   '2026-04-06 07:00:00'),
    (@p15, @uid, @wh_b,    'Stock-Out',  15, 'Canteen order',           '2026-04-14 08:30:00'),
    (@p16, @uid, @wh_main, 'Stock-In',   20, 'Supplier drop-off',       '2026-04-07 09:45:00'),
    (@p16, @uid, @wh_main, 'Stock-Out',  13, 'Retail sale',             '2026-04-16 14:00:00');
