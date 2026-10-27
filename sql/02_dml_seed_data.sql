-- ============================================================================
-- ORACLE SQL DML (DATA MANIPULATION LANGUAGE) SCRIPT
-- Project: Inventory Management System
-- Database: Oracle 19c / 21c / 23ai
-- Description: Populates all tables with realistic enterprise inventory data.
-- ============================================================================

SET DEFINE OFF;
SET FEEDBACK ON;

-- ----------------------------------------------------------------------------
-- 1. SEED CATEGORIES
-- ----------------------------------------------------------------------------
INSERT INTO CATEGORIES (category_name, description) VALUES ('Laptops & Computers', 'High performance enterprise laptops, desktops, and workstations');
INSERT INTO CATEGORIES (category_name, description) VALUES ('Computer Peripherals', 'Keyboards, mice, webcams, headsets, and docking stations');
INSERT INTO CATEGORIES (category_name, description) VALUES ('Networking Equipment', 'Enterprise switches, routers, access points, and patch cables');
INSERT INTO CATEGORIES (category_name, description) VALUES ('Data Storage & Memory', 'NVMe SSDs, external hard drives, RAM modules, and flash drives');
INSERT INTO CATEGORIES (category_name, description) VALUES ('Office Ergonomics', 'Adjustable standing desks, ergonomic chairs, and monitor arms');
INSERT INTO CATEGORIES (category_name, description) VALUES ('Displays & Monitors', '4K UHD monitors, ultrawide gaming and productivity displays');

-- ----------------------------------------------------------------------------
-- 2. SEED SUPPLIERS
-- ----------------------------------------------------------------------------
INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status) 
VALUES ('Apex Silicon Distributing', 'Marcus Vance', 'marcus@apexsilicon.com', '+1-555-0144', '100 Technology Parkway', 'San Jose', 4.8, 'ACTIVE');

INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status) 
VALUES ('Global Peripheral Corp', 'Sarah Jenkins', 'sarah.j@globalperiph.com', '+1-555-0182', '45 Industrial Way', 'Chicago', 4.6, 'ACTIVE');

INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status) 
VALUES ('Quantum Network Labs', 'David Chen', 'dchen@quantumnet.io', '+1-555-0291', '78 Telecom Blvd', 'Austin', 4.9, 'ACTIVE');

INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status) 
VALUES ('ErgoWork Solutions', 'Elena Rostova', 'elena@ergowork.org', '+1-555-0377', '12 Workspace Road', 'Boston', 4.5, 'ACTIVE');

INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status) 
VALUES ('SolidState Logistics', 'Liam O''Connor', 'liam@solidstatelog.com', '+1-555-0466', '88 Storage Ave', 'Seattle', 4.7, 'ACTIVE');

-- ----------------------------------------------------------------------------
-- 3. SEED WAREHOUSES
-- ----------------------------------------------------------------------------
INSERT INTO WAREHOUSES (warehouse_name, location, capacity, manager_name, contact_number, status)
VALUES ('Central Mega-Hub', 'Building A, 100 Logistics Way, New York, NY', 50000, 'Robert Sterling', '+1-212-555-0111', 'ACTIVE');

INSERT INTO WAREHOUSES (warehouse_name, location, capacity, manager_name, contact_number, status)
VALUES ('West Coast Distribution', 'Bay Area Logistics Center, Oakland, CA', 35000, 'Amanda Reyes', '+1-510-555-0222', 'ACTIVE');

INSERT INTO WAREHOUSES (warehouse_name, location, capacity, manager_name, contact_number, status)
VALUES ('Midwest Regional Depot', 'Zone 4, O''Hare Cargo Complex, Chicago, IL', 25000, 'Kenji Sato', '+1-312-555-0333', 'ACTIVE');

INSERT INTO WAREHOUSES (warehouse_name, location, capacity, manager_name, contact_number, status)
VALUES ('Southern Fulfillment Hub', 'DFW Commerce Park, Dallas, TX', 30000, 'Diana Martinez', '+1-214-555-0444', 'ACTIVE');

-- ----------------------------------------------------------------------------
-- 4. SEED CUSTOMERS
-- ----------------------------------------------------------------------------
INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
VALUES ('NexGen Technologies Inc', 'procurement@nexgen.com', '+1-555-1101', '500 Innovation Way', 'San Francisco', 'CORPORATE');

INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
VALUES ('Metro Digital Retail', 'purchasing@metrodigital.store', '+1-555-1102', '120 Market Square', 'Chicago', 'WHOLESALE');

INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
VALUES ('Horizon Cloud Systems', 'ops@horizoncloud.net', '+1-555-1103', '77 Cloud Summit Blvd', 'Denver', 'CORPORATE');

INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
VALUES ('Alexander Wright', 'alex.wright@gmail.com', '+1-555-1104', '42 Maple Street', 'Austin', 'RETAIL');

INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
VALUES ('Sophia Patel', 'spatel@consulting.org', '+1-555-1105', '88 Beacon Hill', 'Boston', 'RETAIL');

-- ----------------------------------------------------------------------------
-- 5. SEED PRODUCTS
-- ----------------------------------------------------------------------------
INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-LAP-001', 'ThinkStation Pro Laptop 16" 32GB RAM', 1, 1, 950.00, 1399.99, 15, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-LAP-002', 'UltraBook Carbon 14" Core i7', 1, 1, 780.00, 1149.50, 12, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-DIS-001', 'UltraFine 27" 4K IPS Ergonomic Monitor', 6, 2, 240.00, 389.00, 20, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-DIS-002', 'Curved Gaming & Productivity Display 34"', 6, 2, 380.00, 599.00, 10, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-PER-001', 'MasterKey Mechanical Wireless Keyboard', 2, 2, 55.00, 99.99, 25, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-PER-002', 'ErgoPrecision Multi-Device Mouse', 2, 2, 32.00, 64.99, 30, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-NET-001', 'Enterprise 24-Port Gigabit PoE Managed Switch', 3, 3, 210.00, 349.00, 8, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-NET-002', 'Tri-Band Wi-Fi 7 Enterprise Mesh Router', 3, 3, 130.00, 229.00, 12, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-STO-001', 'PCIe Gen5 NVMe M.2 2TB High-Speed SSD', 4, 5, 85.00, 149.99, 30, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-STO-002', 'Rugged External Hard Drive 4TB USB 3.2', 4, 5, 60.00, 109.99, 15, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-ERG-001', 'Executive Dual-Motor Electric Standing Desk', 5, 4, 290.00, 499.00, 6, 'PCS');

INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
VALUES ('SKU-ERG-002', 'ErgoBreeze High-Back Lumbar Mesh Chair', 5, 4, 160.00, 289.00, 8, 'PCS');

-- ----------------------------------------------------------------------------
-- 6. SEED INVENTORY (STOCK ON HAND ACROSS WAREHOUSES)
-- ----------------------------------------------------------------------------
-- ThinkStation Pro (Prod 1)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (1, 1, 45);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (1, 2, 28);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (1, 3, 14);

-- UltraBook Carbon (Prod 2)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (2, 1, 30);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (2, 4, 18);

-- UltraFine 27" Monitor (Prod 3)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (3, 1, 65);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (3, 2, 40);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (3, 3, 22);

-- Curved Gaming Display 34" (Prod 4) - Intentionally Low Stock for Alert Demo
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (4, 1, 4);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (4, 2, 3);

-- Keyboards & Mice (Prods 5 & 6)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (5, 1, 120);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (5, 2, 85);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (6, 1, 140);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (6, 3, 60);

-- Networking Switch (Prod 7) - Low Stock
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (7, 1, 3);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (7, 2, 2);

-- Wi-Fi 7 Router (Prod 8)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (8, 1, 35);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (8, 4, 25);

-- Storage SSDs & HDDs (Prods 9 & 10)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (9, 1, 90);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (9, 2, 75);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (10, 1, 50);

-- Ergonomics Standing Desk & Chair (Prods 11 & 12)
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (11, 1, 12);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (11, 3, 8);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (12, 1, 20);
INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand) VALUES (12, 4, 15);

