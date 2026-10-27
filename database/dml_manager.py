"""
DML (Data Manipulation Language) Manager & CRUD Repository.
Implements Create, Read, Update, and Delete operations for all business entities
using parameterized Oracle SQL statements.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
from database.connection import db

class DMLManager:
    """Provides complete CRUD operations for the Inventory Management System."""

    # =========================================================================
    # 1. PRODUCTS CRUD
    # =========================================================================

    @staticmethod
    def get_products(category_id: Optional[int] = None, supplier_id: Optional[int] = None, search_term: Optional[str] = None) -> pd.DataFrame:
        """Fetch all products with category and supplier names, plus stock totals."""
        sql = """
            SELECT 
                p.product_id,
                p.sku,
                p.product_name,
                c.category_name,
                p.category_id,
                s.supplier_name,
                p.supplier_id,
                p.cost_price,
                p.unit_price,
                ROUND((p.unit_price - p.cost_price), 2) AS profit_margin,
                ROUND(((p.unit_price - p.cost_price) / NULLIF(p.unit_price, 0)) * 100, 2) AS margin_pct,
                p.reorder_level,
                p.unit_of_measure,
                NVL(SUM(i.quantity_on_hand), 0) AS total_stock,
                CASE 
                    WHEN NVL(SUM(i.quantity_on_hand), 0) = 0 THEN 'OUT_OF_STOCK'
                    WHEN NVL(SUM(i.quantity_on_hand), 0) <= p.reorder_level THEN 'LOW_STOCK'
                    ELSE 'IN_STOCK'
                END AS stock_status,
                TO_CHAR(p.created_at, 'YYYY-MM-DD HH24:MI') AS date_added
            FROM PRODUCTS p
            LEFT JOIN CATEGORIES c ON p.category_id = c.category_id
            LEFT JOIN SUPPLIERS s ON p.supplier_id = s.supplier_id
            LEFT JOIN INVENTORY i ON p.product_id = i.product_id
            WHERE 1=1
        """
        params = {}
        if category_id:
            sql += " AND p.category_id = :cat_id"
            params["cat_id"] = category_id
        if supplier_id:
            sql += " AND p.supplier_id = :sup_id"
            params["sup_id"] = supplier_id
        if search_term:
            sql += " AND (UPPER(p.product_name) LIKE :search OR UPPER(p.sku) LIKE :search)"
            params["search"] = f"%{search_term.strip().upper()}%"

        sql += """
            GROUP BY 
                p.product_id, p.sku, p.product_name, c.category_name, p.category_id,
                s.supplier_name, p.supplier_id, p.cost_price, p.unit_price, p.reorder_level, 
                p.unit_of_measure, p.created_at
            ORDER BY p.product_name ASC
        """
        return db.execute_query(sql, params)

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        sql = "SELECT * FROM PRODUCTS WHERE product_id = :pid"
        df = db.execute_query(sql, {"pid": product_id})
        return df.iloc[0].to_dict() if not df.empty else None

    @staticmethod
    def create_product(sku: str, name: str, category_id: int, supplier_id: int, cost_price: float, unit_price: float, reorder_level: int, unit_of_measure: str = "PCS") -> int:
        """Insert a new product record."""
        sql = """
            INSERT INTO PRODUCTS (sku, product_name, category_id, supplier_id, cost_price, unit_price, reorder_level, unit_of_measure)
            VALUES (:sku, :name, :cat_id, :sup_id, :cost, :price, :reorder, :uom)
        """
        params = {
            "sku": sku.strip().upper(),
            "name": name.strip(),
            "cat_id": category_id,
            "sup_id": supplier_id,
            "cost": float(cost_price),
            "price": float(unit_price),
            "reorder": int(reorder_level),
            "uom": unit_of_measure
        }
        return db.execute_dml(sql, params)

    @staticmethod
    def update_product(product_id: int, sku: str, name: str, category_id: int, supplier_id: int, cost_price: float, unit_price: float, reorder_level: int, unit_of_measure: str = "PCS") -> int:
        """Update existing product details."""
        sql = """
            UPDATE PRODUCTS
            SET sku = :sku,
                product_name = :name,
                category_id = :cat_id,
                supplier_id = :sup_id,
                cost_price = :cost,
                unit_price = :price,
                reorder_level = :reorder,
                unit_of_measure = :uom
            WHERE product_id = :pid
        """
        params = {
            "sku": sku.strip().upper(),
            "name": name.strip(),
            "cat_id": category_id,
            "sup_id": supplier_id,
            "cost": float(cost_price),
            "price": float(unit_price),
            "reorder": int(reorder_level),
            "uom": unit_of_measure,
            "pid": product_id
        }
        return db.execute_dml(sql, params)

    @staticmethod
    def delete_product(product_id: int) -> int:
        """Delete product by ID (Cascade deletes inventory and triggers audit)."""
        sql = "DELETE FROM PRODUCTS WHERE product_id = :pid"
        return db.execute_dml(sql, {"pid": product_id})

    # =========================================================================
    # 2. CATEGORIES CRUD
    # =========================================================================

    @staticmethod
    def get_categories() -> pd.DataFrame:
        sql = """
            SELECT 
                c.category_id,
                c.category_name,
                c.description,
                COUNT(p.product_id) AS product_count,
                TO_CHAR(c.created_at, 'YYYY-MM-DD') AS created_date
            FROM CATEGORIES c
            LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
            GROUP BY c.category_id, c.category_name, c.description, c.created_at
            ORDER BY c.category_name ASC
        """
        return db.execute_query(sql)

    @staticmethod
    def create_category(category_name: str, description: str) -> int:
        sql = "INSERT INTO CATEGORIES (category_name, description) VALUES (:name, :desc)"
        return db.execute_dml(sql, {"name": category_name.strip(), "desc": description.strip()})

    @staticmethod
    def update_category(category_id: int, category_name: str, description: str) -> int:
        sql = "UPDATE CATEGORIES SET category_name = :name, description = :desc WHERE category_id = :cid"
        return db.execute_dml(sql, {"name": category_name.strip(), "desc": description.strip(), "cid": category_id})

    @staticmethod
    def delete_category(category_id: int) -> int:
        sql = "DELETE FROM CATEGORIES WHERE category_id = :cid"
        return db.execute_dml(sql, {"cid": category_id})

    # =========================================================================
    # 3. SUPPLIERS CRUD
    # =========================================================================

    @staticmethod
    def get_suppliers() -> pd.DataFrame:
        sql = """
            SELECT 
                s.supplier_id,
                s.supplier_name,
                s.contact_person,
                s.email,
                s.phone,
                s.city,
                s.address,
                s.rating,
                s.status,
                COUNT(p.product_id) AS products_count,
                TO_CHAR(s.created_at, 'YYYY-MM-DD') AS registered_date
            FROM SUPPLIERS s
            LEFT JOIN PRODUCTS p ON s.supplier_id = p.supplier_id
            GROUP BY s.supplier_id, s.supplier_name, s.contact_person, s.email, s.phone, s.city, s.address, s.rating, s.status, s.created_at
            ORDER BY s.supplier_name ASC
        """
        return db.execute_query(sql)

    @staticmethod
    def create_supplier(name: str, contact: str, email: str, phone: str, address: str, city: str, rating: float, status: str = "ACTIVE") -> int:
        sql = """
            INSERT INTO SUPPLIERS (supplier_name, contact_person, email, phone, address, city, rating, status)
            VALUES (:name, :contact, :email, :phone, :address, :city, :rating, :status)
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "contact": contact.strip(), "email": email.strip(),
            "phone": phone.strip(), "address": address.strip(), "city": city.strip(),
            "rating": float(rating), "status": status
        })

    @staticmethod
    def update_supplier(supplier_id: int, name: str, contact: str, email: str, phone: str, address: str, city: str, rating: float, status: str) -> int:
        sql = """
            UPDATE SUPPLIERS
            SET supplier_name = :name, contact_person = :contact, email = :email,
                phone = :phone, address = :address, city = :city, rating = :rating, status = :status
            WHERE supplier_id = :sid
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "contact": contact.strip(), "email": email.strip(),
            "phone": phone.strip(), "address": address.strip(), "city": city.strip(),
            "rating": float(rating), "status": status, "sid": supplier_id
        })

    @staticmethod
    def delete_supplier(supplier_id: int) -> int:
        sql = "DELETE FROM SUPPLIERS WHERE supplier_id = :sid"
        return db.execute_dml(sql, {"sid": supplier_id})

    # =========================================================================
    # 4. WAREHOUSES CRUD
    # =========================================================================

    @staticmethod
    def get_warehouses() -> pd.DataFrame:
        sql = """
            SELECT 
                w.warehouse_id,
                w.warehouse_name,
                w.location,
                w.capacity,
                w.manager_name,
                w.contact_number,
                w.status,
                NVL(SUM(i.quantity_on_hand), 0) AS total_units_stored,
                ROUND((NVL(SUM(i.quantity_on_hand), 0) / w.capacity) * 100, 1) AS occupancy_pct,
                TO_CHAR(w.created_at, 'YYYY-MM-DD') AS established_date
            FROM WAREHOUSES w
            LEFT JOIN INVENTORY i ON w.warehouse_id = i.warehouse_id
            GROUP BY w.warehouse_id, w.warehouse_name, w.location, w.capacity, w.manager_name, w.contact_number, w.status, w.created_at
            ORDER BY w.warehouse_id ASC
        """
        return db.execute_query(sql)

    @staticmethod
    def create_warehouse(name: str, location: str, capacity: int, manager: str, phone: str, status: str = "ACTIVE") -> int:
        sql = """
            INSERT INTO WAREHOUSES (warehouse_name, location, capacity, manager_name, contact_number, status)
            VALUES (:name, :location, :capacity, :manager, :phone, :status)
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "location": location.strip(), "capacity": int(capacity),
            "manager": manager.strip(), "phone": phone.strip(), "status": status
        })

    @staticmethod
    def update_warehouse(warehouse_id: int, name: str, location: str, capacity: int, manager: str, phone: str, status: str) -> int:
        sql = """
            UPDATE WAREHOUSES
            SET warehouse_name = :name, location = :location, capacity = :capacity,
                manager_name = :manager, contact_number = :phone, status = :status
            WHERE warehouse_id = :wid
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "location": location.strip(), "capacity": int(capacity),
            "manager": manager.strip(), "phone": phone.strip(), "status": status, "wid": warehouse_id
        })

    @staticmethod
    def delete_warehouse(warehouse_id: int) -> int:
        sql = "DELETE FROM WAREHOUSES WHERE warehouse_id = :wid"
        return db.execute_dml(sql, {"wid": warehouse_id})

    # =========================================================================
    # 5. CUSTOMERS CRUD
    # =========================================================================

    @staticmethod
    def get_customers() -> pd.DataFrame:
        sql = """
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                c.phone,
                c.city,
                c.customer_type,
                COUNT(o.order_id) AS total_orders,
                NVL(SUM(o.total_amount), 0) AS total_spend,
                TO_CHAR(c.created_at, 'YYYY-MM-DD') AS registered_date
            FROM CUSTOMERS c
            LEFT JOIN ORDERS o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_name, c.email, c.phone, c.city, c.customer_type, c.created_at
            ORDER BY c.customer_name ASC
        """
        return db.execute_query(sql)

    @staticmethod
    def create_customer(name: str, email: str, phone: str, address: str, city: str, cust_type: str = "RETAIL") -> int:
        sql = """
            INSERT INTO CUSTOMERS (customer_name, email, phone, address, city, customer_type)
            VALUES (:name, :email, :phone, :address, :city, :cust_type)
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "email": email.strip(), "phone": phone.strip(),
            "address": address.strip(), "city": city.strip(), "cust_type": cust_type
        })

    @staticmethod
    def update_customer(customer_id: int, name: str, email: str, phone: str, address: str, city: str, cust_type: str) -> int:
        sql = """
            UPDATE CUSTOMERS
            SET customer_name = :name, email = :email, phone = :phone,
                address = :address, city = :city, customer_type = :cust_type
            WHERE customer_id = :cid
        """
        return db.execute_dml(sql, {
            "name": name.strip(), "email": email.strip(), "phone": phone.strip(),
            "address": address.strip(), "city": city.strip(), "cust_type": cust_type, "cid": customer_id
        })

    @staticmethod
    def delete_customer(customer_id: int) -> int:
        sql = "DELETE FROM CUSTOMERS WHERE customer_id = :cid"
        return db.execute_dml(sql, {"cid": customer_id})

    # =========================================================================
    # 6. INVENTORY & STOCK MATRIX
    # =========================================================================

    @staticmethod
    def get_inventory_matrix() -> pd.DataFrame:
        """Returns pivoted or tabular stock of each product per warehouse."""
        sql = """
            SELECT 
                p.product_id,
                p.sku,
                p.product_name,
                c.category_name,
                w.warehouse_id,
                w.warehouse_name,
                NVL(i.quantity_on_hand, 0) AS stock_on_hand,
                p.reorder_level,
                p.cost_price,
                ROUND(NVL(i.quantity_on_hand, 0) * p.cost_price, 2) AS stock_valuation,
                TO_CHAR(i.last_updated, 'YYYY-MM-DD HH24:MI') AS last_updated
            FROM PRODUCTS p
            CROSS JOIN WAREHOUSES w
            LEFT JOIN INVENTORY i ON p.product_id = i.product_id AND w.warehouse_id = i.warehouse_id
            JOIN CATEGORIES c ON p.category_id = c.category_id
            ORDER BY p.product_name, w.warehouse_name
        """
        return db.execute_query(sql)

    @staticmethod
    def update_inventory_quantity(product_id: int, warehouse_id: int, new_quantity: int) -> int:
        """MERGE statement (Upsert) to set quantity directly in inventory."""
        sql = """
            MERGE INTO INVENTORY i
            USING (SELECT :pid AS product_id, :wid AS warehouse_id FROM DUAL) src
            ON (i.product_id = src.product_id AND i.warehouse_id = src.warehouse_id)
            WHEN MATCHED THEN
                UPDATE SET i.quantity_on_hand = :qty, i.last_updated = CURRENT_TIMESTAMP
            WHEN NOT MATCHED THEN
                INSERT (product_id, warehouse_id, quantity_on_hand, last_updated)
                VALUES (src.product_id, src.warehouse_id, :qty, CURRENT_TIMESTAMP)
        """
        return db.execute_dml(sql, {"pid": product_id, "wid": warehouse_id, "qty": int(new_quantity)})

    # =========================================================================
    # 7. ORDERS & SALES BILLING (TRANSACTIONAL)
    # =========================================================================

    @staticmethod
    def get_orders() -> pd.DataFrame:
        sql = """
            SELECT 
                o.order_id,
                o.order_number,
                c.customer_name,
                c.customer_type,
                TO_CHAR(o.order_date, 'YYYY-MM-DD HH24:MI') AS order_date,
                o.total_amount,
                o.tax_amount,
                o.payment_method,
                o.status,
                COUNT(oi.order_item_id) AS total_items
            FROM ORDERS o
            JOIN CUSTOMERS c ON o.customer_id = c.customer_id
            LEFT JOIN ORDER_ITEMS oi ON o.order_id = oi.order_id
            GROUP BY o.order_id, o.order_number, c.customer_name, c.customer_type, o.order_date, o.total_amount, o.tax_amount, o.payment_method, o.status
            ORDER BY o.order_id DESC
        """
        return db.execute_query(sql)

    @staticmethod
    def get_order_items(order_id: int) -> pd.DataFrame:
        sql = """
            SELECT 
                oi.order_item_id,
                p.sku,
                p.product_name,
                w.warehouse_name,
                oi.quantity,
                oi.unit_price,
                oi.subtotal
            FROM ORDER_ITEMS oi
            JOIN PRODUCTS p ON oi.product_id = p.product_id
            JOIN WAREHOUSES w ON oi.warehouse_id = w.warehouse_id
            WHERE oi.order_id = :oid
            ORDER BY oi.order_item_id ASC
        """
        return db.execute_query(sql, {"oid": order_id})

    @staticmethod
    def create_sales_order(customer_id: int, payment_method: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Creates a Sales Order atomically.
        Calculates subtotal, applies tax (8%), creates order, order items,
        deducts stock from inventory, and records stock transactions.
        """
        if not items:
            return {"success": False, "message": "Order must have at least one line item."}

        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()

                # Generate unique order number
                cursor.execute("SELECT 'ORD-' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '-' || LPAD(NVL(MAX(order_id), 0) + 1, 4, '0') FROM ORDERS")
                order_number = cursor.fetchone()[0]

                # Validate stock for all items first
                subtotal_sum = 0.0
                for item in items:
                    pid = item["product_id"]
                    wid = item["warehouse_id"]
                    qty = item["quantity"]
                    cursor.execute(
                        "SELECT quantity_on_hand FROM INVENTORY WHERE product_id = :pid AND warehouse_id = :wid FOR UPDATE",
                        {"pid": pid, "wid": wid}
                    )
                    row = cursor.fetchone()
                    avail = row[0] if row else 0
                    if avail < qty:
                        conn.rollback()
                        return {"success": False, "message": f"Insufficient stock for Product ID {pid} in Warehouse ID {wid}. Available: {avail}, Ordered: {qty}"}

                    subtotal = item["unit_price"] * qty
                    subtotal_sum += subtotal

                tax_amount = round(subtotal_sum * 0.08, 2)
                total_amount = round(subtotal_sum + tax_amount, 2)

                # Insert Order
                order_id_var = cursor.var(int)
                cursor.execute("""
                    INSERT INTO ORDERS (order_number, customer_id, total_amount, tax_amount, status, payment_method)
                    VALUES (:order_num, :cid, :total, :tax, 'COMPLETED', :pay_method)
                    RETURNING order_id INTO :out_oid
                """, {
                    "order_num": order_number,
                    "cid": customer_id,
                    "total": total_amount,
                    "tax": tax_amount,
                    "pay_method": payment_method,
                    "out_oid": order_id_var
                })
                new_order_id = order_id_var.getvalue()[0]

                # Insert Order Items & Deduct Stock
                for item in items:
                    pid = item["product_id"]
                    wid = item["warehouse_id"]
                    qty = item["quantity"]
                    unit_price = item["unit_price"]
                    line_subtotal = round(qty * unit_price, 2)

                    cursor.execute("""
                        INSERT INTO ORDER_ITEMS (order_id, product_id, warehouse_id, quantity, unit_price, subtotal)
                        VALUES (:oid, :pid, :wid, :qty, :price, :subtotal)
                    """, {
                        "oid": new_order_id,
                        "pid": pid,
                        "wid": wid,
                        "qty": qty,
                        "price": unit_price,
                        "subtotal": line_subtotal
                    })

                    # Deduct from inventory
                    cursor.execute("""
                        UPDATE INVENTORY
                        SET quantity_on_hand = quantity_on_hand - :qty,
                            last_updated = CURRENT_TIMESTAMP
                        WHERE product_id = :pid AND warehouse_id = :wid
                    """, {"qty": qty, "pid": pid, "wid": wid})

                    # Log Stock Transaction
                    cursor.execute("""
                        INSERT INTO STOCK_TRANSACTIONS (product_id, warehouse_id, transaction_type, quantity, reference_id, notes, performed_by)
                        VALUES (:pid, :wid, 'STOCK_OUT', :neg_qty, :ref, 'Sales Order fulfillment', USER)
                    """, {
                        "pid": pid,
                        "wid": wid,
                        "neg_qty": -qty,
                        "ref": order_number
                    })

                conn.commit()
                return {
                    "success": True,
                    "order_id": new_order_id,
                    "order_number": order_number,
                    "total_amount": total_amount,
                    "message": f"Order {order_number} created successfully! Inventory deducted."
                }

        except Exception as e:
            return {"success": False, "message": f"Order Transaction Error: {str(e)}"}

    # =========================================================================
    # 8. STOCK MOVEMENTS & AUDIT LOGS
    # =========================================================================

    @staticmethod
    def get_stock_transactions(limit: int = 100) -> pd.DataFrame:
        sql = f"""
            SELECT 
                st.transaction_id,
                TO_CHAR(st.transaction_date, 'YYYY-MM-DD HH24:MI:SS') AS timestamp,
                p.sku,
                p.product_name,
                w.warehouse_name,
                st.transaction_type,
                st.quantity,
                st.reference_id,
                st.notes,
                st.performed_by
            FROM STOCK_TRANSACTIONS st
            JOIN PRODUCTS p ON st.product_id = p.product_id
            JOIN WAREHOUSES w ON st.warehouse_id = w.warehouse_id
            ORDER BY st.transaction_id DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        return db.execute_query(sql)

    @staticmethod
    def get_audit_logs(limit: int = 100) -> pd.DataFrame:
        sql = f"""
            SELECT 
                log_id,
                TO_CHAR(action_date, 'YYYY-MM-DD HH24:MI:SS') AS timestamp,
                table_name,
                action_type,
                record_id,
                performed_by,
                details
            FROM AUDIT_LOGS
            ORDER BY log_id DESC
            FETCH FIRST {limit} ROWS ONLY
        """
        return db.execute_query(sql)

    # =========================================================================
    # 9. DASHBOARD KPIS & ANALYTICS
    # =========================================================================

    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        """Fetch summary KPIs for the dashboard."""
        metrics = {}
        try:
            # Total products
            p_df = db.execute_query("SELECT COUNT(*) AS cnt FROM PRODUCTS")
            metrics["total_products"] = int(p_df.iloc[0]["CNT"]) if not p_df.empty else 0

            # Total units in stock & total valuation
            val_df = db.execute_query("""
                SELECT 
                    NVL(SUM(i.quantity_on_hand), 0) AS total_units,
                    NVL(SUM(i.quantity_on_hand * p.cost_price), 0) AS cost_valuation,
                    NVL(SUM(i.quantity_on_hand * p.unit_price), 0) AS retail_valuation
                FROM PRODUCTS p
                LEFT JOIN INVENTORY i ON p.product_id = i.product_id
            """)
            if not val_df.empty:
                metrics["total_units"] = int(val_df.iloc[0]["TOTAL_UNITS"])
                metrics["cost_valuation"] = float(val_df.iloc[0]["COST_VALUATION"])
                metrics["retail_valuation"] = float(val_df.iloc[0]["RETAIL_VALUATION"])
            else:
                metrics["total_units"] = 0
                metrics["cost_valuation"] = 0.0
                metrics["retail_valuation"] = 0.0

            # Low stock items count
            low_df = db.execute_query("""
                SELECT COUNT(*) AS cnt 
                FROM VW_LOW_STOCK_ALERTS
            """)
            metrics["low_stock_count"] = int(low_df.iloc[0]["CNT"]) if not low_df.empty else 0

            # Total orders & revenue
            ord_df = db.execute_query("""
                SELECT 
                    COUNT(*) AS total_orders,
                    NVL(SUM(total_amount), 0) AS total_revenue
                FROM ORDERS
                WHERE status = 'COMPLETED'
            """)
            if not ord_df.empty:
                metrics["total_orders"] = int(ord_df.iloc[0]["TOTAL_ORDERS"])
                metrics["total_revenue"] = float(ord_df.iloc[0]["TOTAL_REVENUE"])
            else:
                metrics["total_orders"] = 0
                metrics["total_revenue"] = 0.0

            # Warehouse count & average occupancy
            wh_df = db.execute_query("""
                SELECT 
                    COUNT(*) AS total_warehouses,
                    ROUND(AVG((current_stock_units / NULLIF(capacity, 0)) * 100), 1) AS avg_occupancy
                FROM VW_WAREHOUSE_OCCUPANCY
            """)
            if not wh_df.empty:
                metrics["total_warehouses"] = int(wh_df.iloc[0]["TOTAL_WAREHOUSES"])
                metrics["avg_occupancy"] = float(wh_df.iloc[0]["AVG_OCCUPANCY"] or 0.0)
            else:
                metrics["total_warehouses"] = 0
                metrics["avg_occupancy"] = 0.0

        except Exception as e:
            print("Dashboard metric error:", e)
            return {
                "total_products": 0, "total_units": 0, "cost_valuation": 0.0,
                "retail_valuation": 0.0, "low_stock_count": 0, "total_orders": 0,
                "total_revenue": 0.0, "total_warehouses": 0, "avg_occupancy": 0.0
            }

        return metrics
