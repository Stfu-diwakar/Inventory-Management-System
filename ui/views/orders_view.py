"""
Orders & Sales Billing View: POS Shopping Cart, Multi-Item Checkout,
Automatic Stock Deduction, and Invoice Generation.
"""

import streamlit as st
import pandas as pd
from database.dml_manager import DMLManager
from database.connection import db
from ui.components import format_currency, export_dataframe_button

def render_orders():
    st.markdown("### 🛒 Orders & Point of Sale (POS) Billing")
    st.caption("Process customer sales orders with atomic transaction rollback, stock validation, and invoice generation.")

    ord_tab1, ord_tab2 = st.tabs(["📋 Orders Ledger & Invoices", "⚡ Create New Sales Order"])

    # Initialize shopping cart in session state
    if "cart_items" not in st.session_state:
        st.session_state.cart_items = []

    # -------------------------------------------------------------------------
    # TAB 1: ORDERS LEDGER & INVOICES
    # -------------------------------------------------------------------------
    with ord_tab1:
        orders_df = DMLManager.get_orders()

        if not orders_df.empty:
            st.dataframe(
                orders_df,
                use_container_width=True,
                column_config={
                    "ORDER_ID": st.column_config.NumberColumn("ID", width="small"),
                    "ORDER_NUMBER": st.column_config.TextColumn("Order #", width="medium"),
                    "CUSTOMER_NAME": st.column_config.TextColumn("Customer", width="large"),
                    "CUSTOMER_TYPE": st.column_config.TextColumn("Type"),
                    "ORDER_DATE": st.column_config.TextColumn("Date & Time"),
                    "TOTAL_AMOUNT": st.column_config.NumberColumn("Total Amount", format="$%.2f"),
                    "TAX_AMOUNT": st.column_config.NumberColumn("Tax", format="$%.2f"),
                    "PAYMENT_METHOD": st.column_config.TextColumn("Payment"),
                    "STATUS": st.column_config.TextColumn("Status"),
                    "TOTAL_ITEMS": st.column_config.NumberColumn("Lines")
                },
                hide_index=True
            )
            export_dataframe_button(orders_df, "sales_orders.csv")

            st.markdown("---")
            st.subheader("🧾 Invoice & Line-Item Inspector")
            order_options = {f"{r['ORDER_NUMBER']} - {r['CUSTOMER_NAME']} (${r['TOTAL_AMOUNT']:,.2f})": int(r['ORDER_ID']) for _, r in orders_df.iterrows()}
            selected_ord_label = st.selectbox("Select Order to View Detailed Invoice", list(order_options.keys()))
            selected_ord_id = order_options[selected_ord_label]

            # Fetch line items
            items_df = DMLManager.get_order_items(selected_ord_id)
            ord_row = orders_df[orders_df["ORDER_ID"] == selected_ord_id].iloc[0]

            with st.container():
                st.markdown(f"""
                <div class="content-card" style="border: 2px dashed rgba(255, 255, 255, 0.2);">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 12px;">
                        <div>
                            <h3 style="margin: 0; color: #60A5FA;">INVOICE: {ord_row['ORDER_NUMBER']}</h3>
                            <div style="font-size: 13px; color: #94A3B8;">Date: {ord_row['ORDER_DATE']}</div>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge badge-completed">{ord_row['STATUS']}</span>
                            <div style="font-size: 13px; color: #CBD5E1; margin-top: 4px;">Payment: {ord_row['PAYMENT_METHOD']}</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 14px;">
                        <strong>Billed To:</strong> {ord_row['CUSTOMER_NAME']} ({ord_row['CUSTOMER_TYPE']})
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not items_df.empty:
                    st.dataframe(
                        items_df,
                        use_container_width=True,
                        column_config={
                            "ORDER_ITEM_ID": st.column_config.NumberColumn("Line #", width="small"),
                            "SKU": st.column_config.TextColumn("SKU"),
                            "PRODUCT_NAME": st.column_config.TextColumn("Product Item", width="large"),
                            "WAREHOUSE_NAME": st.column_config.TextColumn("Fulfilled From"),
                            "QUANTITY": st.column_config.NumberColumn("Quantity"),
                            "UNIT_PRICE": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
                            "SUBTOTAL": st.column_config.NumberColumn("Subtotal", format="$%.2f")
                        },
                        hide_index=True
                    )
                    
                    inv_col1, inv_col2 = st.columns([2, 1])
                    with inv_col2:
                        st.markdown(f"""
                        <div style="text-align: right; padding: 10px; background: rgba(15, 23, 42, 0.5); border-radius: 8px;">
                            <div>Subtotal: <strong>{format_currency(ord_row['TOTAL_AMOUNT'] - ord_row['TAX_AMOUNT'])}</strong></div>
                            <div>Tax (8%): <strong>{format_currency(ord_row['TAX_AMOUNT'])}</strong></div>
                            <hr style="border-color: rgba(255,255,255,0.1); margin: 6px 0;">
                            <div style="font-size: 18px; font-weight: 800; color: #38BDF8;">Grand Total: {format_currency(ord_row['TOTAL_AMOUNT'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No orders found in the database.")

    # -------------------------------------------------------------------------
    # TAB 2: CREATE NEW SALES ORDER
    # -------------------------------------------------------------------------
    with ord_tab2:
        st.subheader("⚡ New Sales Order Entry")
        custs_df = DMLManager.get_customers()
        prods_df = DMLManager.get_products()
        whs_df = DMLManager.get_warehouses()

        if custs_df.empty or prods_df.empty or whs_df.empty:
            st.warning("Please ensure Customers, Products, and Warehouses exist.")
        else:
            # Order Customer & Payment Header
            ord_h1, ord_h2 = st.columns(2)
            with ord_h1:
                cust_options = {f"{r['CUSTOMER_NAME']} ({r['CUSTOMER_TYPE']})": int(r['CUSTOMER_ID']) for _, r in custs_df.iterrows()}
                selected_cust_label = st.selectbox("Select Customer*", list(cust_options.keys()))
                selected_cust_id = cust_options[selected_cust_label]
            with ord_h2:
                selected_pay_method = st.selectbox("Payment Method*", ["CREDIT_CARD", "BANK_TRANSFER", "CASH", "UPI"])

            st.markdown("---")
            st.markdown("##### 🛒 Add Items to Order Cart")

            item_c1, item_c2, item_c3, item_c4 = st.columns([2.5, 2, 1.5, 1.5])
            with item_c1:
                p_dict = {f"{r['SKU']} - {r['PRODUCT_NAME']} (${r['UNIT_PRICE']:.2f})": r for _, r in prods_df.iterrows()}
                sel_p_label = st.selectbox("Product", list(p_dict.keys()), key="cart_p_select")
                sel_product = p_dict[sel_p_label]
            with item_c2:
                w_dict = {r["WAREHOUSE_NAME"]: int(r["WAREHOUSE_ID"]) for _, r in whs_df.iterrows()}
                sel_w_name = st.selectbox("Fulfill from Warehouse", list(w_dict.keys()), key="cart_w_select")
                sel_w_id = w_dict[sel_w_name]
            with item_c3:
                # Query available stock in that specific warehouse
                avail_query = db.execute_query(
                    "SELECT NVL(quantity_on_hand, 0) AS avail FROM INVENTORY WHERE product_id = :pid AND warehouse_id = :wid",
                    {"pid": int(sel_product["PRODUCT_ID"]), "wid": sel_w_id}
                )
                avail_units = int(avail_query.iloc[0]["AVAIL"]) if not avail_query.empty else 0
                st.caption(f"In Stock at WH: **{avail_units} units**")
                order_qty = st.number_input("Qty", min_value=1, max_value=max(avail_units, 1), value=1, step=1, key="cart_qty_input")
            with item_c4:
                st.write("")
                st.write("")
                if st.button("➕ Add to Cart", use_container_width=True, disabled=(avail_units <= 0)):
                    st.session_state.cart_items.append({
                        "product_id": int(sel_product["PRODUCT_ID"]),
                        "sku": sel_product["SKU"],
                        "product_name": sel_product["PRODUCT_NAME"],
                        "warehouse_id": sel_w_id,
                        "warehouse_name": sel_w_name,
                        "quantity": int(order_qty),
                        "unit_price": float(sel_product["UNIT_PRICE"]),
                        "subtotal": round(float(sel_product["UNIT_PRICE"]) * int(order_qty), 2)
                    })
                    st.success(f"Added {order_qty}x {sel_product['PRODUCT_NAME']} to cart!")
                    st.rerun()

            # Render current cart
            st.markdown("##### Current Cart Contents")
            if st.session_state.cart_items:
                cart_df = pd.DataFrame(st.session_state.cart_items)
                st.dataframe(
                    cart_df[["sku", "product_name", "warehouse_name", "quantity", "unit_price", "subtotal"]],
                    use_container_width=True,
                    column_config={
                        "sku": "SKU",
                        "product_name": "Product Name",
                        "warehouse_name": "Warehouse",
                        "quantity": "Quantity",
                        "unit_price": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
                        "subtotal": st.column_config.NumberColumn("Subtotal", format="$%.2f")
                    },
                    hide_index=True
                )

                # Order summary totals
                cart_subtotal = sum(i["subtotal"] for i in st.session_state.cart_items)
                cart_tax = round(cart_subtotal * 0.08, 2)
                cart_grand_total = round(cart_subtotal + cart_tax, 2)

                sum_c1, sum_c2 = st.columns([2, 1])
                with sum_c2:
                    st.markdown(f"""
                    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 16px; margin: 12px 0;">
                        <div>Cart Subtotal: <strong>{format_currency(cart_subtotal)}</strong></div>
                        <div>Estimated Tax (8%): <strong>{format_currency(cart_tax)}</strong></div>
                        <hr style="border-color: rgba(255,255,255,0.1); margin: 8px 0;">
                        <div style="font-size: 20px; font-weight: 800; color: #34D399;">Grand Total: {format_currency(cart_grand_total)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                act_c1, act_c2 = st.columns([1, 1])
                with act_c1:
                    if st.button("🗑️ Clear Cart", use_container_width=True):
                        st.session_state.cart_items = []
                        st.rerun()
                with act_c2:
                    if st.button("🚀 Place Order & Deduct Inventory (COMMIT)", use_container_width=True, type="primary"):
                        result = DMLManager.create_sales_order(
                            customer_id=selected_cust_id,
                            payment_method=selected_pay_method,
                            items=st.session_state.cart_items
                        )
                        if result["success"]:
                            st.session_state.cart_items = []
                            st.balloons()
                            st.success(f"🎉 {result['message']}")
                            st.info(f"Order #{result['order_number']} is now COMPLETED. Stock has been deducted across all warehouses.")
                            st.rerun()
                        else:
                            st.error(f"Order failed: {result['message']}")
            else:
                st.info("Your order cart is currently empty. Add products above to start building an order.")
