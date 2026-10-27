-- ============================================================================
-- ORACLE SQL CLEANUP / RESET SCRIPT
-- Project: Inventory Management System
-- Database: Oracle 19c / 21c / 23ai
-- Description: Safely drops all project tables, views, triggers, and procedures.
-- ============================================================================

SET SERVEROUTPUT ON;

BEGIN
    -- Drop Procedures and Functions
    FOR p IN (SELECT object_name, object_type FROM user_objects WHERE object_type IN ('PROCEDURE', 'FUNCTION') 
              AND object_name IN ('SP_PROCESS_STOCK_MOVEMENT', 'SP_TRANSFER_STOCK', 'FN_GET_STOCK_HEALTH', 'FN_GET_PRODUCT_VALUATION')) LOOP
        EXECUTE IMMEDIATE 'DROP ' || p.object_type || ' ' || p.object_name;
        DBMS_OUTPUT.PUT_LINE('Dropped ' || p.object_type || ': ' || p.object_name);
    END LOOP;

    -- Drop Views
    FOR v IN (SELECT view_name FROM user_views WHERE view_name IN (
        'VW_PRODUCT_STOCK_SUMMARY', 'VW_LOW_STOCK_ALERTS', 
        'VW_SALES_ANALYTICS', 'VW_WAREHOUSE_OCCUPANCY', 'VW_SUPPLIER_RATINGS'
    )) LOOP
        EXECUTE IMMEDIATE 'DROP VIEW ' || v.view_name;
        DBMS_OUTPUT.PUT_LINE('Dropped View: ' || v.view_name);
    END LOOP;

    -- Drop Tables
    FOR t IN (SELECT table_name FROM user_tables WHERE table_name IN (
        'AUDIT_LOGS', 'STOCK_TRANSACTIONS', 'ORDER_ITEMS', 'ORDERS', 
        'INVENTORY', 'PRODUCTS', 'WAREHOUSES', 'SUPPLIERS', 'CUSTOMERS', 'CATEGORIES'
    )) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS PURGE';
        DBMS_OUTPUT.PUT_LINE('Dropped Table: ' || t.table_name);
    END LOOP;

    -- Drop Roles
    FOR r IN (SELECT role FROM user_roles WHERE role IN ('INV_ADMIN_ROLE', 'INV_MANAGER_ROLE', 'INV_STAFF_ROLE', 'INV_AUDITOR_ROLE')) LOOP
        BEGIN
            EXECUTE IMMEDIATE 'DROP ROLE ' || r.role;
            DBMS_OUTPUT.PUT_LINE('Dropped Role: ' || r.role);
        EXCEPTION
            WHEN OTHERS THEN NULL;
        END;
    END LOOP;

    DBMS_OUTPUT.PUT_LINE('Cleanup completed successfully.');
END;
/
