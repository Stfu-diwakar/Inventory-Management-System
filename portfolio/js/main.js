/**
 * ApexStock Enterprise — Portfolio Interactive Engine
 * Oracle SQL Simulation, ERD Inspector, UI Tour & Viva Guide
 */

// ============================================================================
// CURATED DEMO QUERIES & SIMULATED ORACLE DATASETS
// ============================================================================
const DEMO_QUERIES = {
  JOIN_1: {
    category: "Multi-Table Relational Joins",
    description: "4-Way INNER JOIN linking PRODUCTS, CATEGORIES, INVENTORY, and WAREHOUSES with computed valuation.",
    sql: `SELECT 
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
ORDER BY c.category_name, p.product_name;`,
    headers: ["SKU", "PRODUCT_NAME", "CATEGORY_NAME", "WAREHOUSE_NAME", "QTY_ON_HAND", "UNIT_PRICE", "RETAIL_VALUE"],
    rows: [
      ["SKU-ELC-001", "Industrial PLC Controller v2", "Industrial Automation", "Central Hub (Austin)", "45", "$849.00", "$38,205.00"],
      ["SKU-ELC-001", "Industrial PLC Controller v2", "Industrial Automation", "Pacific Depot (Seattle)", "28", "$849.00", "$23,772.00"],
      ["SKU-ELC-002", "Opto-Isolated Relay Board", "Industrial Automation", "Central Hub (Austin)", "120", "$64.50", "$7,740.00"],
      ["SKU-SNS-014", "Ultrasonic Range Transducer", "Precision Sensorics", "Central Hub (Austin)", "110", "$189.50", "$20,845.00"],
      ["SKU-SNS-014", "Ultrasonic Range Transducer", "Precision Sensorics", "Atlantic Logistics (Newark)", "40", "$189.50", "$7,580.00"],
      ["SKU-PWR-009", "3-Phase Harmonic Inverter", "Power Distribution", "Pacific Depot (Seattle)", "15", "$1,240.00", "$18,600.00"]
    ],
    cost: "4",
    cardinality: "32",
    plan: `------------------------------------------------------------------------------------------
| Id  | Operation                     | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT              |             |    32 |  2496 |     4   (0)| 00:00:01 |
|   1 |  SORT ORDER BY                |             |    32 |  2496 |     4   (0)| 00:00:01 |
|*  2 |   HASH JOIN                   |             |    32 |  2496 |     4   (0)| 00:00:01 |
|   3 |    TABLE ACCESS FULL          | WAREHOUSES  |     4 |   128 |     2   (0)| 00:00:01 |
|*  4 |    HASH JOIN                  |             |    32 |  1472 |     2   (0)| 00:00:01 |
|   5 |     TABLE ACCESS FULL         | INVENTORY   |    32 |   512 |     2   (0)| 00:00:01 |
|   6 |     TABLE ACCESS FULL         | PRODUCTS    |    24 |   720 |     2   (0)| 00:00:01 |
------------------------------------------------------------------------------------------
Predicate Information (identified by operation id):
---------------------------------------------------
   2 - access("I"."WAREHOUSE_ID"="W"."WAREHOUSE_ID")
   4 - access("P"."PRODUCT_ID"="I"."PRODUCT_ID")`
  },

  JOIN_2: {
    category: "Multi-Table Relational Joins",
    description: "LEFT OUTER JOIN with NVL() ensuring zero-stock and unassigned warehouses are not lost in reports.",
    sql: `SELECT 
    w.warehouse_name,
    w.location,
    w.capacity,
    NVL(p.product_name, '--- NO INVENTORY ALLOCATED ---') AS product_name,
    NVL(i.quantity_on_hand, 0) AS stock_held
FROM WAREHOUSES w
LEFT OUTER JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
LEFT OUTER JOIN PRODUCTS p ON i.product_id = p.product_id
ORDER BY w.warehouse_name, stock_held DESC;`,
    headers: ["WAREHOUSE_NAME", "LOCATION", "CAPACITY", "PRODUCT_NAME", "STOCK_HELD"],
    rows: [
      ["Atlantic Logistics", "Newark, NJ", "15,000", "Industrial PLC Controller v2", "12"],
      ["Atlantic Logistics", "Newark, NJ", "15,000", "Ultrasonic Range Transducer", "40"],
      ["Central Hub", "Austin, TX", "25,000", "Opto-Isolated Relay Board", "120"],
      ["Central Hub", "Austin, TX", "25,000", "Industrial PLC Controller v2", "45"],
      ["Gulf Cold Storage", "Houston, TX", "8,000", "--- NO INVENTORY ALLOCATED ---", "0"],
      ["Pacific Depot", "Seattle, WA", "18,000", "3-Phase Harmonic Inverter", "15"]
    ],
    cost: "3",
    cardinality: "28",
    plan: `-------------------------------------------------------------------------------------------
| Id  | Operation                      | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |             |    28 |  1960 |     3   (0)| 00:00:01 |
|   1 |  SORT ORDER BY                 |             |    28 |  1960 |     3   (0)| 00:00:01 |
|*  2 |   HASH JOIN OUTER              |             |    28 |  1960 |     3   (0)| 00:00:01 |
|   3 |    TABLE ACCESS FULL           | WAREHOUSES  |     4 |   160 |     2   (0)| 00:00:01 |
|   4 |    VIEW                        |             |    28 |   840 |     2   (0)| 00:00:01 |
|   5 |     TABLE ACCESS FULL          | INVENTORY   |    28 |   448 |     2   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------`
  },

  AGG_1: {
    category: "Aggregations & Grouping",
    description: "GROUP BY category computing total products, stock units, average price, cost valuation and retail valuation.",
    sql: `SELECT 
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
ORDER BY total_retail_valuation DESC;`,
    headers: ["CATEGORY_NAME", "TOTAL_PRODUCTS", "UNITS_IN_STOCK", "AVG_PRICE", "COST_VALUATION", "RETAIL_VALUATION"],
    rows: [
      ["Industrial Automation", "8", "410", "$524.50", "$142,500.00", "$215,045.00"],
      ["Power Distribution", "6", "185", "$890.00", "$98,200.00", "$164,650.00"],
      ["Precision Sensorics", "7", "340", "$145.20", "$32,100.00", "$49,368.00"],
      ["Cables & Interconnects", "3", "890", "$28.00", "$12,450.00", "$24,920.00"]
    ],
    cost: "5",
    cardinality: "4",
    plan: `-------------------------------------------------------------------------------------------
| Id  | Operation                      | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |             |     4 |   312 |     5  (20)| 00:00:01 |
|   1 |  SORT ORDER BY                 |             |     4 |   312 |     5  (20)| 00:00:01 |
|   2 |   HASH GROUP BY                |             |     4 |   312 |     5  (20)| 00:00:01 |
|*  3 |    HASH JOIN OUTER             |             |    32 |  2496 |     4   (0)| 00:00:01 |
|   4 |     TABLE ACCESS FULL          | CATEGORIES  |     4 |    80 |     2   (0)| 00:00:01 |
|   5 |     TABLE ACCESS FULL          | PRODUCTS    |    24 |   720 |     2   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------`
  },

  AGG_2: {
    category: "Aggregations & Grouping",
    description: "Post-aggregation filtering using HAVING to identify facilities carrying stock greater than 100 units.",
    sql: `SELECT 
    w.warehouse_name,
    w.capacity,
    SUM(i.quantity_on_hand) AS total_stock_held,
    ROUND((SUM(i.quantity_on_hand) / w.capacity) * 100, 2) AS occupancy_pct
FROM WAREHOUSES w
JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.capacity
HAVING SUM(i.quantity_on_hand) > 100
ORDER BY total_stock_held DESC;`,
    headers: ["WAREHOUSE_NAME", "CAPACITY", "TOTAL_STOCK_HELD", "OCCUPANCY_PCT"],
    rows: [
      ["Central Hub (Austin)", "25,000", "845 units", "3.38%"],
      ["Pacific Depot (Seattle)", "18,000", "420 units", "2.33%"],
      ["Atlantic Logistics (Newark)", "15,000", "285 units", "1.90%"]
    ],
    cost: "3",
    cardinality: "3",
    plan: `------------------------------------------------------------------------------------------
| Id  | Operation                    | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |             |     3 |   144 |     3   (0)| 00:00:01 |
|*  1 |  FILTER                      |             |       |       |            |          |
|   2 |   HASH GROUP BY              |             |     3 |   144 |     3   (0)| 00:00:01 |
|*  3 |    HASH JOIN                 |             |    28 |  1344 |     2   (0)| 00:00:01 |
|   4 |     TABLE ACCESS FULL        | WAREHOUSES  |     4 |   128 |     2   (0)| 00:00:01 |
|   5 |     TABLE ACCESS FULL        | INVENTORY   |    28 |   448 |     2   (0)| 00:00:01 |
------------------------------------------------------------------------------------------`
  },

  WIN_1: {
    category: "Analytic & Window Functions",
    description: "DENSE_RANK() OVER (PARTITION BY category_id ORDER BY unit_price DESC) ranking catalog prices.",
    sql: `SELECT 
    c.category_name,
    p.sku,
    p.product_name,
    p.unit_price,
    DENSE_RANK() OVER (
        PARTITION BY p.category_id 
        ORDER BY p.unit_price DESC
    ) AS price_rank_in_category
FROM PRODUCTS p
JOIN CATEGORIES c ON p.category_id = c.category_id
ORDER BY c.category_name, price_rank_in_category;`,
    headers: ["CATEGORY_NAME", "SKU", "PRODUCT_NAME", "UNIT_PRICE", "PRICE_RANK"],
    rows: [
      ["Industrial Automation", "SKU-ELC-001", "Industrial PLC Controller v2", "$849.00", "1"],
      ["Industrial Automation", "SKU-ELC-003", "Modular Expansion Rack", "$340.00", "2"],
      ["Industrial Automation", "SKU-ELC-002", "Opto-Isolated Relay Board", "$64.50", "3"],
      ["Power Distribution", "SKU-PWR-009", "3-Phase Harmonic Inverter", "$1,240.00", "1"],
      ["Power Distribution", "SKU-PWR-004", "Surge Protection Module", "$310.00", "2"],
      ["Precision Sensorics", "SKU-SNS-014", "Ultrasonic Range Transducer", "$189.50", "1"],
      ["Precision Sensorics", "SKU-SNS-008", "Optical Laser Proximity Switch", "$124.00", "2"]
    ],
    cost: "4",
    cardinality: "24",
    plan: `-------------------------------------------------------------------------------------------
| Id  | Operation                      | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |             |    24 |  1680 |     4  (25)| 00:00:01 |
|   1 |  WINDOW SORT                   |             |    24 |  1680 |     4  (25)| 00:00:01 |
|*  2 |   HASH JOIN                    |             |    24 |  1680 |     3   (0)| 00:00:01 |
|   3 |    TABLE ACCESS FULL           | CATEGORIES  |     4 |    80 |     2   (0)| 00:00:01 |
|   4 |    TABLE ACCESS FULL           | PRODUCTS    |    24 |  1200 |     2   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------`
  },

  WIN_2: {
    category: "Analytic & Window Functions",
    description: "Cumulative running total using SUM(total_amount) OVER (ORDER BY order_date ROWS UNBOUNDED PRECEDING).",
    sql: `SELECT 
    order_id,
    order_number,
    TO_CHAR(order_date, 'YYYY-MM-DD') AS order_date,
    total_amount,
    SUM(total_amount) OVER (
        ORDER BY order_date, order_id 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_revenue_total
FROM ORDERS
ORDER BY order_date ASC;`,
    headers: ["ORDER_ID", "ORDER_NUMBER", "ORDER_DATE", "TOTAL_AMOUNT", "CUMULATIVE_REVENUE"],
    rows: [
      ["101", "ORD-202610-0081", "2026-10-14", "$3,450.00", "$3,450.00"],
      ["102", "ORD-202610-0082", "2026-10-18", "$1,280.00", "$4,730.00"],
      ["103", "ORD-202610-0083", "2026-10-21", "$8,940.00", "$13,670.00"],
      ["104", "ORD-202610-0084", "2026-10-24", "$4,120.00", "$17,790.00"],
      ["105", "ORD-202610-0085", "2026-10-27", "$6,350.00", "$24,140.00"]
    ],
    cost: "3",
    cardinality: "15",
    plan: `------------------------------------------------------------------------------------------
| Id  | Operation                    | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |             |    15 |   690 |     3  (33)| 00:00:01 |
|   1 |  WINDOW SORT                 |             |    15 |   690 |     3  (33)| 00:00:01 |
|   2 |   TABLE ACCESS FULL          | ORDERS      |    15 |   690 |     2   (0)| 00:00:01 |
------------------------------------------------------------------------------------------`
  },

  SUB_1: {
    category: "Subqueries & Predicates",
    description: "Correlated subquery retrieving the most expensive product within each respective category.",
    sql: `SELECT 
    p1.product_id,
    p1.sku,
    p1.product_name,
    p1.unit_price,
    c.category_name
FROM PRODUCTS p1
JOIN CATEGORIES c ON p1.category_id = c.category_id
WHERE p1.unit_price = (
    SELECT MAX(p2.unit_price)
    FROM PRODUCTS p2
    WHERE p2.category_id = p1.category_id
)
ORDER BY p1.unit_price DESC;`,
    headers: ["PRODUCT_ID", "SKU", "PRODUCT_NAME", "UNIT_PRICE", "CATEGORY_NAME"],
    rows: [
      ["109", "SKU-PWR-009", "3-Phase Harmonic Inverter", "$1,240.00", "Power Distribution"],
      ["101", "SKU-ELC-001", "Industrial PLC Controller v2", "$849.00", "Industrial Automation"],
      ["114", "SKU-SNS-014", "Ultrasonic Range Transducer", "$189.50", "Precision Sensorics"],
      ["105", "SKU-CBL-005", "Shielded Industrial Cat6A Spool", "$94.00", "Cables & Interconnects"]
    ],
    cost: "6",
    cardinality: "4",
    plan: `-------------------------------------------------------------------------------------------
| Id  | Operation                      | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |             |     4 |   280 |     6   (0)| 00:00:01 |
|*  1 |  HASH JOIN                     |             |     4 |   280 |     6   (0)| 00:00:01 |
|   2 |   VIEW                         |             |     4 |   104 |     4   (0)| 00:00:01 |
|   3 |    HASH GROUP BY               |             |     4 |   104 |     4   (0)| 00:00:01 |
|   4 |     TABLE ACCESS FULL          | PRODUCTS    |    24 |   624 |     2   (0)| 00:00:01 |
|*  5 |   HASH JOIN                    |             |    24 |  1056 |     2   (0)| 00:00:01 |
|   6 |    TABLE ACCESS FULL           | CATEGORIES  |     4 |    80 |     2   (0)| 00:00:01 |
|   7 |    TABLE ACCESS FULL           | PRODUCTS    |    24 |   624 |     2   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------`
  },

  MERGE_1: {
    category: "Atomic DML & Concurrency",
    description: "Atomic MERGE (Upsert) synchronizing stock without client-side race conditions or separate SELECT checks.",
    sql: `MERGE INTO INVENTORY target
USING (
    SELECT 
        101 AS product_id, 
        2   AS warehouse_id, 
        50  AS new_quantity
    FROM DUAL
) source
ON (target.product_id = source.product_id AND target.warehouse_id = source.warehouse_id)
WHEN MATCHED THEN
    UPDATE SET 
        target.quantity_on_hand = target.quantity_on_hand + source.new_quantity,
        target.last_updated = SYSTIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (product_id, warehouse_id, quantity_on_hand, last_updated)
    VALUES (source.product_id, source.warehouse_id, source.new_quantity, SYSTIMESTAMP);`,
    headers: ["OPERATION_PERFORMED", "TARGET_TABLE", "MATCHED_STATUS", "ROWS_MERGED", "RESULT"],
    rows: [
      ["MERGE (UPSERT)", "INVENTORY", "MATCHED (KEY EXISTS)", "1 row updated", "SUCCESS (COMMIT)"]
    ],
    cost: "2",
    cardinality: "1",
    plan: `------------------------------------------------------------------------------------------
| Id  | Operation                    | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | MERGE STATEMENT              |             |     1 |    42 |     2   (0)| 00:00:01 |
|   1 |  MERGE                       | INVENTORY   |       |       |            |          |
|   2 |   VIEW                       |             |       |       |            |          |
|*  3 |    HASH JOIN OUTER           |             |     1 |    42 |     2   (0)| 00:00:01 |
|   4 |     TABLE ACCESS FULL        | DUAL        |     1 |     2 |     2   (0)| 00:00:01 |
|   5 |     TABLE ACCESS BY INDEX ROW| INVENTORY   |     1 |    40 |     1   (0)| 00:00:01 |
------------------------------------------------------------------------------------------`
  },

  DCL_1: {
    category: "Data Control Language (DCL)",
    description: "Querying Oracle Data Dictionary view USER_TAB_PRIVS_MADE to inspect granted role privileges.",
    sql: `SELECT 
    grantee,
    table_name,
    privilege,
    grantable
FROM USER_TAB_PRIVS_MADE
WHERE grantee LIKE 'INV_%'
ORDER BY grantee, table_name;`,
    headers: ["GRANTEE_ROLE", "TABLE_NAME", "PRIVILEGE", "GRANTABLE"],
    rows: [
      ["INV_ADMIN_ROLE", "ALL_PROJECT_TABLES", "ALL PRIVILEGES", "YES"],
      ["INV_AUDITOR_ROLE", "AUDIT_LOGS", "SELECT", "NO"],
      ["INV_AUDITOR_ROLE", "INVENTORY", "SELECT", "NO"],
      ["INV_AUDITOR_ROLE", "ORDERS", "SELECT", "NO"],
      ["INV_MANAGER_ROLE", "INVENTORY", "SELECT, UPDATE, INSERT", "NO"],
      ["INV_MANAGER_ROLE", "PRODUCTS", "SELECT, UPDATE, INSERT", "NO"],
      ["INV_STAFF_ROLE", "ORDERS", "INSERT, SELECT", "NO"],
      ["INV_STAFF_ROLE", "ORDER_ITEMS", "INSERT, SELECT", "NO"],
      ["INV_STAFF_ROLE", "PRODUCTS", "SELECT", "NO"]
    ],
    cost: "2",
    cardinality: "9",
    plan: `-------------------------------------------------------------------------------------------
| Id  | Operation                      | Name                 | Rows  | Cost (%CPU)| Time     |
-------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT               |                      |     9 |     2   (0)| 00:00:01 |
|   1 |  TABLE ACCESS FULL             | USER_TAB_PRIVS_MADE  |     9 |     2   (0)| 00:00:01 |
-------------------------------------------------------------------------------------------`
  },

  AUDIT_1: {
    category: "Autonomous Triggers & Audit",
    description: "Inspecting tamper-proof price audit trail populated by trigger TRG_AUDIT_PRODUCT_CHANGES.",
    sql: `SELECT 
    log_id,
    table_name,
    action_type,
    record_id,
    performed_by,
    TO_CHAR(action_date, 'YYYY-MM-DD HH24:MI:SS') AS timestamp_logged,
    details
FROM AUDIT_LOGS
ORDER BY action_date DESC;`,
    headers: ["LOG_ID", "TABLE", "ACTION", "RECORD_ID", "BY_USER", "LOGGED_TIMESTAMP", "AUDIT_DETAILS"],
    rows: [
      ["501", "PRODUCTS", "UPDATE", "101", "INV_ADMIN", "2026-10-27 14:22:08", "Price updated for SKU-ELC-001. Old: $799.00, New: $849.00."],
      ["502", "PRODUCTS", "UPDATE", "114", "INV_ADMIN", "2026-10-27 15:10:44", "Price updated for SKU-SNS-014. Old: $175.00, New: $189.50."],
      ["503", "PRODUCTS", "DELETE", "199", "INV_ADMIN", "2026-10-27 16:04:12", "Archived product SKU-LEGACY-09 before cascade drop."]
    ],
    cost: "2",
    cardinality: "3",
    plan: `------------------------------------------------------------------------------------------
| Id  | Operation                    | Name        | Rows  | Bytes | Cost (%CPU)| Time     |
------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT             |             |     3 |   450 |     2   (0)| 00:00:01 |
|   1 |  SORT ORDER BY               |             |     3 |   450 |     2   (0)| 00:00:01 |
|   2 |   TABLE ACCESS FULL          | AUDIT_LOGS  |     3 |   450 |     2   (0)| 00:00:01 |
------------------------------------------------------------------------------------------`
  }
};

