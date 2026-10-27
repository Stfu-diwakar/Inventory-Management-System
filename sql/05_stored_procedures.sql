-- ============================================================================
-- ORACLE PL/SQL STORED PROCEDURES & FUNCTIONS
-- Project: Inventory Management System
-- Database: Oracle 19c / 21c / 23ai
-- Description: Business logic, transactional stock updates, warehouse transfers,
--              and analytical functions.
-- ============================================================================

SET DEFINE OFF;
SET SERVEROUTPUT ON;

-- ----------------------------------------------------------------------------
-- 1. PROCEDURE: RECORD STOCK MOVEMENT (STOCK IN / STOCK OUT / ADJUSTMENT)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_PROCESS_STOCK_MOVEMENT (
    p_product_id       IN NUMBER,
    p_warehouse_id     IN NUMBER,
    p_transaction_type IN VARCHAR2,
    p_quantity         IN NUMBER,
    p_reference_id     IN VARCHAR2,
    p_notes            IN VARCHAR2,
    p_performed_by     IN VARCHAR2,
    p_status           OUT VARCHAR2,
    p_message          OUT VARCHAR2
) AS
    v_current_stock NUMBER := 0;
    v_new_stock     NUMBER := 0;
BEGIN
    -- Check if inventory record exists
    BEGIN
        SELECT quantity_on_hand INTO v_current_stock
        FROM INVENTORY
        WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            -- Initialize with 0 if no record exists
            INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand)
            VALUES (p_product_id, p_warehouse_id, 0);
            v_current_stock := 0;
    END;

    -- Calculate new stock level based on transaction type
    IF p_transaction_type IN ('STOCK_IN', 'TRANSFER_IN') THEN
        v_new_stock := v_current_stock + ABS(p_quantity);
    ELSIF p_transaction_type IN ('STOCK_OUT', 'TRANSFER_OUT') THEN
        IF v_current_stock < ABS(p_quantity) THEN
            p_status := 'ERROR';
            p_message := 'Insufficient stock on hand. Available: ' || v_current_stock || ', Requested: ' || ABS(p_quantity);
            ROLLBACK;
            RETURN;
        END IF;
        v_new_stock := v_current_stock - ABS(p_quantity);
    ELSIF p_transaction_type = 'ADJUSTMENT' THEN
        -- Quantity can be positive or negative for adjustment
        IF (v_current_stock + p_quantity) < 0 THEN
            p_status := 'ERROR';
            p_message := 'Adjustment would result in negative stock (' || (v_current_stock + p_quantity) || ').';
            ROLLBACK;
            RETURN;
        END IF;
        v_new_stock := v_current_stock + p_quantity;
    ELSE
        p_status := 'ERROR';
        p_message := 'Invalid transaction type: ' || p_transaction_type;
        ROLLBACK;
        RETURN;
    END IF;

    -- Update inventory
    UPDATE INVENTORY
    SET quantity_on_hand = v_new_stock,
        last_updated = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id AND warehouse_id = p_warehouse_id;

    -- Record in transaction ledger
    INSERT INTO STOCK_TRANSACTIONS (
        product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by
    ) VALUES (
        p_product_id, p_warehouse_id, p_transaction_type, p_quantity, p_reference_id, p_notes, NVL(p_performed_by, USER)
    );

    COMMIT;
    p_status := 'SUCCESS';
    p_message := 'Transaction completed successfully. New stock level: ' || v_new_stock;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_status := 'ERROR';
        p_message := 'Database error: ' || SQLERRM;
END SP_PROCESS_STOCK_MOVEMENT;
/

-- ----------------------------------------------------------------------------
-- 2. PROCEDURE: ATOMIC WAREHOUSE-TO-WAREHOUSE STOCK TRANSFER
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE SP_TRANSFER_STOCK (
    p_product_id       IN NUMBER,
    p_from_wh_id       IN NUMBER,
    p_to_wh_id         IN NUMBER,
    p_quantity         IN NUMBER,
    p_reference_id     IN VARCHAR2,
    p_notes            IN VARCHAR2,
    p_performed_by     IN VARCHAR2,
    p_status           OUT VARCHAR2,
    p_message          OUT VARCHAR2
) AS
    v_source_stock NUMBER := 0;
    v_dest_stock   NUMBER := 0;
