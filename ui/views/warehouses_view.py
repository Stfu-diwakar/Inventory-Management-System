"""
Warehouses & Inventory Matrix View: Capacity tracking, multi-facility stock matrix,
and direct stock adjustments using Oracle MERGE statement.
"""

import streamlit as st
import pandas as pd
from database.dml_manager import DMLManager
from ui.components import export_dataframe_button

def render_warehouses():
    st.markdown("### 🏢 Warehouses & Inventory Stock Matrix")
    st.caption("Manage enterprise storage facilities, track space utilization, and inspect stock distributions across locations.")

    w_tab1, w_tab2, w_tab3, w_tab4 = st.tabs([
        "📍 Facilities Overview",
        "📊 Stock-on-Hand Matrix",
        "⚡ Direct Stock Adjustment (MERGE)",
        "➕ Add New Warehouse"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: FACILITIES OVERVIEW
    # -------------------------------------------------------------------------
    with w_tab1:
        warehouses_df = DMLManager.get_warehouses()
        if not warehouses_df.empty:
            for _, wh in warehouses_df.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="content-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h4 style="margin: 0; color: #60A5FA;">{wh['WAREHOUSE_NAME']}</h4>
                            <span class="badge badge-active">{wh['STATUS']}</span>
                        </div>
                        <div style="font-size: 13px; color: #94A3B8; margin-bottom: 12px;">
                            📍 {wh['LOCATION']} | 👤 Manager: <strong>{wh['MANAGER_NAME']}</strong> ({wh['CONTACT_NUMBER']})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    p_col1, p_col2 = st.columns([3, 1])
                    with p_col1:
                        occ = float(wh['OCCUPANCY_PCT'])
                        st.progress(min(occ / 100.0, 1.0))
                    with p_col2:
                        st.markdown(f"**{wh['TOTAL_UNITS_STORED']:,} / {wh['CAPACITY']:,} units** ({occ}%)")
                    st.divider()
        else:
            st.info("No warehouses found.")

    # -------------------------------------------------------------------------
    # TAB 2: MULTI-FACILITY STOCK-ON-HAND MATRIX
    # -------------------------------------------------------------------------
    with w_tab2:
        st.subheader("📊 Product Inventory by Warehouse")
        matrix_df = DMLManager.get_inventory_matrix()

        if not matrix_df.empty:
            # Pivot table for product vs warehouse
            pivot_stock = matrix_df.pivot_table(
                index=["SKU", "PRODUCT_NAME", "CATEGORY_NAME"],
                columns="WAREHOUSE_NAME",
                values="STOCK_ON_HAND",
                fill_value=0
            ).reset_index()

            st.dataframe(
                pivot_stock,
                use_container_width=True,
                hide_index=True
            )
            export_dataframe_button(pivot_stock, "inventory_stock_matrix.csv")

            st.markdown("##### Detailed Allocation Breakdown")
            st.dataframe(
                matrix_df[["SKU", "PRODUCT_NAME", "WAREHOUSE_NAME", "STOCK_ON_HAND", "REORDER_LEVEL", "STOCK_VALUATION", "LAST_UPDATED"]],
                use_container_width=True,
                column_config={
                    "STOCK_ON_HAND": st.column_config.NumberColumn("Quantity on Hand"),
                    "STOCK_VALUATION": st.column_config.NumberColumn("Valuation", format="$%.2f")
                },
                hide_index=True
            )
        else:
            st.info("No inventory allocations found.")

    # -------------------------------------------------------------------------
    # TAB 3: DIRECT STOCK ADJUSTMENT (ORACLE MERGE STATEMENT)
    # -------------------------------------------------------------------------
    with w_tab3:
        st.subheader("⚡ Quick Stock Adjustment (MERGE Upsert)")
        st.caption("Demonstrates the Oracle SQL MERGE statement to automatically insert or update stock-on-hand records.")

        prods_df = DMLManager.get_products()
        whs_df = DMLManager.get_warehouses()

        if not prods_df.empty and not whs_df.empty:
            with st.form("quick_adjust_form"):
                adj_col1, adj_col2, adj_col3 = st.columns(3)
                with adj_col1:
                    p_options = {f"{r['SKU']} - {r['PRODUCT_NAME']}": int(r["PRODUCT_ID"]) for _, r in prods_df.iterrows()}
                    selected_p_label = st.selectbox("Select Product", list(p_options.keys()))
                    selected_p_id = p_options[selected_p_label]
                with adj_col2:
                    w_options = {r["WAREHOUSE_NAME"]: int(r["WAREHOUSE_ID"]) for _, r in whs_df.iterrows()}
                    selected_w_label = st.selectbox("Select Warehouse", list(w_options.keys()))
                    selected_w_id = w_options[selected_w_label]
                with adj_col3:
                    new_qty = st.number_input("New Exact Stock Count", min_value=0, value=25, step=1)

                adjust_btn = st.form_submit_button("⚡ Execute MERGE Adjustment", use_container_width=True, type="primary")
                if adjust_btn:
                    try:
                        DMLManager.update_inventory_quantity(
                            product_id=selected_p_id,
                            warehouse_id=selected_w_id,
                            new_quantity=new_qty
                        )
                        st.success(f"✅ Successfully merged stock! {selected_p_label} in {selected_w_label} is now {new_qty} units.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"MERGE Error: {e}")

    # -------------------------------------------------------------------------
    # TAB 4: ADD NEW WAREHOUSE
    # -------------------------------------------------------------------------
    with w_tab4:
        st.subheader("➕ Register New Storage Facility")
        with st.form("new_warehouse_form", clear_on_submit=True):
            wh_c1, wh_c2 = st.columns(2)
            with wh_c1:
                wh_name = st.text_input("Warehouse Name*", placeholder="e.g. Northwest Logistics Hub")
                wh_loc = st.text_input("Physical Location / Address*", placeholder="e.g. 500 Freight Way, Seattle, WA")
                wh_cap = st.number_input("Max Storage Capacity (Units)*", min_value=1000, value=20000, step=1000)
            with wh_c2:
                wh_mgr = st.text_input("Warehouse Manager Name*", placeholder="e.g. Michael Thorne")
                wh_phone = st.text_input("Contact Phone*", placeholder="e.g. +1-206-555-0811")
                wh_status = st.selectbox("Initial Status", ["ACTIVE", "MAINTENANCE"])

            submit_wh = st.form_submit_button("Create Warehouse", use_container_width=True)
            if submit_wh:
                if not wh_name.strip() or not wh_loc.strip():
                    st.error("Warehouse Name and Location are required.")
                else:
                    try:
                        DMLManager.create_warehouse(wh_name, wh_loc, wh_cap, wh_mgr, wh_phone, wh_status)
                        st.success(f"✅ Warehouse '{wh_name}' registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