// ============================================================================
// ERD TABLE DEFINITIONS & DDL METADATA
// ============================================================================
const TABLE_METADATA = {
  CATEGORIES: {
    badge: "Master Entity",
    desc: "Classifies inventory into functional engineering verticals (e.g. Industrial Automation, Power Distribution, Precision Sensorics). Ensures 3NF by isolating category descriptions from products.",
    columns: [
      { name: "category_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "category_name", type: "VARCHAR2(50)", constraint: "UNIQUE, NOT NULL", rule: "Domain uniqueness for lookup" },
      { name: "description", type: "VARCHAR2(255)", constraint: "NULLABLE", rule: "Optional vertical notes" },
      { name: "created_at", type: "TIMESTAMP", constraint: "DEFAULT SYSTIMESTAMP", rule: "Audit timestamp" }
    ],
    ddl: `CREATE TABLE CATEGORIES (
    category_id   NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    category_name VARCHAR2(50) NOT NULL UNIQUE,
    description   VARCHAR2(255),
    created_at    TIMESTAMP DEFAULT SYSTIMESTAMP
);`
  },

  SUPPLIERS: {
    badge: "Master Entity",
    desc: "Maintains vendor registries with vendor credit ratings (1-5 scale) and location data. Linked to products to track procurement lead-times.",
    columns: [
      { name: "supplier_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "supplier_name", type: "VARCHAR2(100)", constraint: "NOT NULL", rule: "Corporate trade name" },
      { name: "contact_person", type: "VARCHAR2(100)", constraint: "NULLABLE", rule: "Primary sales rep" },
      { name: "email", type: "VARCHAR2(100)", constraint: "UNIQUE, NOT NULL", rule: "Unique vendor email" },
      { name: "phone", type: "VARCHAR2(20)", constraint: "NULLABLE", rule: "International E.164 phone" },
      { name: "city", type: "VARCHAR2(50)", constraint: "NULLABLE", rule: "Logistics hub city" },
      { name: "rating", type: "NUMBER(2,1)", constraint: "CHECK", rule: "CHECK (rating BETWEEN 1 AND 5)" },
      { name: "status", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (status IN ('ACTIVE','INACTIVE'))" }
    ],
    ddl: `CREATE TABLE SUPPLIERS (
    supplier_id    NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    supplier_name  VARCHAR2(100) NOT NULL,
    contact_person VARCHAR2(100),
    email          VARCHAR2(100) NOT NULL UNIQUE,
    phone          VARCHAR2(20),
    city           VARCHAR2(50),
    rating         NUMBER(2,1) DEFAULT 3.0,
    status         VARCHAR2(20) DEFAULT 'ACTIVE',
    created_at     TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT chk_supp_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT chk_supp_status CHECK (status IN ('ACTIVE', 'INACTIVE'))
);`
  },

  WAREHOUSES: {
    badge: "Facility Entity",
    desc: "Geographical storage depots and distribution centers. Capacity constraint ensures positive unit threshold. Used for cross-facility inventory rebalancing.",
    columns: [
      { name: "warehouse_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "warehouse_name", type: "VARCHAR2(100)", constraint: "UNIQUE, NOT NULL", rule: "Facility name" },
      { name: "location", type: "VARCHAR2(150)", constraint: "NOT NULL", rule: "City / State location" },
      { name: "capacity", type: "NUMBER", constraint: "CHECK", rule: "CHECK (capacity > 0)" },
      { name: "manager_name", type: "VARCHAR2(100)", constraint: "NULLABLE", rule: "Depot supervisor" },
      { name: "status", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (status IN ('ACTIVE','MAINTENANCE'))" }
    ],
    ddl: `CREATE TABLE WAREHOUSES (
    warehouse_id   NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    warehouse_name VARCHAR2(100) NOT NULL UNIQUE,
    location       VARCHAR2(150) NOT NULL,
    capacity       NUMBER NOT NULL,
    manager_name   VARCHAR2(100),
    contact_number VARCHAR2(20),
    status         VARCHAR2(20) DEFAULT 'ACTIVE',
    CONSTRAINT chk_wh_capacity CHECK (capacity > 0),
    CONSTRAINT chk_wh_status   CHECK (status IN ('ACTIVE', 'MAINTENANCE', 'CLOSED'))
);`
  },

  PRODUCTS: {
    badge: "Central Catalog Hub",
    desc: "The central relational anchor connecting Categories, Suppliers, Inventory, and Order Items. Enforces non-negative profit markup at database engine level.",
    columns: [
      { name: "product_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "sku", type: "VARCHAR2(50)", constraint: "UNIQUE, NOT NULL", rule: "Stock Keeping Unit code" },
      { name: "product_name", type: "VARCHAR2(150)", constraint: "NOT NULL", rule: "Catalog title" },
      { name: "category_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES CATEGORIES(category_id) ON DELETE SET NULL" },
      { name: "supplier_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL" },
      { name: "cost_price", type: "NUMBER(10,2)", constraint: "CHECK", rule: "CHECK (cost_price >= 0)" },
      { name: "unit_price", type: "NUMBER(10,2)", constraint: "CHECK", rule: "CHECK (unit_price >= cost_price)" },
      { name: "reorder_level", type: "NUMBER", constraint: "DEFAULT 10", rule: "Automated replenishment trigger" },
      { name: "unit_of_measure", type: "VARCHAR2(20)", constraint: "DEFAULT 'PCS'", rule: "PCS / BOX / METER" }
    ],
    ddl: `CREATE TABLE PRODUCTS (
    product_id      NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sku             VARCHAR2(50) NOT NULL UNIQUE,
    product_name    VARCHAR2(150) NOT NULL,
    category_id     NUMBER,
    supplier_id     NUMBER,
    cost_price      NUMBER(10,2) NOT NULL,
    unit_price      NUMBER(10,2) NOT NULL,
    reorder_level   NUMBER DEFAULT 10,
    unit_of_measure VARCHAR2(20) DEFAULT 'PCS',
    created_at      TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_prod_cat  FOREIGN KEY (category_id) REFERENCES CATEGORIES(category_id) ON DELETE SET NULL,
    CONSTRAINT fk_prod_supp FOREIGN KEY (supplier_id) REFERENCES SUPPLIERS(supplier_id) ON DELETE SET NULL,
    CONSTRAINT chk_cost_pos CHECK (cost_price >= 0),
    CONSTRAINT chk_price_gte_cost CHECK (unit_price >= cost_price)
);`
  },

  INVENTORY: {
    badge: "Associative Bridge (M:N)",
    desc: "Resolves the Many-to-Many relationship between Products and Warehouses. Implements a Composite Unique Key on (product_id, warehouse_id) and non-negative stock check.",
    columns: [
      { name: "inventory_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "product_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES PRODUCTS(product_id) ON DELETE CASCADE" },
      { name: "warehouse_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES WAREHOUSES(warehouse_id) ON DELETE CASCADE" },
      { name: "quantity_on_hand", type: "NUMBER", constraint: "CHECK", rule: "CHECK (quantity_on_hand >= 0)" },
      { name: "last_updated", type: "TIMESTAMP", constraint: "DEFAULT SYSTIMESTAMP", rule: "Tracked in atomic MERGE" }
    ],
    ddl: `CREATE TABLE INVENTORY (
    inventory_id     NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    product_id       NUMBER NOT NULL,
    warehouse_id     NUMBER NOT NULL,
    quantity_on_hand NUMBER DEFAULT 0 NOT NULL,
    last_updated     TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_inv_prod FOREIGN KEY (product_id)   REFERENCES PRODUCTS(product_id) ON DELETE CASCADE,
    CONSTRAINT fk_inv_wh   FOREIGN KEY (warehouse_id) REFERENCES WAREHOUSES(warehouse_id) ON DELETE CASCADE,
    CONSTRAINT uq_prod_wh  UNIQUE (product_id, warehouse_id),
    CONSTRAINT chk_qty_pos CHECK (quantity_on_hand >= 0)
);`
  },

  CUSTOMERS: {
    badge: "Client Entity",
    desc: "Stores retail, wholesale, and corporate client accounts with unique email and domain customer classifications.",
    columns: [
      { name: "customer_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "customer_name", type: "VARCHAR2(100)", constraint: "NOT NULL", rule: "Client or Corporate entity" },
      { name: "email", type: "VARCHAR2(100)", constraint: "UNIQUE, NOT NULL", rule: "Billing contact email" },
      { name: "phone", type: "VARCHAR2(20)", constraint: "NULLABLE", rule: "Contact phone" },
      { name: "city", type: "VARCHAR2(50)", constraint: "NULLABLE", rule: "Billing city" },
      { name: "customer_type", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (customer_type IN ('RETAIL','WHOLESALE','CORPORATE'))" }
    ],
    ddl: `CREATE TABLE CUSTOMERS (
    customer_id   NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    customer_name VARCHAR2(100) NOT NULL,
    email         VARCHAR2(100) NOT NULL UNIQUE,
    phone         VARCHAR2(20),
    city          VARCHAR2(50),
    customer_type VARCHAR2(20) DEFAULT 'RETAIL',
    created_at    TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT chk_cust_type CHECK (customer_type IN ('RETAIL', 'WHOLESALE', 'CORPORATE'))
);`
  },

  ORDERS: {
    badge: "Header Transaction",
    desc: "Master sales order registry containing invoice number, customer reference, order timestamp, computed tax, and fulfillment status.",
    columns: [
      { name: "order_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "order_number", type: "VARCHAR2(50)", constraint: "UNIQUE, NOT NULL", rule: "Sequential invoice format" },
      { name: "customer_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES CUSTOMERS(customer_id)" },
      { name: "order_date", type: "TIMESTAMP", constraint: "DEFAULT SYSTIMESTAMP", rule: "Order timestamp" },
      { name: "total_amount", type: "NUMBER(12,2)", constraint: "CHECK", rule: "CHECK (total_amount >= 0)" },
      { name: "tax_amount", type: "NUMBER(10,2)", constraint: "DEFAULT 0", rule: "Calculated state sales tax (8%)" },
      { name: "status", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (status IN ('PENDING','PROCESSING','COMPLETED','CANCELLED'))" }
    ],
    ddl: `CREATE TABLE ORDERS (
    order_id       NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    order_number   VARCHAR2(50) NOT NULL UNIQUE,
    customer_id    NUMBER NOT NULL,
    order_date     TIMESTAMP DEFAULT SYSTIMESTAMP,
    total_amount   NUMBER(12,2) DEFAULT 0 NOT NULL,
    tax_amount     NUMBER(10,2) DEFAULT 0,
    status         VARCHAR2(20) DEFAULT 'PENDING',
    payment_method VARCHAR2(30) DEFAULT 'INVOICE_NET30',
    CONSTRAINT fk_ord_cust   FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id),
    CONSTRAINT chk_ord_total CHECK (total_amount >= 0),
    CONSTRAINT chk_ord_stat  CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED'))
);`
  },

  ORDER_ITEMS: {
    badge: "Detail Item Entity",
    desc: "Individual line item details linking to specific orders, products, and fulfillment warehouses. Subtotal = quantity * unit_price.",
    columns: [
      { name: "order_item_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "order_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES ORDERS(order_id) ON DELETE CASCADE" },
      { name: "product_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES PRODUCTS(product_id)" },
      { name: "warehouse_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES WAREHOUSES(warehouse_id)" },
      { name: "quantity", type: "NUMBER", constraint: "CHECK", rule: "CHECK (quantity > 0)" },
      { name: "unit_price", type: "NUMBER(10,2)", constraint: "CHECK", rule: "CHECK (unit_price >= 0)" },
      { name: "subtotal", type: "NUMBER(12,2)", constraint: "CHECK", rule: "CHECK (subtotal >= 0)" }
    ],
    ddl: `CREATE TABLE ORDER_ITEMS (
    order_item_id NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    order_id      NUMBER NOT NULL,
    product_id    NUMBER NOT NULL,
    warehouse_id  NUMBER NOT NULL,
    quantity      NUMBER NOT NULL,
    unit_price    NUMBER(10,2) NOT NULL,
    subtotal      NUMBER(12,2) NOT NULL,
    CONSTRAINT fk_oi_ord  FOREIGN KEY (order_id)     REFERENCES ORDERS(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_oi_prod FOREIGN KEY (product_id)   REFERENCES PRODUCTS(product_id),
    CONSTRAINT fk_oi_wh   FOREIGN KEY (warehouse_id) REFERENCES WAREHOUSES(warehouse_id),
    CONSTRAINT chk_oi_qty CHECK (quantity > 0),
    CONSTRAINT chk_oi_sub CHECK (subtotal >= 0)
);`
  },

  STOCK_TRANSACTIONS: {
    badge: "Immutable Ledger",
    desc: "Complete double-entry audit ledger for stock movements (STOCK_IN, STOCK_OUT, TRANSFER_IN, TRANSFER_OUT, ADJUSTMENT).",
    columns: [
      { name: "transaction_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "product_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES PRODUCTS(product_id)" },
      { name: "warehouse_id", type: "NUMBER", constraint: "FOREIGN KEY", rule: "REFERENCES WAREHOUSES(warehouse_id)" },
      { name: "transaction_type", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (transaction_type IN ('STOCK_IN','STOCK_OUT','TRANSFER_IN','TRANSFER_OUT','ADJUSTMENT'))" },
      { name: "quantity", type: "NUMBER", constraint: "NOT NULL", rule: "Signed or unsigned unit count" },
      { name: "performed_by", type: "VARCHAR2(50)", constraint: "DEFAULT USER", rule: "Oracle session user / actor" },
      { name: "transaction_date", type: "TIMESTAMP", constraint: "DEFAULT SYSTIMESTAMP", rule: "Ledger commit timestamp" }
    ],
    ddl: `CREATE TABLE STOCK_TRANSACTIONS (
    transaction_id   NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    product_id       NUMBER NOT NULL,
    warehouse_id     NUMBER NOT NULL,
    transaction_type VARCHAR2(20) NOT NULL,
    quantity         NUMBER NOT NULL,
    reference_id     VARCHAR2(100),
    performed_by     VARCHAR2(50) DEFAULT USER,
    transaction_date TIMESTAMP DEFAULT SYSTIMESTAMP,
    CONSTRAINT fk_st_prod FOREIGN KEY (product_id)   REFERENCES PRODUCTS(product_id),
    CONSTRAINT fk_st_wh   FOREIGN KEY (warehouse_id) REFERENCES WAREHOUSES(warehouse_id),
    CONSTRAINT chk_st_type CHECK (transaction_type IN ('STOCK_IN', 'STOCK_OUT', 'TRANSFER_IN', 'TRANSFER_OUT', 'ADJUSTMENT'))
);`
  },

  AUDIT_LOGS: {
    badge: "Autonomous Trigger Target",
    desc: "Captures historical modifications to crucial financial tables (price updates, deletions) automatically fired via Oracle DML row triggers.",
    columns: [
      { name: "log_id", type: "NUMBER", constraint: "PRIMARY KEY", rule: "GENERATED BY DEFAULT AS IDENTITY" },
      { name: "table_name", type: "VARCHAR2(50)", constraint: "NOT NULL", rule: "Target table (e.g. PRODUCTS)" },
      { name: "action_type", type: "VARCHAR2(20)", constraint: "CHECK", rule: "CHECK (action_type IN ('INSERT','UPDATE','DELETE'))" },
      { name: "record_id", type: "VARCHAR2(50)", constraint: "NOT NULL", rule: "Identity key value" },
      { name: "performed_by", type: "VARCHAR2(50)", constraint: "DEFAULT USER", rule: "DB session username" },
      { name: "action_date", type: "TIMESTAMP", constraint: "DEFAULT SYSTIMESTAMP", rule: "Trigger execution time" },
      { name: "details", type: "VARCHAR2(4000)", constraint: "NULLABLE", rule: "Old vs New price comparison payload" }
    ],
    ddl: `CREATE TABLE AUDIT_LOGS (
    log_id       NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    table_name   VARCHAR2(50) NOT NULL,
    action_type  VARCHAR2(20) NOT NULL,
    record_id    VARCHAR2(50) NOT NULL,
    performed_by VARCHAR2(50) DEFAULT USER,
    action_date  TIMESTAMP DEFAULT SYSTIMESTAMP,
    details      VARCHAR2(4000),
    CONSTRAINT chk_audit_action CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE'))
);`
  }
};

// ============================================================================
// INITIALIZATION & EVENT LISTENERS
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
  // 1. Load initial demo query
  loadSelectedQuery();

  // 2. Animate counter metrics on scroll
  initMetricCounters();

  // 3. Mobile menu toggle
  initMobileNav();

  // 4. Smooth scrolling for anchor links
  initSmoothScroll();
});

// ============================================================================
// SQL WORKBENCH LOGIC
// ============================================================================
function loadSelectedQuery() {
  const selector = document.getElementById("querySelector");
  const queryKey = selector.value;
  const qData = DEMO_QUERIES[queryKey];

  if (!qData) return;

  // Update text & inputs
  document.getElementById("queryCategoryBadge").innerText = qData.category;
  document.getElementById("queryDescription").innerText = qData.description;
  document.getElementById("sqlCodeInput").value = qData.sql;

  // Render results
  renderQueryResults(qData);
}

function executeCurrentQuery() {
  const btn = document.getElementById("btnRunQuery");
  const originalText = btn.innerHTML;

  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Executing...`;
  btn.disabled = true;

  // Random realistic execution latency between 6.5ms and 15.2ms
  const simulatedLatency = (Math.random() * (15.2 - 6.5) + 6.5).toFixed(1);

  setTimeout(() => {
    btn.innerHTML = originalText;
    btn.disabled = false;

    const selector = document.getElementById("querySelector");
    const qData = DEMO_QUERIES[selector.value];

    document.getElementById("resultsLatency").innerHTML = `<i class="fa-solid fa-gauge-high"></i> Latency: <strong>${simulatedLatency} ms</strong>`;
    showToast(`Oracle 23ai returned ${qData.rows.length} rows in ${simulatedLatency}ms`);
  }, 450);
}

function renderQueryResults(qData) {
  const container = document.getElementById("resultsTableContainer");
  const countBadge = document.getElementById("resultsRowCount");

  countBadge.innerText = `${qData.rows.length} rows`;

  let html = `<table class="data-table"><thead><tr>`;
  qData.headers.forEach(h => {
    html += `<th>${h}</th>`;
  });
  html += `</tr></thead><tbody>`;

  qData.rows.forEach(r => {
    html += `<tr>`;
    r.forEach(cell => {
      if (cell.startsWith("$")) {
        html += `<td class="text-green"><strong>${cell}</strong></td>`;
      } else if (cell.includes("---")) {
        html += `<td class="text-dim"><em>${cell}</em></td>`;
      } else if (cell === "1") {
        html += `<td><span class="badge-table-green">Rank #1</span></td>`;
      } else {
        html += `<td>${cell}</td>`;
      }
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

function copyCurrentSQL() {
  const sql = document.getElementById("sqlCodeInput").value;
  navigator.clipboard.writeText(sql).then(() => {
    showToast("SQL query copied to clipboard!");
  });
}

function showExplainPlan() {
  const selector = document.getElementById("querySelector");
  const qData = DEMO_QUERIES[selector.value];

  document.getElementById("explainCost").innerText = qData.cost || "3";
  document.getElementById("explainCardinality").innerText = qData.cardinality || "24";
  document.getElementById("explainPlanText").innerText = qData.plan;

  document.getElementById("explainModal").classList.add("open");
}

function closeExplainModal(e) {
  if (e.target.id === "explainModal") {
    closeExplainModalDirect();
  }
}

function closeExplainModalDirect() {
  document.getElementById("explainModal").classList.remove("open");
}

// ============================================================================
// ERD MODAL INSPECTOR
// ============================================================================
let currentModalDDL = "";

function openTableModal(tableName) {
  const meta = TABLE_METADATA[tableName];
  if (!meta) return;

  document.getElementById("modalTableName").innerText = tableName;
  document.getElementById("modalTableBadge").innerText = meta.badge;
  document.getElementById("modalTableDesc").innerText = meta.desc;

  const tbody = document.getElementById("modalColumnsBody");
  tbody.innerHTML = "";

  meta.columns.forEach(col => {
    const tr = document.createElement("tr");

    let constraintBadge = `<span class="badge-card">${col.constraint}</span>`;
    if (col.constraint.includes("PRIMARY KEY")) {
      constraintBadge = `<span class="badge-pk">PRIMARY KEY</span>`;
    } else if (col.constraint.includes("FOREIGN KEY")) {
      constraintBadge = `<span class="badge-card" style="background: rgba(139,92,246,0.2); color:#c4b5fd;">FOREIGN KEY</span>`;
    } else if (col.constraint.includes("CHECK")) {
      constraintBadge = `<span class="badge-status-green">CHECK</span>`;
    }

    tr.innerHTML = `
      <td><code>${col.name}</code></td>
      <td><span class="text-cyan">${col.type}</span></td>
      <td>${constraintBadge}</td>
      <td class="text-muted">${col.rule}</td>
    `;
    tbody.appendChild(tr);
  });

  currentModalDDL = meta.ddl;
  document.getElementById("modalDDLCode").innerText = meta.ddl;

  document.getElementById("tableModal").classList.add("open");
}

function closeTableModal(e) {
  if (e.target.id === "tableModal") {
    closeTableModalDirect();
  }
}

function closeTableModalDirect() {
  document.getElementById("tableModal").classList.remove("open");
}

function copyModalDDL() {
  if (!currentModalDDL) return;
  navigator.clipboard.writeText(currentModalDDL).then(() => {
    showToast("DDL statement copied to clipboard!");
  });
}

// ============================================================================
// UI TOUR TABS
// ============================================================================
function switchUITab(index) {
  const buttons = document.querySelectorAll(".ui-tab-btn");
  const panes = document.querySelectorAll(".ui-tab-pane");

  buttons.forEach((btn, i) => {
    if (i === index) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  panes.forEach((pane, i) => {
    if (i === index) {
      pane.classList.add("active");
    } else {
      pane.classList.remove("active");
    }
  });
}

// ============================================================================
// VIVA ACCORDION
// ============================================================================
function toggleAccordion(btn) {
  const item = btn.parentElement;
  const isOpen = item.classList.contains("open");

  // Close all
  document.querySelectorAll(".accordion-item").forEach(el => {
    el.classList.remove("open");
  });

  // Toggle clicked
  if (!isOpen) {
    item.classList.add("open");
  }
}

// ============================================================================
// METRIC COUNTER ANIMATIONS
// ============================================================================
function initMetricCounters() {
  const counters = document.querySelectorAll(".metric-number[data-count]");
  let animated = false;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !animated) {
        animated = true;
        counters.forEach(counter => {
          const target = +counter.getAttribute("data-count");
          let current = 0;
          const step = Math.ceil(target / 20) || 1;
          const timer = setInterval(() => {
            current += step;
            if (current >= target) {
              counter.innerText = target;
              clearInterval(timer);
            } else {
              counter.innerText = current;
            }
          }, 40);
        });
      }
    });
  }, { threshold: 0.3 });

  const metricsSection = document.querySelector(".metrics-grid");
  if (metricsSection) {
    observer.observe(metricsSection);
  }
}

// ============================================================================
// SNIPPET COPIER & TOAST
// ============================================================================
function copySnippet(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    showToast("PL/SQL block copied to clipboard!");
  });
}

function showToast(message) {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}

// ============================================================================
// MOBILE NAVIGATION & SCROLL SPY
// ============================================================================
function initMobileNav() {
  const toggle = document.getElementById("mobileToggle");
  const navLinks = document.getElementById("navLinks");

  if (toggle && navLinks) {
    toggle.addEventListener("click", () => {
      navLinks.classList.toggle("mobile-open");
    });

    document.querySelectorAll(".nav-item").forEach(link => {
      link.addEventListener("click", () => {
        navLinks.classList.remove("mobile-open");
      });
    });
  }
}

function initSmoothScroll() {
  const sections = document.querySelectorAll("section[id]");
  const navItems = document.querySelectorAll(".nav-item");

  window.addEventListener("scroll", () => {
    let current = "";
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.pageYOffset >= sectionTop) {
        current = section.getAttribute("id");
      }
    });

    navItems.forEach(item => {
      item.classList.remove("active");
      if (item.getAttribute("href") === `#${current}`) {
        item.classList.add("active");
      }
    });
  });
}
