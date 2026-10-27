-- ============================================================================
-- ORACLE SQL QUERIES DEMONSTRATION SCRIPT
-- Project: Inventory Management System
-- Database: Oracle 19c / 21c / 23ai
-- Description: Comprehensive collection of SQL queries demonstrating fundamental
--              to advanced DBMS query concepts: Joins, Aggregations, Subqueries,
--              Set Operations, and Analytical/Window Functions.
-- ============================================================================

SET DEFINE OFF;
SET PAGESIZE 100;
SET LINESIZE 200;

-- ============================================================================
-- SECTION 1: SELECTION, PROJECTION, FILTERING & PATTERN MATCHING
-- ============================================================================

-- Q1.1: List all active suppliers located in California or Texas sorted by rating descending
SELECT supplier_id, supplier_name, city, rating, status
FROM SUPPLIERS
WHERE status = 'ACTIVE' AND city IN ('San Jose', 'Austin', 'Dallas')
ORDER BY rating DESC;

-- Q1.2: Products with price between $100 and $600 having unit measure 'PCS'
SELECT sku, product_name, cost_price, unit_price, (unit_price - cost_price) AS markup
FROM PRODUCTS
WHERE unit_price BETWEEN 100 AND 600
ORDER BY unit_price ASC;

-- Q1.3: Wildcard search for products containing 'Pro' or 'Enterprise'
SELECT product_id, sku, product_name, unit_price
FROM PRODUCTS
WHERE UPPER(product_name) LIKE '%PRO%' OR UPPER(product_name) LIKE '%ENTERPRISE%';


-- ============================================================================
-- SECTION 2: MULTI-TABLE JOINS (INNER, LEFT OUTER, FULL OUTER, MULTI-JOIN)
-- ============================================================================

-- Q2.1: [INNER JOIN] Comprehensive Product Stock Catalog with Category and Supplier
SELECT 
    p.sku,
    p.product_name,
    c.category_name,
    s.supplier_name,
    p.cost_price,
    p.unit_price,
    i.quantity_on_hand,
    w.warehouse_name
FROM PRODUCTS p
INNER JOIN CATEGORIES c ON p.category_id = c.category_id
INNER JOIN SUPPLIERS s ON p.supplier_id = s.supplier_id
INNER JOIN INVENTORY i ON p.product_id = i.product_id
INNER JOIN WAREHOUSES w ON i.warehouse_id = w.warehouse_id
ORDER BY c.category_name, p.product_name;

-- Q2.2: [LEFT OUTER JOIN] Warehouses and their assigned stock (including empty ones)
SELECT 
    w.warehouse_id,
    w.warehouse_name,
    w.location,
    w.capacity,
    NVL(p.product_name, '--- NO STOCK ALLOCATED ---') AS product_name,
    NVL(i.quantity_on_hand, 0) AS stock_qty
FROM WAREHOUSES w
LEFT OUTER JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
LEFT OUTER JOIN PRODUCTS p ON i.product_id = p.product_id
ORDER BY w.warehouse_name;

-- Q2.3: [MULTI-JOIN with CALCULATED EXPRESSIONS] Detailed Sales Order Breakdown
SELECT 
    o.order_number,
    o.order_date,
    c.customer_name,
    c.customer_type,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    oi.subtotal,
    w.warehouse_name AS fulfilled_from
FROM ORDERS o
JOIN CUSTOMERS c ON o.customer_id = c.customer_id
JOIN ORDER_ITEMS oi ON o.order_id = oi.order_id
JOIN PRODUCTS p ON oi.product_id = p.product_id
JOIN WAREHOUSES w ON oi.warehouse_id = w.warehouse_id
ORDER BY o.order_date DESC, o.order_number;


-- ============================================================================
-- SECTION 3: AGGREGATE FUNCTIONS WITH GROUP BY & HAVING
-- ============================================================================

-- Q3.1: Inventory Valuation and Unit Summary Grouped by Category
SELECT 
    c.category_name,
    COUNT(DISTINCT p.product_id) AS total_products,
    SUM(i.quantity_on_hand) AS total_units_in_stock,
    ROUND(AVG(p.unit_price), 2) AS avg_unit_price,
    ROUND(SUM(i.quantity_on_hand * p.cost_price), 2) AS total_cost_valuation,
    ROUND(SUM(i.quantity_on_hand * p.unit_price), 2) AS total_retail_valuation,
    ROUND(SUM(i.quantity_on_hand * (p.unit_price - p.cost_price)), 2) AS potential_gross_profit
FROM CATEGORIES c
LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
LEFT JOIN INVENTORY i ON p.product_id = i.product_id
GROUP BY c.category_id, c.category_name
ORDER BY total_retail_valuation DESC;