-- ----------------------------------------------------------------------------
-- 7. SEED ORDERS & ORDER ITEMS
-- ----------------------------------------------------------------------------
-- Order 1: Corporate Order for NexGen Tech
INSERT INTO ORDERS (order_number, customer_id, order_date, total_amount, tax_amount, status, payment_method)
VALUES ('ORD-2026-0001', 1, TIMESTAMP '2026-10-15 09:30:00', 17889.90, 1431.19, 'COMPLETED', 'BANK_TRANSFER');

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (1, 1, 1, 10, 1399.99, 13999.90);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (1, 3, 1, 10, 389.00, 3890.00);

-- Order 2: Wholesale Order for Metro Digital Retail
INSERT INTO ORDERS (order_number, customer_id, order_date, total_amount, tax_amount, status, payment_method)
VALUES ('ORD-2026-0002', 2, TIMESTAMP '2026-10-18 14:15:00', 4999.50, 399.96, 'COMPLETED', 'CREDIT_CARD');

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (2, 5, 2, 30, 99.99, 2999.70);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (2, 6, 2, 20, 64.99, 1299.80);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (2, 9, 2, 5, 149.99, 749.95);

-- Order 3: Horizon Cloud Systems
INSERT INTO ORDERS (order_number, customer_id, order_date, total_amount, tax_amount, status, payment_method)
VALUES ('ORD-2026-0003', 3, TIMESTAMP '2026-10-22 11:45:00', 2792.00, 223.36, 'PROCESSING', 'BANK_TRANSFER');

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (3, 7, 1, 4, 349.00, 1396.00);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (3, 8, 1, 6, 229.00, 1374.00);

-- Order 4: Retail Purchase by Alexander Wright
INSERT INTO ORDERS (order_number, customer_id, order_date, total_amount, tax_amount, status, payment_method)
VALUES ('ORD-2026-0004', 4, TIMESTAMP '2026-10-24 16:20:00', 1688.99, 135.12, 'COMPLETED', 'UPI');

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (4, 2, 1, 1, 1149.50, 1149.50);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (4, 5, 1, 1, 99.99, 99.99);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (4, 3, 1, 1, 389.00, 389.00);

-- Order 5: Sophia Patel (Pending)
INSERT INTO ORDERS (order_number, customer_id, order_date, total_amount, tax_amount, status, payment_method)
VALUES ('ORD-2026-0005', 5, CURRENT_TIMESTAMP, 788.00, 63.04, 'PENDING', 'CREDIT_CARD');

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (5, 11, 1, 1, 499.00, 499.00);

INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
VALUES (5, 12, 1, 1, 289.00, 289.00);

-- ----------------------------------------------------------------------------
-- 8. SEED STOCK TRANSACTIONS (AUDIT TRAIL)
-- ----------------------------------------------------------------------------
INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
VALUES (1, 1, 'STOCK_IN', 55, 'PO-2026-8801', 'Initial bulk purchase order received from Apex Silicon', 'INVENTORY_ADMIN');

INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
VALUES (1, 1, 'STOCK_OUT', -10, 'ORD-2026-0001', 'Customer shipment for NexGen Technologies', 'LOGISTICS_LEAD');

INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
VALUES (3, 1, 'TRANSFER_OUT', -15, 'TRF-NY-SF-01', 'Internal transfer to West Coast Distribution', 'LOGISTICS_LEAD');

INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
VALUES (3, 2, 'TRANSFER_IN', 15, 'TRF-NY-SF-01', 'Transfer received at West Coast Distribution', 'LOGISTICS_LEAD');

INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
VALUES (7, 1, 'ADJUSTMENT', -2, 'AUD-Q3-2026', 'Annual physical inventory count adjustment (damaged units)', 'INVENTORY_AUDITOR');

-- ----------------------------------------------------------------------------
-- 9. SEED AUDIT LOGS
-- ----------------------------------------------------------------------------
INSERT INTO AUDIT_LOGS (table_name, action_type, record_id, details, performed_by)
VALUES ('SYSTEM', 'INSERT', 'INIT_001', 'System database tables and schemas initialized successfully.', 'SYSTEM_DBA');

INSERT INTO AUDIT_LOGS (table_name, action_type, record_id, details, performed_by)
VALUES ('PRODUCTS', 'UPDATE', '1', 'Price updated for SKU SKU-LAP-001. Promotional retail pricing activated.', 'INVENTORY_ADMIN');

COMMIT;