BEGIN
    IF p_from_wh_id = p_to_wh_id THEN
        p_status := 'ERROR';
        p_message := 'Source and destination warehouses cannot be identical.';
        RETURN;
    END IF;

    IF p_quantity <= 0 THEN
        p_status := 'ERROR';
        p_message := 'Transfer quantity must be greater than zero.';
        RETURN;
    END IF;

    -- Check source warehouse stock
    BEGIN
        SELECT quantity_on_hand INTO v_source_stock
        FROM INVENTORY
        WHERE product_id = p_product_id AND warehouse_id = p_from_wh_id
        FOR UPDATE;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            p_status := 'ERROR';
            p_message := 'Product does not exist in the source warehouse.';
            RETURN;
    END;

    IF v_source_stock < p_quantity THEN
        p_status := 'ERROR';
        p_message := 'Insufficient stock in source warehouse. Available: ' || v_source_stock || ', Transfer requested: ' || p_quantity;
        RETURN;
    END IF;

    -- Deduct from source warehouse
    UPDATE INVENTORY
    SET quantity_on_hand = quantity_on_hand - p_quantity,
        last_updated = CURRENT_TIMESTAMP
    WHERE product_id = p_product_id AND warehouse_id = p_from_wh_id;

    -- Ensure destination warehouse inventory record exists
    BEGIN
        SELECT quantity_on_hand INTO v_dest_stock
        FROM INVENTORY
        WHERE product_id = p_product_id AND warehouse_id = p_to_wh_id
        FOR UPDATE;

        UPDATE INVENTORY
        SET quantity_on_hand = quantity_on_hand + p_quantity,
            last_updated = CURRENT_TIMESTAMP
        WHERE product_id = p_product_id AND warehouse_id = p_to_wh_id;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            INSERT INTO INVENTORY (product_id, warehouse_id, quantity_on_hand)
            VALUES (p_product_id, p_to_wh_id, p_quantity);
    END;

    -- Log both legs of transfer in transaction ledger
    INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
    VALUES (p_product_id, p_from_wh_id, 'TRANSFER_OUT', -p_quantity, p_reference_id, 'Transferred to WH #' || p_to_wh_id || ': ' || p_notes, NVL(p_performed_by, USER));

    INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
    VALUES (p_product_id, p_to_wh_id, 'TRANSFER_IN', p_quantity, p_reference_id, 'Transferred from WH #' || p_from_wh_id || ': ' || p_notes, NVL(p_performed_by, USER));

    COMMIT;
    p_status := 'SUCCESS';
    p_message := 'Stock transfer completed successfully (' || p_quantity || ' units transferred).';
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_status := 'ERROR';
        p_message := 'Transfer failed: ' || SQLERRM;
END SP_TRANSFER_STOCK;
/

-- ----------------------------------------------------------------------------
-- 3. FUNCTION: PRODUCT STOCK HEALTH EVALUATOR
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION FN_GET_STOCK_HEALTH (
    p_product_id IN NUMBER
) RETURN VARCHAR2 AS
    v_total_stock   NUMBER := 0;
    v_reorder_level NUMBER := 10;
BEGIN
    SELECT NVL(reorder_level, 10) INTO v_reorder_level
    FROM PRODUCTS
    WHERE product_id = p_product_id;

    SELECT NVL(SUM(quantity_on_hand), 0) INTO v_total_stock
    FROM INVENTORY
    WHERE product_id = p_product_id;

    IF v_total_stock = 0 THEN
        RETURN 'CRITICAL_OUT_OF_STOCK';
    ELSIF v_total_stock <= v_reorder_level THEN
        RETURN 'LOW_STOCK_WARNING';
    ELSIF v_total_stock > (v_reorder_level * 5) THEN
        RETURN 'OVERSTOCKED';
    ELSE
        RETURN 'OPTIMAL';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 'UNKNOWN';
END FN_GET_STOCK_HEALTH;
/

-- ----------------------------------------------------------------------------
-- 4. FUNCTION: PRODUCT INVENTORY VALUATION
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION FN_GET_PRODUCT_VALUATION (
    p_product_id IN NUMBER,
    p_valuation_type IN VARCHAR2 DEFAULT 'COST'
) RETURN NUMBER AS
    v_cost_price  NUMBER := 0;
    v_unit_price  NUMBER := 0;
    v_total_stock NUMBER := 0;
BEGIN
    SELECT cost_price, unit_price INTO v_cost_price, v_unit_price
    FROM PRODUCTS
    WHERE product_id = p_product_id;

    SELECT NVL(SUM(quantity_on_hand), 0) INTO v_total_stock
    FROM INVENTORY
    WHERE product_id = p_product_id;

    IF UPPER(p_valuation_type) = 'RETAIL' THEN
        RETURN ROUND(v_total_stock * v_unit_price, 2);
    ELSE
        RETURN ROUND(v_total_stock * v_cost_price, 2);
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END FN_GET_PRODUCT_VALUATION;
/

SHOW ERRORS;