-- Q3.2: [HAVING CLAUSE] Warehouses with Total Stock Units Exceeding 100 Units
SELECT 
    w.warehouse_name,
    w.capacity,
    SUM(i.quantity_on_hand) AS total_stock_held,
    ROUND((SUM(i.quantity_on_hand) / w.capacity) * 100, 2) AS occupancy_rate_pct
FROM WAREHOUSES w
JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.capacity
HAVING SUM(i.quantity_on_hand) > 100
ORDER BY total_stock_held DESC;

-- Q3.3: Total Revenue and Average Order Value per Customer
SELECT 
    c.customer_name,
    c.customer_type,
    COUNT(o.order_id) AS total_orders,
    NVL(SUM(o.total_amount), 0) AS lifetime_spent,
    ROUND(NVL(AVG(o.total_amount), 0), 2) AS average_order_value
FROM CUSTOMERS c
LEFT JOIN ORDERS o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY lifetime_spent DESC;


-- ============================================================================
-- SECTION 4: SUBQUERIES (SINGLE-ROW, MULTI-ROW, CORRELATED)
-- ============================================================================

-- Q4.1: [NON-CORRELATED SUBQUERY] Products priced higher than the average catalog price
SELECT sku, product_name, unit_price
FROM PRODUCTS
WHERE unit_price > (SELECT AVG(unit_price) FROM PRODUCTS)
ORDER BY unit_price DESC;

-- Q4.2: [CORRELATED SUBQUERY] Products that have the highest price within their category
SELECT p.product_id, p.sku, p.product_name, c.category_name, p.unit_price
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
WHERE p.unit_price = (
    SELECT MAX(p2.unit_price)
    FROM PRODUCTS p2
    WHERE p2.category_id = p.category_id
);

-- Q4.3: [EXISTS CLAUSE] Suppliers who currently supply at least one low-stock product
SELECT s.supplier_id, s.supplier_name, s.contact_person, s.phone
FROM SUPPLIERS s
WHERE EXISTS (
    SELECT 1 
    FROM PRODUCTS p
    JOIN INVENTORY i ON p.product_id = i.product_id
    WHERE p.supplier_id = s.supplier_id
    GROUP BY p.product_id, p.reorder_level
    HAVING SUM(i.quantity_on_hand) <= p.reorder_level
);


-- ============================================================================
-- SECTION 5: SET OPERATORS (UNION, INTERSECT, MINUS)
-- ============================================================================

-- Q5.1: [UNION ALL] Master contact directory of both Customers and Suppliers
SELECT 'SUPPLIER' AS entity_type, supplier_name AS contact_name, email, phone, city
FROM SUPPLIERS
UNION ALL
SELECT 'CUSTOMER' AS entity_type, customer_name AS contact_name, email, phone, city
FROM CUSTOMERS
ORDER BY entity_type, contact_name;

-- Q5.2: [MINUS] Warehouses that currently do NOT hold any low-stock items
SELECT warehouse_id, warehouse_name FROM WAREHOUSES
MINUS
SELECT DISTINCT w.warehouse_id, w.warehouse_name
FROM WAREHOUSES w
JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
JOIN PRODUCTS p ON i.product_id = p.product_id
WHERE i.quantity_on_hand < p.reorder_level;


-- ============================================================================
-- SECTION 6: ANALYTIC / WINDOW FUNCTIONS (RANK, DENSE_RANK, RUNNING TOTALS)
-- ============================================================================

-- Q6.1: [RANK & DENSE_RANK] Rank products by unit price within each category
SELECT 
    c.category_name,
    p.product_name,
    p.unit_price,
    RANK() OVER (PARTITION BY p.category_id ORDER BY p.unit_price DESC) AS price_rank,
    DENSE_RANK() OVER (PARTITION BY p.category_id ORDER BY p.unit_price DESC) AS dense_price_rank
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
ORDER BY c.category_name, price_rank;

-- Q6.2: [RUNNING TOTAL] Cumulative sales revenue over time
SELECT 
    order_id,
    order_number,
    order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sales_revenue
FROM ORDERS
WHERE status = 'COMPLETED'
ORDER BY order_date;

-- Q6.3: [PERCENTILE / RATIO TO REPORT] Stock contribution percentage per warehouse
SELECT 
    w.warehouse_name,
    p.product_name,
    i.quantity_on_hand,
    ROUND(RATIO_TO_REPORT(i.quantity_on_hand) OVER(PARTITION BY p.product_id) * 100, 2) AS pct_of_product_stock
FROM INVENTORY i
JOIN WAREHOUSES w ON i.warehouse_id = w.warehouse_id
JOIN PRODUCTS p ON i.product_id = p.product_id
ORDER BY p.product_name, w.warehouse_name;
