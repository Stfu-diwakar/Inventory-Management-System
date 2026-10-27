"""
SQL Query Service for Academic Demonstration and SQL Workbench.
Maintains curated DBMS demonstration queries categorized by concept:
DDL, DML, Multi-Table Joins, Aggregations, Subqueries, Set Operations,
Window Functions, and DCL.
"""

from typing import Dict, Any, List
import pandas as pd
from database.connection import db

DEMO_QUERIES: List[Dict[str, Any]] = [
    {
        "id": "JOIN_1",
        "category": "Multi-Table Joins",
        "title": "3-Way INNER JOIN: Product Stock, Category & Warehouse",
        "concept": "Demonstrates INNER JOIN across PRODUCTS, CATEGORIES, INVENTORY, and WAREHOUSES.",
        "sql": """SELECT 
    p.sku,
    p.product_name,
    c.category_name,
    w.warehouse_name,
    i.quantity_on_hand,
    p.unit_price,
    ROUND(i.quantity_on_hand * p.unit_price, 2) AS stock_retail_value
FROM PRODUCTS p
INNER JOIN CATEGORIES c ON p.category_id = c.category_id
INNER JOIN INVENTORY i ON p.product_id = i.product_id
INNER JOIN WAREHOUSES w ON i.warehouse_id = w.warehouse_id
ORDER BY c.category_name, p.product_name"""
    },
    {
        "id": "JOIN_2",
        "category": "Multi-Table Joins",
        "title": "LEFT OUTER JOIN: Complete Warehouse Inventory Matrix",
        "concept": "Demonstrates LEFT OUTER JOIN with NVL() to retain warehouses even if empty.",
        "sql": """SELECT 
    w.warehouse_name,
    w.location,
    w.capacity,
    NVL(p.product_name, '--- NO INVENTORY ALLOCATED ---') AS product_name,
    NVL(i.quantity_on_hand, 0) AS stock_held
FROM WAREHOUSES w
LEFT OUTER JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
LEFT OUTER JOIN PRODUCTS p ON i.product_id = p.product_id
ORDER BY w.warehouse_name, stock_held DESC"""
    },
    {
        "id": "AGG_1",
        "category": "Aggregations & Grouping",
        "title": "GROUP BY with SUM, AVG, & Computed Valuation by Category",
        "concept": "Demonstrates Aggregate Functions (COUNT, SUM, AVG) and GROUP BY.",
        "sql": """SELECT 
    c.category_name,
    COUNT(DISTINCT p.product_id) AS total_products,
    NVL(SUM(i.quantity_on_hand), 0) AS total_units_in_stock,
    ROUND(AVG(p.unit_price), 2) AS avg_unit_price,
    ROUND(SUM(i.quantity_on_hand * p.cost_price), 2) AS total_cost_valuation,
    ROUND(SUM(i.quantity_on_hand * p.unit_price), 2) AS total_retail_valuation
FROM CATEGORIES c
LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
LEFT JOIN INVENTORY i ON p.product_id = i.product_id
GROUP BY c.category_id, c.category_name
ORDER BY total_retail_valuation DESC"""
    },
    {
        "id": "AGG_2",
        "category": "Aggregations & Grouping",
        "title": "HAVING Clause: Warehouses with Stock Exceeding 100 Units",
        "concept": "Demonstrates filter on aggregated results using the HAVING clause.",
        "sql": """SELECT 
    w.warehouse_name,
    w.capacity,
    SUM(i.quantity_on_hand) AS total_stock_held,
    ROUND((SUM(i.quantity_on_hand) / w.capacity) * 100, 2) AS occupancy_pct
FROM WAREHOUSES w
JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.capacity
HAVING SUM(i.quantity_on_hand) > 100
ORDER BY total_stock_held DESC"""
    },
    {
        "id": "SUB_1",
        "category": "Subqueries",
        "title": "Non-Correlated Subquery: Products Above Average Price",
        "concept": "Demonstrates a subquery in the WHERE clause evaluating the catalog-wide average price.",
        "sql": """SELECT 
    p.sku,
    p.product_name,
    c.category_name,
    p.unit_price,
    ROUND((SELECT AVG(unit_price) FROM PRODUCTS), 2) AS catalog_avg_price,
    ROUND(p.unit_price - (SELECT AVG(unit_price) FROM PRODUCTS), 2) AS variance_from_avg
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
WHERE p.unit_price > (SELECT AVG(unit_price) FROM PRODUCTS)
ORDER BY p.unit_price DESC"""
    },
    {
        "id": "SUB_2",
        "category": "Subqueries",
        "title": "Correlated Subquery: Maximum Priced Product per Category",
        "concept": "Demonstrates a correlated subquery referencing outer query category_id.",
        "sql": """SELECT 
    p.product_id,
    p.sku,
    p.product_name,
    c.category_name,
    p.unit_price
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
WHERE p.unit_price = (
    SELECT MAX(p2.unit_price)
    FROM PRODUCTS p2
    WHERE p2.category_id = p.category_id
)
ORDER BY p.unit_price DESC"""
    },
    {
        "id": "SET_1",
        "category": "Set Operations",
        "title": "UNION ALL: Unified Stakeholder Contact Directory",
        "concept": "Demonstrates UNION ALL combining Suppliers and Customers into a polymorphic view.",
        "sql": """SELECT 'SUPPLIER' AS entity_type, supplier_name AS contact_name, email, phone, city
FROM SUPPLIERS
UNION ALL
SELECT 'CUSTOMER' AS entity_type, customer_name AS contact_name, email, phone, city
FROM CUSTOMERS
ORDER BY entity_type, contact_name"""
    },
    {
        "id": "WIN_1",
        "category": "Window / Analytic Functions",
        "title": "DENSE_RANK() & PARTITION BY: Product Price Rank within Category",
        "concept": "Demonstrates Oracle Analytical Window function DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...)",
        "sql": """SELECT 
    c.category_name,
    p.product_name,
    p.unit_price,
    DENSE_RANK() OVER (PARTITION BY p.category_id ORDER BY p.unit_price DESC) AS price_rank_in_category
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
ORDER BY c.category_name, price_rank_in_category"""
    },
    {
        "id": "WIN_2",
        "category": "Window / Analytic Functions",
        "title": "Cumulative Sales Running Total (Window Frame)",
        "concept": "Demonstrates running aggregation using SUM(...) OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
        "sql": """SELECT 
    order_id,
    order_number,
    TO_CHAR(order_date, 'YYYY-MM-DD HH24:MI') AS order_date,
    total_amount,
    SUM(total_amount) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sales_revenue
FROM ORDERS
WHERE status = 'COMPLETED'
ORDER BY order_date"""
    },
    {
        "id": "VIEW_1",
        "category": "Database Views",
        "title": "Analytical View: Low Stock Reorder Alerts",
        "concept": "Queries the predefined database view VW_LOW_STOCK_ALERTS.",
        "sql": """SELECT 
    product_id,
    sku,
    product_name,
    category_name,
    supplier_name,
    total_stock,
    reorder_level,
    units_needed,
    cost_price,
    stock_status
FROM VW_LOW_STOCK_ALERTS
ORDER BY units_needed DESC"""
    }
]

class QueryService:
    @staticmethod
    def get_demo_queries() -> List[Dict[str, Any]]:
        return DEMO_QUERIES

    @staticmethod
    def execute_custom_query(sql: str) -> pd.DataFrame:
        """Executes custom user-provided SQL query safely."""
        cleaned_sql = sql.strip().rstrip(";")
        return db.execute_query(cleaned_sql)
