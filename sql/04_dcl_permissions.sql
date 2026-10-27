-- ============================================================================
-- ORACLE SQL DCL (DATA CONTROL LANGUAGE) SCRIPT
-- Project: Inventory Management System
-- Database: Oracle 19c / 21c / 23ai
-- Description: Demonstrates creation of security roles, fine-grained object
--              privileges (GRANT / REVOKE), and role assignment to database users.
-- ============================================================================

SET DEFINE OFF;
SET FEEDBACK ON;

-- ----------------------------------------------------------------------------
-- 1. CLEANUP PREVIOUS ROLES & USERS (IF RUNNING REPEATEDLY)
-- ----------------------------------------------------------------------------
BEGIN
    FOR r IN (SELECT role FROM user_roles WHERE role IN ('INV_ADMIN_ROLE', 'INV_MANAGER_ROLE', 'INV_STAFF_ROLE', 'INV_AUDITOR_ROLE')) LOOP
        BEGIN EXECUTE IMMEDIATE 'DROP ROLE ' || r.role; EXCEPTION WHEN OTHERS THEN NULL; END;
    END LOOP;
END;
/

-- ----------------------------------------------------------------------------
-- 2. CREATE ROLES FOR ROLE-BASED ACCESS CONTROL (RBAC)
-- ----------------------------------------------------------------------------
-- Role 1: Administrator (Full DML and DDL privileges)
CREATE ROLE INV_ADMIN_ROLE;

-- Role 2: Inventory Manager (Can manage products, inventory, suppliers, warehouses)
CREATE ROLE INV_MANAGER_ROLE;

-- Role 3: Sales Staff / Cashier (Can read catalog, create orders, and check stock)
CREATE ROLE INV_STAFF_ROLE;

-- Role 4: Auditor / Inspector (Read-only access to all tables, views, and audit logs)
CREATE ROLE INV_AUDITOR_ROLE;

-- ----------------------------------------------------------------------------
-- 3. GRANT PERMISSIONS TO ROLES (OBJECT PRIVILEGES)
-- ----------------------------------------------------------------------------

-- A) Permissions for INV_ADMIN_ROLE (Full Control)
GRANT ALL ON CATEGORIES TO INV_ADMIN_ROLE;
GRANT ALL ON SUPPLIERS TO INV_ADMIN_ROLE;
GRANT ALL ON WAREHOUSES TO INV_ADMIN_ROLE;
GRANT ALL ON CUSTOMERS TO INV_ADMIN_ROLE;
GRANT ALL ON PRODUCTS TO INV_ADMIN_ROLE;
GRANT ALL ON INVENTORY TO INV_ADMIN_ROLE;
GRANT ALL ON ORDERS TO INV_ADMIN_ROLE;
GRANT ALL ON ORDER_ITEMS TO INV_ADMIN_ROLE;
GRANT ALL ON STOCK_TRANSACTIONS TO INV_ADMIN_ROLE;
GRANT ALL ON AUDIT_LOGS TO INV_ADMIN_ROLE;

-- B) Permissions for INV_MANAGER_ROLE (Inventory Operations)
GRANT SELECT, INSERT, UPDATE ON PRODUCTS TO INV_MANAGER_ROLE;
GRANT SELECT, INSERT, UPDATE ON INVENTORY TO INV_MANAGER_ROLE;
GRANT SELECT, INSERT, UPDATE ON CATEGORIES TO INV_MANAGER_ROLE;
GRANT SELECT, INSERT, UPDATE ON SUPPLIERS TO INV_MANAGER_ROLE;
GRANT SELECT, INSERT, UPDATE ON WAREHOUSES TO INV_MANAGER_ROLE;
GRANT SELECT, INSERT ON STOCK_TRANSACTIONS TO INV_MANAGER_ROLE;
GRANT SELECT ON ORDERS TO INV_MANAGER_ROLE;
GRANT SELECT ON ORDER_ITEMS TO INV_MANAGER_ROLE;
GRANT SELECT ON VW_PRODUCT_STOCK_SUMMARY TO INV_MANAGER_ROLE;
GRANT SELECT ON VW_LOW_STOCK_ALERTS TO INV_MANAGER_ROLE;
GRANT SELECT ON VW_WAREHOUSE_OCCUPANCY TO INV_MANAGER_ROLE;

-- C) Permissions for INV_STAFF_ROLE (Sales & Billing Staff)
GRANT SELECT ON PRODUCTS TO INV_STAFF_ROLE;
GRANT SELECT ON CATEGORIES TO INV_STAFF_ROLE;
GRANT SELECT ON INVENTORY TO INV_STAFF_ROLE;
GRANT SELECT, INSERT ON CUSTOMERS TO INV_STAFF_ROLE;
GRANT SELECT, INSERT, UPDATE ON ORDERS TO INV_STAFF_ROLE;
GRANT SELECT, INSERT ON ORDER_ITEMS TO INV_STAFF_ROLE;
GRANT SELECT ON VW_PRODUCT_STOCK_SUMMARY TO INV_STAFF_ROLE;

-- D) Permissions for INV_AUDITOR_ROLE (Read-Only Compliance & Auditing)
GRANT SELECT ON PRODUCTS TO INV_AUDITOR_ROLE;
GRANT SELECT ON INVENTORY TO INV_AUDITOR_ROLE;
GRANT SELECT ON CATEGORIES TO INV_AUDITOR_ROLE;
GRANT SELECT ON SUPPLIERS TO INV_AUDITOR_ROLE;
GRANT SELECT ON WAREHOUSES TO INV_AUDITOR_ROLE;
GRANT SELECT ON CUSTOMERS TO INV_AUDITOR_ROLE;
GRANT SELECT ON ORDERS TO INV_AUDITOR_ROLE;
GRANT SELECT ON ORDER_ITEMS TO INV_AUDITOR_ROLE;
GRANT SELECT ON STOCK_TRANSACTIONS TO INV_AUDITOR_ROLE;
GRANT SELECT ON AUDIT_LOGS TO INV_AUDITOR_ROLE;
GRANT SELECT ON VW_PRODUCT_STOCK_SUMMARY TO INV_AUDITOR_ROLE;
GRANT SELECT ON VW_LOW_STOCK_ALERTS TO INV_AUDITOR_ROLE;
GRANT SELECT ON VW_WAREHOUSE_OCCUPANCY TO INV_AUDITOR_ROLE;
GRANT SELECT ON VW_SALES_ANALYTICS TO INV_AUDITOR_ROLE;
GRANT SELECT ON VW_SUPPLIER_RATINGS TO INV_AUDITOR_ROLE;

-- ----------------------------------------------------------------------------
-- 4. DEMONSTRATION OF REVOKE (DATA CONTROL LANGUAGE)
-- ----------------------------------------------------------------------------
-- Example: Temporarily granting and then revoking DELETE privileges from Manager
GRANT DELETE ON PRODUCTS TO INV_MANAGER_ROLE;
-- Revoking DELETE from Manager (Manager should only archive/deactivate, not purge)
REVOKE DELETE ON PRODUCTS FROM INV_MANAGER_ROLE;

-- ----------------------------------------------------------------------------
-- 5. VERIFY GRANTED PRIVILEGES FROM DATA DICTIONARY
-- ----------------------------------------------------------------------------
SELECT 
    grantee,
    table_name,
    privilege,
    grantable
FROM USER_TAB_PRIVS_MADE
WHERE grantee IN ('INV_ADMIN_ROLE', 'INV_MANAGER_ROLE', 'INV_STAFF_ROLE', 'INV_AUDITOR_ROLE')
ORDER BY grantee, table_name, privilege;

COMMIT;
