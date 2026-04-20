-- ============================================================
-- Reset & Seed — Warehouse/Store Management
-- Assumes schema.sql is applied first.
-- ============================================================

USE inventory_db;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transactions;
TRUNCATE TABLE product_batches;
TRUNCATE TABLE products;
TRUNCATE TABLE warehouses;
TRUNCATE TABLE categories;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- Users password: password
INSERT INTO users (username, password_hash, full_name, role, email, profile_image_url, assigned_warehouse_id, is_active) VALUES
    ('admin', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Alyssa Reyes', 'Admin', 'alyssa.reyes@warehouse.local', NULL, NULL, 1),
    ('ops_manager', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Marco Dela Cruz', 'Manager', 'marco.delacruz@warehouse.local', NULL, 1, 1),
    ('north_manager', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Nina Bautista', 'Manager', 'nina.bautista@warehouse.local', NULL, 2, 1),
    ('south_manager', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Samuel Cruz', 'Manager', 'samuel.cruz@warehouse.local', NULL, 3, 1),
    ('east_manager', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Erica Flores', 'Manager', 'erica.flores@warehouse.local', NULL, 4, 1),
    ('west_manager', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Winston Lim', 'Manager', 'winston.lim@warehouse.local', NULL, 5, 1),
    ('main_clerk_1', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Janelle Santos', 'Clerk', 'janelle.santos@warehouse.local', NULL, 1, 1),
    ('main_clerk_2', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Paolo Diaz', 'Clerk', 'paolo.diaz@warehouse.local', NULL, 1, 1),
    ('north_clerk_1', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Rica Mendoza', 'Clerk', 'rica.mendoza@warehouse.local', NULL, 2, 1),
    ('north_clerk_2', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Tessa Uy', 'Clerk', 'tessa.uy@warehouse.local', NULL, 2, 1),
    ('south_clerk_1', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Adrian Lee', 'Clerk', 'adrian.lee@warehouse.local', NULL, 3, 1),
    ('south_clerk_2', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Bianca Reyes', 'Clerk', 'bianca.reyes@warehouse.local', NULL, 3, 1),
    ('east_clerk_1', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Carlo Tan', 'Clerk', 'carlo.tan@warehouse.local', NULL, 4, 1),
    ('east_clerk_2', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Diana Cruz', 'Clerk', 'diana.cruz@warehouse.local', NULL, 4, 1),
    ('west_clerk_1', '$2b$12$WVn.UQAEmiUvAqGMkEbn5en1qtPswlaj.ACIlexb8wXvaY8M4zMVO', 'Enzo Villanueva', 'Clerk', 'enzo.villanueva@warehouse.local', NULL, 5, 1);

SET @uid_admin = (SELECT user_id FROM users WHERE username = 'admin' LIMIT 1);
SET @uid_ops_manager = (SELECT user_id FROM users WHERE username = 'ops_manager' LIMIT 1);
SET @uid_north_manager = (SELECT user_id FROM users WHERE username = 'north_manager' LIMIT 1);
SET @uid_south_manager = (SELECT user_id FROM users WHERE username = 'south_manager' LIMIT 1);
SET @uid_east_manager = (SELECT user_id FROM users WHERE username = 'east_manager' LIMIT 1);
SET @uid_west_manager = (SELECT user_id FROM users WHERE username = 'west_manager' LIMIT 1);
SET @uid_main_clerk_1 = (SELECT user_id FROM users WHERE username = 'main_clerk_1' LIMIT 1);
SET @uid_main_clerk_2 = (SELECT user_id FROM users WHERE username = 'main_clerk_2' LIMIT 1);
SET @uid_north_clerk_1 = (SELECT user_id FROM users WHERE username = 'north_clerk_1' LIMIT 1);
SET @uid_north_clerk_2 = (SELECT user_id FROM users WHERE username = 'north_clerk_2' LIMIT 1);
SET @uid_south_clerk_1 = (SELECT user_id FROM users WHERE username = 'south_clerk_1' LIMIT 1);
SET @uid_south_clerk_2 = (SELECT user_id FROM users WHERE username = 'south_clerk_2' LIMIT 1);
SET @uid_east_clerk_1 = (SELECT user_id FROM users WHERE username = 'east_clerk_1' LIMIT 1);
SET @uid_east_clerk_2 = (SELECT user_id FROM users WHERE username = 'east_clerk_2' LIMIT 1);
SET @uid_west_clerk_1 = (SELECT user_id FROM users WHERE username = 'west_clerk_1' LIMIT 1);

INSERT INTO warehouses (name, location, is_active) VALUES
    ('Main Warehouse', 'Block A, Industrial Zone', 1),
    ('North Branch Store', '12 North Avenue, Caloocan', 1),
    ('South Branch Store', '48 South Road, Parañaque', 1),
    ('East Depot Store', '7 East Loop, Pasig', 1),
    ('West Outlet Store', '90 West Point, Manila', 1);

INSERT INTO categories (name, description) VALUES
    ('Canned Goods', 'Shelf-stable canned products'),
    ('Beverages', 'Drinks and hydration items'),
    ('Snacks', 'Packaged chips, crackers, and snacks'),
    ('Dairy', 'Milk and dairy goods'),
    ('Frozen', 'Frozen foods and chilled items'),
    ('Household', 'Cleaning and household supplies'),
    ('Personal Care', 'Toiletries and personal care items');

SET @wh_main = (SELECT warehouse_id FROM warehouses WHERE name = 'Main Warehouse' LIMIT 1);
SET @wh_north = (SELECT warehouse_id FROM warehouses WHERE name = 'North Branch Store' LIMIT 1);
SET @wh_south = (SELECT warehouse_id FROM warehouses WHERE name = 'South Branch Store' LIMIT 1);
SET @wh_east = (SELECT warehouse_id FROM warehouses WHERE name = 'East Depot Store' LIMIT 1);
SET @wh_west = (SELECT warehouse_id FROM warehouses WHERE name = 'West Outlet Store' LIMIT 1);

SET @cat_can = (SELECT category_id FROM categories WHERE name = 'Canned Goods' LIMIT 1);
SET @cat_bev = (SELECT category_id FROM categories WHERE name = 'Beverages' LIMIT 1);
SET @cat_snk = (SELECT category_id FROM categories WHERE name = 'Snacks' LIMIT 1);
SET @cat_dry = (SELECT category_id FROM categories WHERE name = 'Dairy' LIMIT 1);
SET @cat_frz = (SELECT category_id FROM categories WHERE name = 'Frozen' LIMIT 1);
SET @cat_hhp = (SELECT category_id FROM categories WHERE name = 'Household' LIMIT 1);
SET @cat_per = (SELECT category_id FROM categories WHERE name = 'Personal Care' LIMIT 1);

INSERT INTO products
    (name, description, current_stock, unit_price, unit, warehouse_id, category_id,
     low_stock_threshold, expiry_date, expiry_status, manufactured_date, batch_number, is_deleted)
VALUES
    ('Century Tuna Flakes', 'Century tuna in oil 155g', 120, 38.50, 'pcs', @wh_main, @cat_can, 24, '2027-06-15', 'Active', '2025-06-15', 'B-CT-001', 0),
    ('Argentina Corned Beef', 'Argentina corned beef 260g', 84, 52.00, 'pcs', @wh_main, @cat_can, 18, '2027-03-01', 'Active', '2025-03-01', 'B-ACB-001', 0),
    ('Nescafe 3-in-1', 'Nescafe original 3-in-1 sachet', 260, 12.00, 'pcs', @wh_main, @cat_bev, 40, '2027-12-01', 'Active', '2025-12-01', 'B-NC-001', 0),
    ('Summit Drinking Water', 'Summit purified water 500ml', 420, 10.00, 'btl', @wh_main, @cat_bev, 80, NULL, 'Active', NULL, 'B-SW-001', 0),
    ('Alaska Evaporada', 'Alaska evaporated milk 370ml', 36, 39.00, 'pcs', @wh_main, @cat_dry, 12, '2026-03-12', 'Expired', '2025-05-30', 'B-AE-001', 0),
    ('Piattos Cheese', 'Piattos cheese flavored 85g', 62, 21.00, 'pcs', @wh_main, @cat_snk, 16, '2027-05-15', 'Active', '2026-05-15', 'B-PC-001', 0),
    ('Lucky Me Pancit Canton', 'Pancit Canton chicken flavor', 180, 15.00, 'pcs', @wh_north, @cat_snk, 30, '2027-01-22', 'Active', '2026-01-22', 'B-LM-001', 0),
    ('C2 Apple Green Tea', 'C2 green tea apple 500ml', 92, 18.50, 'btl', @wh_north, @cat_bev, 20, '2027-04-15', 'Active', '2026-04-15', 'B-C2-001', 0),
    ('Oishi Prawn Crackers', 'Oishi prawn crackers 60g', 74, 17.25, 'pcs', @wh_north, @cat_snk, 18, '2027-02-28', 'Active', '2026-02-28', 'B-OP-001', 0),
    ('Magnolia Chocolate Milk', 'Magnolia chocolate milk 1L', 96, 22.00, 'pcs', @wh_north, @cat_dry, 20, '2027-06-20', 'Active', '2026-06-20', 'B-MC-001', 0),
    ('Yakult Original', 'Yakult probiotic drink 5-pack', 48, 9.50, 'pack', @wh_north, @cat_dry, 14, '2026-03-31', 'Expired', '2025-11-30', 'B-YA-001', 0),
    ('Safeguard Bath Soap', 'Safeguard soap 90g', 140, 25.00, 'pcs', @wh_north, @cat_per, 24, '2027-08-15', 'Active', '2026-08-15', 'B-SG-001', 0),
    ('Purefoods Corned Beef', 'Purefoods corned beef loaf 350g', 34, 115.00, 'pcs', @wh_south, @cat_can, 10, '2027-06-01', 'Active', '2026-06-01', 'B-PF-001', 0),
    ('SkyFlakes Crackers', 'SkyFlakes saltine crackers 250g', 76, 15.50, 'pcs', @wh_south, @cat_snk, 20, '2027-07-01', 'Active', '2026-01-01', 'B-SF-001', 0),
    ('Zesto Orange Drink', 'Zesto orange juice drink 250ml', 150, 11.00, 'btl', @wh_south, @cat_bev, 30, '2027-04-01', 'Active', '2026-04-01', 'B-ZO-001', 0),
    ('Champion Detergent Powder', 'Champion detergent powder 1kg', 40, 78.00, 'pack', @wh_south, @cat_hhp, 12, '2027-02-11', 'Active', '2026-02-11', 'B-CH-001', 0),
    ('Selecta Ice Cream Cup', 'Selecta cookies and cream cup', 24, 24.00, 'cup', @wh_south, @cat_frz, 8, '2026-10-15', 'Active', '2026-04-15', 'B-SI-001', 0),
    ('Cream Silk Conditioner', 'Cream Silk conditioner 180ml', 48, 89.00, 'btl', @wh_south, @cat_per, 16, '2026-03-20', 'Expired', '2025-09-20', 'B-CS-001', 0),
    ('CDO Juicy Hotdog', 'CDO regular hotdog 500g', 58, 88.00, 'pcs', @wh_east, @cat_frz, 14, '2027-03-15', 'Active', '2026-03-15', 'B-CDO-001', 0),
    ('Mega Sardines', 'Mega sardines in tomato sauce 155g', 112, 24.75, 'pcs', @wh_east, @cat_can, 22, '2027-08-20', 'Active', '2025-08-20', 'B-MS-001', 0),
    ('Nova Cheese', 'Nova cheese flavored corn chips', 76, 13.75, 'pcs', @wh_east, @cat_snk, 18, '2027-07-09', 'Active', '2026-07-09', 'B-NV-001', 0),
    ('Alaska Powdered Milk', 'Alaska powdered milk 500g', 30, 210.00, 'pack', @wh_east, @cat_dry, 10, '2027-05-05', 'Active', '2026-05-05', 'B-AP-001', 0),
    ('Head and Shoulders Shampoo', 'H&S shampoo 180ml', 45, 160.00, 'btl', @wh_east, @cat_per, 12, '2027-01-12', 'Active', '2026-01-12', 'B-HS-001', 0),
    ('Bear Brand Fortified', 'Bear Brand powdered milk 300g', 62, 18.00, 'pack', @wh_east, @cat_dry, 16, '2027-09-18', 'Active', '2026-09-18', 'B-BB-001', 0),
    ('Spam Classic', 'Spam classic luncheon meat 340g', 22, 185.00, 'can', @wh_west, @cat_can, 8, '2027-10-10', 'Active', '2026-10-10', 'B-SP-001', 0),
    ('Gardenia White Bread', 'Gardenia white bread loaf', 44, 42.00, 'loaf', @wh_west, @cat_dry, 14, '2026-04-25', 'Active', '2026-04-18', 'B-GW-001', 0),
    ('Nestea Iced Tea', 'Nestea iced tea 330ml', 180, 12.00, 'btl', @wh_west, @cat_bev, 30, '2027-06-30', 'Active', '2026-06-30', 'B-NT-001', 0),
    ('Surf Detergent', 'Surf detergent powder 1kg', 66, 30.00, 'pack', @wh_west, @cat_hhp, 14, '2027-02-01', 'Active', '2026-02-01', 'B-SU-001', 0),
    ('Chippy Barbecue', 'Chippy barbecue corn chips', 95, 9.50, 'pcs', @wh_west, @cat_snk, 20, '2027-08-08', 'Active', '2026-08-08', 'B-CHP-001', 0),
    ('Energen Chocolate', 'Energen chocolate cereal drink', 130, 14.00, 'pack', @wh_west, @cat_dry, 25, '2027-03-30', 'Active', '2026-03-30', 'B-EN-001', 0);

-- Seed batch inventory per product for FEFO + expiry action workflows
INSERT INTO product_batches
    (product_id, batch_number, manufactured_date, expiry_date, expiry_status, quantity_on_hand)
SELECT
    p.product_id,
    COALESCE(p.batch_number, CONCAT('AUTO-BATCH-', p.product_id)),
    p.manufactured_date,
    p.expiry_date,
    CASE
        WHEN p.expiry_status IN ('Quarantined', 'Disposed') THEN p.expiry_status
        WHEN p.expiry_date IS NOT NULL AND p.expiry_date < CURDATE() THEN 'Expired'
        ELSE 'Active'
    END,
    p.current_stock
FROM products p
WHERE p.is_deleted = 0;

-- Create explicit actionable rows for Clerk expiry workflow demos
UPDATE product_batches pb
JOIN products p ON p.product_id = pb.product_id
SET pb.expiry_status = 'Quarantined',
    pb.expiry_date = DATE_SUB(CURDATE(), INTERVAL 5 DAY)
WHERE p.name = 'Yakult Original';

UPDATE product_batches pb
JOIN products p ON p.product_id = pb.product_id
SET pb.expiry_status = 'Expired',
    pb.expiry_date = DATE_SUB(CURDATE(), INTERVAL 20 DAY)
WHERE p.name = 'Cream Silk Conditioner';

SET @p1 = (SELECT product_id FROM products WHERE name = 'Century Tuna Flakes' LIMIT 1);
SET @p2 = (SELECT product_id FROM products WHERE name = 'Argentina Corned Beef' LIMIT 1);
SET @p3 = (SELECT product_id FROM products WHERE name = 'Nescafe 3-in-1' LIMIT 1);
SET @p4 = (SELECT product_id FROM products WHERE name = 'Summit Drinking Water' LIMIT 1);
SET @p5 = (SELECT product_id FROM products WHERE name = 'Alaska Evaporada' LIMIT 1);
SET @p6 = (SELECT product_id FROM products WHERE name = 'Piattos Cheese' LIMIT 1);
SET @p7 = (SELECT product_id FROM products WHERE name = 'Lucky Me Pancit Canton' LIMIT 1);
SET @p8 = (SELECT product_id FROM products WHERE name = 'C2 Apple Green Tea' LIMIT 1);
SET @p9 = (SELECT product_id FROM products WHERE name = 'Oishi Prawn Crackers' LIMIT 1);
SET @p10 = (SELECT product_id FROM products WHERE name = 'Magnolia Chocolate Milk' LIMIT 1);
SET @p11 = (SELECT product_id FROM products WHERE name = 'Yakult Original' LIMIT 1);
SET @p12 = (SELECT product_id FROM products WHERE name = 'Safeguard Bath Soap' LIMIT 1);
SET @p13 = (SELECT product_id FROM products WHERE name = 'Purefoods Corned Beef' LIMIT 1);
SET @p14 = (SELECT product_id FROM products WHERE name = 'SkyFlakes Crackers' LIMIT 1);
SET @p15 = (SELECT product_id FROM products WHERE name = 'Zesto Orange Drink' LIMIT 1);
SET @p16 = (SELECT product_id FROM products WHERE name = 'Champion Detergent Powder' LIMIT 1);
SET @p17 = (SELECT product_id FROM products WHERE name = 'Selecta Ice Cream Cup' LIMIT 1);
SET @p18 = (SELECT product_id FROM products WHERE name = 'Cream Silk Conditioner' LIMIT 1);
SET @p19 = (SELECT product_id FROM products WHERE name = 'CDO Juicy Hotdog' LIMIT 1);
SET @p20 = (SELECT product_id FROM products WHERE name = 'Mega Sardines' LIMIT 1);
SET @p21 = (SELECT product_id FROM products WHERE name = 'Nova Cheese' LIMIT 1);
SET @p22 = (SELECT product_id FROM products WHERE name = 'Alaska Powdered Milk' LIMIT 1);
SET @p23 = (SELECT product_id FROM products WHERE name = 'Head and Shoulders Shampoo' LIMIT 1);
SET @p24 = (SELECT product_id FROM products WHERE name = 'Bear Brand Fortified' LIMIT 1);
SET @p25 = (SELECT product_id FROM products WHERE name = 'Spam Classic' LIMIT 1);
SET @p26 = (SELECT product_id FROM products WHERE name = 'Gardenia White Bread' LIMIT 1);
SET @p27 = (SELECT product_id FROM products WHERE name = 'Nestea Iced Tea' LIMIT 1);
SET @p28 = (SELECT product_id FROM products WHERE name = 'Surf Detergent' LIMIT 1);
SET @p29 = (SELECT product_id FROM products WHERE name = 'Chippy Barbecue' LIMIT 1);
SET @p30 = (SELECT product_id FROM products WHERE name = 'Energen Chocolate' LIMIT 1);

INSERT INTO transactions (product_id, user_id, warehouse_id, type, quantity, unit_cost, remarks, transaction_date) VALUES
    (@p1, @uid_main_clerk_1, @wh_main, 'Stock-In', 36, 38.50, 'opening receiving', '2026-03-01 08:15:00'),
    (@p2, @uid_main_clerk_2, @wh_main, 'Stock-In', 28, 52.00, 'supplier receiving', '2026-03-01 11:40:00'),
    (@p3, @uid_main_clerk_1, @wh_main, 'Stock-In', 72, 12.00, 'shelf refill', '2026-03-01 16:20:00'),
    (@p4, @uid_ops_manager, @wh_main, 'Stock-In', 120, 10.30, 'bulk receiving', '2026-03-02 08:15:00'),
    (@p5, @uid_main_clerk_1, @wh_main, 'Stock-In', 14, 41.34, 'expiry clearance intake', '2026-03-02 11:40:00'),
    (@p6, @uid_main_clerk_2, @wh_main, 'Stock-In', 40, 21.00, 'promotional refill', '2026-03-02 16:20:00'),
    (@p7, @uid_north_clerk_1, @wh_north, 'Stock-In', 52, 15.00, 'branch transfer in', '2026-03-03 08:15:00'),
    (@p8, @uid_north_clerk_2, @wh_north, 'Stock-In', 64, 17.76, 'supplier price update', '2026-03-03 11:40:00'),
    (@p9, @uid_north_clerk_1, @wh_north, 'Stock-In', 38, 17.25, 'routine receiving', '2026-03-03 16:20:00'),
    (@p10, @uid_north_manager, @wh_north, 'Stock-In', 44, 22.66, 'manager-approved replenishment', '2026-03-04 08:15:00'),
    (@p11, @uid_north_clerk_1, @wh_north, 'Stock-In', 18, 10.07, 'near-expiry intake', '2026-03-04 11:40:00'),
    (@p12, @uid_admin, @wh_north, 'Stock-In', 55, 27.25, 'admin audit receiving', '2026-03-04 16:20:00'),
    (@p13, @uid_south_clerk_1, @wh_south, 'Stock-In', 26, 115.00, 'receiving for display', '2026-03-05 08:15:00'),
    (@p14, @uid_south_clerk_2, @wh_south, 'Stock-In', 48, 15.50, 'backroom refill', '2026-03-05 11:40:00'),
    (@p15, @uid_south_clerk_1, @wh_south, 'Stock-In', 70, 10.56, 'price-change replenishment', '2026-03-05 16:20:00'),
    (@p16, @uid_south_manager, @wh_south, 'Stock-In', 32, 80.34, 'supervised restock', '2026-03-06 08:15:00'),
    (@p17, @uid_south_clerk_1, @wh_south, 'Stock-In', 24, 24.00, 'received for promo', '2026-03-06 11:40:00'),
    (@p18, @uid_south_clerk_2, @wh_south, 'Stock-In', 20, 94.34, 'expired clearance intake', '2026-03-06 16:20:00'),
    (@p19, @uid_east_clerk_1, @wh_east, 'Stock-In', 29, 88.00, 'routine receiving', '2026-03-07 08:15:00'),
    (@p20, @uid_east_clerk_2, @wh_east, 'Stock-In', 60, 26.98, 'supplier restock', '2026-03-07 11:40:00'),
    (@p21, @uid_east_clerk_1, @wh_east, 'Stock-In', 31, 13.75, 'shelf refill', '2026-03-07 16:20:00'),
    (@p22, @uid_east_manager, @wh_east, 'Stock-In', 18, 216.30, 'manager-approved restock', '2026-03-08 08:15:00'),
    (@p23, @uid_east_clerk_1, @wh_east, 'Stock-In', 23, 160.00, 'branch transfer in', '2026-03-08 11:40:00'),
    (@p24, @uid_admin, @wh_east, 'Stock-In', 25, 17.28, 'price adjustment receiving', '2026-03-08 16:20:00'),
    (@p25, @uid_west_clerk_1, @wh_west, 'Stock-In', 16, 185.00, 'warehouse receiving', '2026-03-09 08:15:00'),
    (@p26, @uid_west_clerk_1, @wh_west, 'Stock-In', 22, 42.00, 'display refill', '2026-03-09 11:40:00'),
    (@p27, @uid_west_clerk_1, @wh_west, 'Stock-In', 68, 11.52, 'supplier price update', '2026-03-09 16:20:00'),
    (@p28, @uid_west_manager, @wh_west, 'Stock-In', 30, 30.90, 'admin stock audit', '2026-03-10 08:15:00'),
    (@p29, @uid_west_clerk_1, @wh_west, 'Stock-In', 50, 9.50, 'routine receiving', '2026-03-10 11:40:00'),
    (@p30, @uid_west_clerk_1, @wh_west, 'Stock-In', 34, 15.26, 'bulk replenishment', '2026-03-10 16:20:00'),
    (@p1, @uid_main_clerk_1, @wh_main, 'Stock-Out', 13, 38.50, 'branch transfer out', '2026-03-11 08:15:00'),
    (@p2, @uid_main_clerk_2, @wh_main, 'Stock-Out', 16, 50.96, 'daily stock-out', '2026-03-11 11:40:00'),
    (@p3, @uid_main_clerk_1, @wh_main, 'Stock-Out', 19, 12.24, 'promo bundle issue', '2026-03-11 16:20:00'),
    (@p4, @uid_main_clerk_2, @wh_main, 'Stock-Out', 5, 10.00, 'daily stock-out', '2026-03-12 08:15:00'),
    (@p5, @uid_ops_manager, @wh_main, 'Stock-Out', 6, 33.54, 'expired disposal and clearance', '2026-03-12 11:40:00'),
    (@p6, @uid_main_clerk_2, @wh_main, 'Stock-Out', 17, 21.00, 'daily stock-out', '2026-03-12 16:20:00'),
    (@p7, @uid_admin, @wh_north, 'Stock-Out', 14, 15.00, 'daily stock-out', '2026-03-13 08:15:00'),
    (@p8, @uid_north_clerk_2, @wh_north, 'Stock-Out', 17, 18.50, 'daily stock-out', '2026-03-13 11:40:00'),
    (@p9, @uid_north_clerk_1, @wh_north, 'Stock-Out', 20, 17.25, 'daily stock-out', '2026-03-13 16:20:00'),
    (@p10, @uid_north_clerk_2, @wh_north, 'Stock-Out', 6, 21.56, 'daily stock-out', '2026-03-14 08:15:00'),
    (@p11, @uid_north_clerk_1, @wh_north, 'Stock-Out', 5, 8.17, 'expired disposal and clearance', '2026-03-14 11:40:00'),
    (@p12, @uid_north_clerk_2, @wh_north, 'Stock-Out', 12, 25.00, 'daily stock-out', '2026-03-14 16:20:00'),
    (@p13, @uid_south_clerk_1, @wh_south, 'Stock-Out', 15, 115.00, 'daily stock-out', '2026-03-15 08:15:00'),
    (@p14, @uid_south_clerk_2, @wh_south, 'Stock-Out', 18, 15.81, 'daily stock-out', '2026-03-15 11:40:00'),
    (@p15, @uid_south_clerk_1, @wh_south, 'Stock-Out', 27, 11.00, 'daily stock-out', '2026-03-15 16:20:00'),
    (@p16, @uid_south_clerk_2, @wh_south, 'Stock-Out', 7, 78.00, 'branch transfer out', '2026-03-16 08:15:00'),
    (@p17, @uid_south_clerk_1, @wh_south, 'Stock-Out', 10, 24.00, 'daily stock-out', '2026-03-16 11:40:00'),
    (@p18, @uid_south_clerk_2, @wh_south, 'Stock-Out', 13, 87.22, 'daily stock-out', '2026-03-16 16:20:00'),
    (@p19, @uid_east_manager, @wh_east, 'Stock-Out', 16, 88.00, 'manager-approved issue', '2026-03-17 08:15:00'),
    (@p20, @uid_east_clerk_2, @wh_east, 'Stock-Out', 19, 24.75, 'damaged write-off', '2026-03-17 11:40:00'),
    (@p21, @uid_east_clerk_1, @wh_east, 'Stock-Out', 5, 13.75, 'daily stock-out', '2026-03-17 16:20:00'),
    (@p22, @uid_east_clerk_2, @wh_east, 'Stock-Out', 8, 210.00, 'daily stock-out', '2026-03-18 08:15:00'),
    (@p23, @uid_east_clerk_1, @wh_east, 'Stock-Out', 11, 160.00, 'daily stock-out', '2026-03-18 11:40:00'),
    (@p24, @uid_admin, @wh_east, 'Stock-Out', 20, 18.00, 'daily stock-out', '2026-03-18 16:20:00'),
    (@p25, @uid_west_clerk_1, @wh_west, 'Stock-Out', 17, 188.70, 'daily stock-out', '2026-03-19 08:15:00'),
    (@p26, @uid_west_clerk_1, @wh_west, 'Stock-Out', 20, 41.16, 'daily stock-out', '2026-03-19 11:40:00'),
    (@p27, @uid_west_clerk_1, @wh_west, 'Stock-Out', 6, 12.00, 'promo bundle issue', '2026-03-19 16:20:00'),
    (@p28, @uid_west_clerk_1, @wh_west, 'Stock-Out', 9, 30.00, 'daily stock-out', '2026-03-20 08:15:00'),
    (@p29, @uid_west_clerk_1, @wh_west, 'Stock-Out', 12, 9.50, 'daily stock-out', '2026-03-20 11:40:00'),
    (@p30, @uid_west_clerk_1, @wh_west, 'Stock-Out', 15, 14.00, 'daily stock-out', '2026-03-20 16:20:00'),
    (@p1, @uid_main_clerk_1, @wh_main, 'Stock-Out', 18, 38.50, 'branch transfer out', '2026-03-21 08:15:00'),
    (@p2, @uid_main_clerk_2, @wh_main, 'Stock-Out', 21, 52.00, 'daily stock-out', '2026-03-21 11:40:00'),
    (@p3, @uid_ops_manager, @wh_main, 'Stock-Out', 13, 12.00, 'manager-approved issue', '2026-03-21 16:20:00'),
    (@p4, @uid_main_clerk_2, @wh_main, 'Stock-Out', 10, 9.80, 'daily stock-out', '2026-03-22 08:15:00'),
    (@p5, @uid_main_clerk_1, @wh_main, 'Stock-Out', 4, 33.54, 'expired disposal and clearance', '2026-03-22 11:40:00'),
    (@p6, @uid_main_clerk_2, @wh_main, 'Stock-Out', 16, 21.42, 'daily stock-out', '2026-03-22 16:20:00'),
    (@p7, @uid_north_clerk_1, @wh_north, 'Stock-Out', 19, 15.00, 'daily stock-out', '2026-03-23 08:15:00'),
    (@p8, @uid_north_clerk_2, @wh_north, 'Stock-Out', 5, 18.50, 'inventory audit adjustment', '2026-03-23 11:40:00'),
    (@p9, @uid_north_clerk_1, @wh_north, 'Stock-Out', 8, 17.25, 'daily stock-out', '2026-03-23 16:20:00'),
    (@p10, @uid_north_clerk_2, @wh_north, 'Stock-Out', 11, 22.00, 'daily stock-out', '2026-03-24 08:15:00'),
    (@p11, @uid_north_clerk_1, @wh_north, 'Stock-Out', 7, 8.17, 'expired disposal and clearance', '2026-03-24 11:40:00'),
    (@p12, @uid_north_clerk_2, @wh_north, 'Stock-Out', 23, 24.50, 'promo bundle issue', '2026-03-24 16:20:00'),
    (@p13, @uid_south_clerk_1, @wh_south, 'Stock-Out', 20, 115.00, 'daily stock-out', '2026-03-25 08:15:00'),
    (@p14, @uid_south_clerk_2, @wh_south, 'Stock-Out', 6, 15.50, 'daily stock-out', '2026-03-25 11:40:00'),
    (@p15, @uid_south_clerk_1, @wh_south, 'Stock-Out', 9, 11.00, 'damaged write-off', '2026-03-25 16:20:00'),
    (@p16, @uid_south_clerk_2, @wh_south, 'Stock-Out', 12, 78.00, 'branch transfer out', '2026-03-26 08:15:00'),
    (@p17, @uid_south_manager, @wh_south, 'Stock-Out', 15, 24.48, 'manager-approved issue', '2026-03-26 11:40:00'),
    (@p18, @uid_admin, @wh_south, 'Stock-Out', 6, 76.54, 'expired disposal and clearance', '2026-03-26 16:20:00'),
    (@p19, @uid_east_clerk_1, @wh_east, 'Stock-Out', 21, 88.00, 'daily stock-out', '2026-03-27 08:15:00'),
    (@p20, @uid_east_clerk_2, @wh_east, 'Stock-Out', 7, 24.25, 'daily stock-out', '2026-03-27 11:40:00'),
    (@p21, @uid_east_clerk_1, @wh_east, 'Stock-Out', 16, 13.75, 'daily stock-out', '2026-03-27 16:20:00'),
    (@p22, @uid_east_clerk_2, @wh_east, 'Stock-Out', 13, 210.00, 'daily stock-out', '2026-03-28 08:15:00'),
    (@p23, @uid_east_clerk_1, @wh_east, 'Stock-Out', 16, 160.00, 'daily stock-out', '2026-03-28 11:40:00'),
    (@p24, @uid_east_clerk_2, @wh_east, 'Stock-Out', 19, 18.00, 'promo bundle issue', '2026-03-28 16:20:00'),
    (@p25, @uid_west_clerk_1, @wh_west, 'Stock-Out', 5, 185.00, 'daily stock-out', '2026-03-29 08:15:00'),
    (@p26, @uid_west_clerk_1, @wh_west, 'Stock-Out', 8, 42.00, 'daily stock-out', '2026-03-29 11:40:00'),
    (@p27, @uid_west_clerk_1, @wh_west, 'Stock-Out', 11, 12.00, 'daily stock-out', '2026-03-29 16:20:00'),
    (@p28, @uid_west_clerk_1, @wh_west, 'Stock-Out', 14, 30.60, 'daily stock-out', '2026-03-30 08:15:00'),
    (@p29, @uid_west_clerk_1, @wh_west, 'Stock-Out', 17, 9.50, 'daily stock-out', '2026-03-30 11:40:00'),
    (@p30, @uid_west_clerk_1, @wh_west, 'Stock-Out', 26, 14.00, 'inventory audit adjustment', '2026-03-30 16:20:00'),
    (@p1, @uid_ops_manager, @wh_main, 'Stock-Out', 6, 38.50, 'manager-approved issue', '2026-03-31 08:15:00'),
    (@p2, @uid_main_clerk_2, @wh_main, 'Stock-Out', 9, 52.00, 'daily stock-out', '2026-03-31 11:40:00'),
    (@p3, @uid_main_clerk_1, @wh_main, 'Stock-Out', 12, 12.00, 'daily stock-out', '2026-03-31 16:20:00'),
    (@p4, @uid_main_clerk_2, @wh_main, 'Stock-Out', 15, 10.00, 'daily stock-out', '2026-04-01 08:15:00'),
    (@p5, @uid_main_clerk_1, @wh_main, 'Stock-Out', 8, 33.54, 'expired disposal and clearance', '2026-04-01 11:40:00'),
    (@p6, @uid_admin, @wh_main, 'Stock-Out', 21, 20.58, 'branch transfer out', '2026-04-01 16:20:00'),
    (@p7, @uid_north_clerk_1, @wh_north, 'Stock-Out', 7, 15.00, 'daily stock-out', '2026-04-02 08:15:00'),
    (@p8, @uid_north_clerk_2, @wh_north, 'Stock-Out', 10, 18.50, 'daily stock-out', '2026-04-02 11:40:00'),
    (@p9, @uid_north_clerk_1, @wh_north, 'Stock-Out', 19, 17.59, 'promo bundle issue', '2026-04-02 16:20:00'),
    (@p10, @uid_north_clerk_2, @wh_north, 'Stock-Out', 16, 22.00, 'damaged write-off', '2026-04-03 08:15:00'),
    (@p11, @uid_north_clerk_1, @wh_north, 'Stock-Out', 5, 8.17, 'expired disposal and clearance', '2026-04-03 11:40:00'),
    (@p12, @uid_north_clerk_2, @wh_north, 'Stock-Out', 5, 25.00, 'daily stock-out', '2026-04-03 16:20:00'),
    (@p13, @uid_south_clerk_1, @wh_south, 'Stock-Out', 8, 115.00, 'daily stock-out', '2026-04-04 08:15:00'),
    (@p14, @uid_south_clerk_2, @wh_south, 'Stock-Out', 11, 15.19, 'daily stock-out', '2026-04-04 11:40:00'),
    (@p15, @uid_south_clerk_1, @wh_south, 'Stock-Out', 14, 11.00, 'branch transfer out', '2026-04-04 16:20:00'),
    (@p16, @uid_south_clerk_2, @wh_south, 'Stock-In', 44, 79.56, 'replenishment receiving', '2026-04-05 08:15:00'),
    (@p17, @uid_south_clerk_1, @wh_south, 'Stock-In', 36, 24.00, 'shelf refill', '2026-04-05 11:40:00'),
    (@p18, @uid_south_manager, @wh_south, 'Stock-In', 58, 95.23, 'expired clearance intake', '2026-04-05 16:20:00'),
    (@p19, @uid_east_clerk_1, @wh_east, 'Stock-In', 82, 88.00, 'supplier price change', '2026-04-06 08:15:00'),
    (@p20, @uid_east_clerk_2, @wh_east, 'Stock-In', 20, 24.75, 'branch transfer in', '2026-04-06 11:40:00'),
    (@p21, @uid_east_clerk_1, @wh_east, 'Stock-In', 46, 13.06, 'promo stock top-up', '2026-04-06 16:20:00'),
    (@p22, @uid_admin, @wh_east, 'Stock-In', 34, 214.20, 'routine receiving', '2026-04-07 08:15:00'),
    (@p23, @uid_east_clerk_1, @wh_east, 'Stock-In', 42, 160.00, 'backroom refill', '2026-04-07 11:40:00'),
    (@p24, @uid_east_manager, @wh_east, 'Stock-In', 28, 19.26, 'special replenishment', '2026-04-07 16:20:00'),
    (@p25, @uid_west_clerk_1, @wh_west, 'Stock-In', 50, 185.00, 'inventory audit restock', '2026-04-08 08:15:00'),
    (@p26, @uid_west_clerk_1, @wh_west, 'Stock-In', 18, 42.00, 'receiving for display', '2026-04-08 11:40:00'),
    (@p27, @uid_west_clerk_1, @wh_west, 'Stock-In', 24, 11.40, 'price adjustment restock', '2026-04-08 16:20:00'),
    (@p28, @uid_west_clerk_1, @wh_west, 'Stock-In', 30, 30.60, 'warehouse replenishment', '2026-04-09 08:15:00'),
    (@p29, @uid_west_clerk_1, @wh_west, 'Stock-In', 26, 9.50, 'shelf refill', '2026-04-09 11:40:00'),
    (@p30, @uid_west_manager, @wh_west, 'Stock-In', 38, 14.98, 'manager-approved bulk replenishment', '2026-04-09 16:20:00'),
    (@p1, @uid_main_clerk_1, @wh_main, 'Stock-Out', 11, 39.27, 'daily stock-out', '2026-04-10 08:15:00'),
    (@p2, @uid_main_clerk_2, @wh_main, 'Stock-In', 33, 52.52, 'branch stock-in', '2026-04-10 11:40:00'),
    (@p3, @uid_main_clerk_1, @wh_main, 'Stock-Out', 17, 12.00, 'promo bundle issue', '2026-04-10 16:20:00'),
    (@p4, @uid_main_clerk_2, @wh_main, 'Stock-In', 20, 10.10, 'shelf refill', '2026-04-11 08:15:00'),
    (@p5, @uid_ops_manager, @wh_main, 'Stock-Out', 3, 33.54, 'expired disposal and clearance', '2026-04-11 11:40:00'),
    (@p6, @uid_admin, @wh_main, 'Stock-In', 44, 20.37, 'manager-approved replenishment', '2026-04-11 16:20:00'),
    (@p7, @uid_north_clerk_1, @wh_north, 'Stock-Out', 12, 15.00, 'daily stock-out', '2026-04-12 08:15:00'),
    (@p8, @uid_north_clerk_2, @wh_north, 'Stock-In', 21, 18.68, 'inventory audit restock', '2026-04-12 11:40:00'),
    (@p9, @uid_north_clerk_1, @wh_north, 'Stock-Out', 18, 17.25, 'inventory audit adjustment', '2026-04-12 16:20:00'),
    (@p10, @uid_north_manager, @wh_north, 'Stock-In', 35, 23.10, 'special manager-approved replenishment', '2026-04-13 08:15:00'),
    (@p11, @uid_north_clerk_1, @wh_north, 'Stock-Out', 6, 8.17, 'expired disposal and clearance', '2026-04-13 11:40:00'),
    (@p12, @uid_north_clerk_2, @wh_north, 'Stock-In', 32, 25.25, 'supplier receiving', '2026-04-13 16:20:00'),
    (@p13, @uid_south_clerk_1, @wh_south, 'Stock-Out', 13, 115.00, 'daily stock-out', '2026-04-14 08:15:00'),
    (@p14, @uid_south_clerk_2, @wh_south, 'Stock-In', 36, 15.65, 'backroom refill', '2026-04-14 11:40:00'),
    (@p15, @uid_south_clerk_1, @wh_south, 'Stock-Out', 25, 11.00, 'promo bundle issue', '2026-04-14 16:20:00'),
    (@p16, @uid_south_clerk_2, @wh_south, 'Stock-In', 23, 78.78, 'promotion prep', '2026-04-15 08:15:00'),
    (@p17, @uid_south_clerk_1, @wh_south, 'Stock-Out', 8, 24.00, 'branch transfer out', '2026-04-15 11:40:00'),
    (@p18, @uid_south_clerk_2, @wh_south, 'Stock-In', 47, 89.89, 'warehouse receiving', '2026-04-15 16:20:00'),
    (@p19, @uid_east_manager, @wh_east, 'Stock-Out', 14, 88.00, 'manager-approved issue', '2026-04-16 08:15:00'),
    (@p20, @uid_east_clerk_2, @wh_east, 'Stock-In', 24, 25.99, 'replenishment top-up', '2026-04-16 11:40:00'),
    (@p21, @uid_east_clerk_1, @wh_east, 'Stock-Out', 20, 13.75, 'daily stock-out', '2026-04-16 16:20:00'),
    (@p22, @uid_east_manager, @wh_east, 'Stock-In', 38, 212.10, 'manager-approved replenishment', '2026-04-17 08:15:00'),
    (@p23, @uid_east_clerk_1, @wh_east, 'Stock-Out', 9, 163.20, 'damaged write-off', '2026-04-17 11:40:00'),
    (@p24, @uid_admin, @wh_east, 'Stock-In', 35, 18.18, 'admin audit receiving', '2026-04-17 16:20:00'),
    (@p25, @uid_west_clerk_1, @wh_west, 'Stock-Out', 15, 185.00, 'inventory audit adjustment', '2026-04-18 08:15:00'),
    (@p26, @uid_west_clerk_1, @wh_west, 'Stock-In', 39, 42.42, 'display refill', '2026-04-18 11:40:00'),
    (@p27, @uid_west_clerk_1, @wh_west, 'Stock-Out', 21, 12.00, 'promo bundle issue', '2026-04-18 16:20:00'),
    (@p28, @uid_west_clerk_1, @wh_west, 'Stock-In', 26, 30.30, 'branch transfer in', '2026-04-19 08:15:00'),
    (@p29, @uid_west_clerk_1, @wh_west, 'Stock-Out', 10, 9.50, 'daily stock-out', '2026-04-19 11:40:00'),
    (@p30, @uid_west_clerk_1, @wh_west, 'Stock-In', 50, 14.70, 'closing replenishment', '2026-04-19 16:20:00');
