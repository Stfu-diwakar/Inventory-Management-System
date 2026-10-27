"""
Stock Movements View: Stock-In (Purchases), Stock-Out (Dispatches),
Inter-Warehouse Transfers via PL/SQL Stored Procedures, and Complete Audit Ledger.
"""

import streamlit as st
import pandas as pd
from database.dml_manager import DMLManager
from database.connection import db
from ui.components import export_dataframe_button

def render_stock_movement():
    st.markdown("### 🔄 Stock Movements & Warehouse Transfers")
    st.caption("Execute verified stock transactions using PL/SQL stored procedures (SP_PROCESS_STOCK_MOVEMENT & SP_TRANSFER_STOCK).")

    sm_tab1, sm_tab2, sm_tab3, sm_tab4 = st.tabs([
        "📜 Transaction Ledger",
        "📥 Stock In (Receive)",
        "📤 Stock Out (Dispatch)",
        "🚚 Warehouse Transfer (PL/SQL)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: TRANSACTION LEDGER
    # -------------------------------------------------------------------------
    with sm_tab1:
        st.subheader("📜 System Stock Movement Ledger")
        
        fil_col1, fil_col2 = st.columns(2)
        with fil_col1:
            tx_type_filter = st.selectbox("Filter Transaction Type", ["ALL", "STOCK_IN", "STOCK_OUT", "TRANSFER_IN", "TRANSFER_OUT", "ADJUSTMENT"])
        with fil_col2:
            limit_val = st.slider("Max Rows to Display", min_value=10, max_value=200, value=50, step=10)

        tx_df = DMLManager.get_stock_transactions(limit=limit_val)
        if tx_type_filter != "ALL" and not tx_df.empty:
            tx_df = tx_df[tx_df["TRANSACTION_TYPE"] == tx_type_filter]

        if not tx_df.empty:
            st.dataframe(
                tx_df,
                use_container_width=True,
                column_config={
                    "TRANSACTION_ID": st.column_config.NumberColumn("Tx ID", width="small"),
                    "TIMESTAMP": st.column_config.TextColumn("Timestamp"),
                    "SKU": st.column_config.TextColumn("SKU"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product", width="large"),
                    "WAREHOUSE_NAME": st.column_config.TextColumn("Warehouse"),
                    "TRANSACTION_TYPE": st.column_config.TextColumn("Action"),
                    "QUANTITY": st.column_config.NumberColumn("Quantity"),
                    "REFERENCE_ID": st.column_config.TextColumn("Reference"),
                    "NOTES": st.column_config.TextColumn("Notes"),
                    "PERFORMED_BY": st.column_config.TextColumn("Operator")
                },
                hide_index=True
            )
            export_dataframe_button(tx_df, "stock_transactions_ledger.csv")
        else:
            st.info("No transaction records found.")

    # -------------------------------------------------------------------------
    # TAB 2: STOCK IN (RECEIVE)
    # -------------------------------------------------------------------------
    with sm_tab2:
        st.subheader("📥 Receive Inbound Inventory (Stock In)")
        st.caption("Increases warehouse inventory and records a STOCK_IN ledger entry via PL/SQL procedure.")

        prods_df = DMLManager.get_products()
        whs_df = DMLManager.get_warehouses()

        if not prods_df.empty and not whs_df.empty:
            with st.form("stock_in_form", clear_on_submit=True):
                in_c1, in_c2 = st.columns(2)
                with in_c1:
                    p_opts = {f"{r['SKU']} - {r['PRODUCT_NAME']}": int(r['PRODUCT_ID']) for _, r in prods_df.iterrows()}
                    sel_in_p = st.selectbox("Product", list(p_opts.keys()))
                    in_pid = p_opts[sel_in_p]

                    w_opts = {r['WAREHOUSE_NAME']: int(r['WAREHOUSE_ID']) for _, r in whs_df.iterrows()}
                    sel_in_w = st.selectbox("Receiving Warehouse", list(w_opts.keys()))
                    in_wid = w_opts[sel_in_w]
                with in_c2:
                    in_qty = st.number_input("Units to Receive*", min_value=1, value=50, step=1)
                    in_ref = st.text_input("PO / Reference Number*", placeholder="e.g. PO-2026-9021")
                    in_notes = st.text_input("Notes / Description", placeholder="e.g. Batch shipment received in good condition")

                submit_in = st.form_submit_button("📥 Receive Stock (Execute PL/SQL)", use_container_width=True, type="primary")
                if submit_in:
                    success, msg = db.call_stock_movement_procedure(
                        product_id=in_pid,
                        warehouse_id=in_wid,
                        transaction_type="STOCK_IN",
                        quantity=in_qty,
                        reference_id=in_ref or "MANUAL_IN",
                        notes=in_notes or "Manual Stock In",
                        performed_by="INVENTORY_MANAGER"
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"Failed: {msg}")

    # -------------------------------------------------------------------------
    # TAB 3: STOCK OUT (DISPATCH)
    # -------------------------------------------------------------------------
    with sm_tab3:
        st.subheader("📤 Manual Stock Dispatch / Write-Off (Stock Out)")
        st.caption("Deducts units from warehouse. Stock cannot go negative.")

        if not prods_df.empty and not whs_df.empty:
            with st.form("stock_out_form", clear_on_submit=True):
                out_c1, out_c2 = st.columns(2)
                with out_c1:
                    sel_out_p = st.selectbox("Product", list(p_opts.keys()), key="out_p_sel")
                    out_pid = p_opts[sel_out_p]
                    sel_out_w = st.selectbox("Warehouse", list(w_opts.keys()), key="out_w_sel")
                    out_wid = w_opts[sel_out_w]
                with out_c2:
                    out_qty = st.number_input("Units to Dispatch*", min_value=1, value=5, step=1)
                    out_ref = st.text_input("Dispatch Reference*", placeholder="e.g. DSP-2026-102")
                    out_notes = st.text_input("Reason / Notes", placeholder="e.g. Damaged during handling / sample delivery")

                submit_out = st.form_submit_button("📤 Dispatch Stock", use_container_width=True)
                if submit_out:
                    success, msg = db.call_stock_movement_procedure(
                        product_id=out_pid,
                        warehouse_id=out_wid,
                        transaction_type="STOCK_OUT",
                        quantity=-out_qty,
                        reference_id=out_ref or "MANUAL_OUT",
                        notes=out_notes or "Manual Dispatch",
                        performed_by="INVENTORY_MANAGER"
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"Failed: {msg}")

    # -------------------------------------------------------------------------
    # TAB 4: WAREHOUSE-TO-WAREHOUSE TRANSFER (PL/SQL SP_TRANSFER_STOCK)
    # -------------------------------------------------------------------------
    with sm_tab4:
        st.subheader("🚚 Inter-Warehouse Stock Transfer")
        st.caption("Calls PL/SQL Stored Procedure SP_TRANSFER_STOCK for atomic two-phase transfer with balance validation.")

        if not prods_df.empty and not whs_df.empty:
            with st.form("transfer_form", clear_on_submit=True):
                trf_c1, trf_c2 = st.columns(2)
                with trf_c1:
                    sel_trf_p = st.selectbox("Product to Transfer", list(p_opts.keys()), key="trf_p_sel")
                    trf_pid = p_opts[sel_trf_p]
                    sel_from_w = st.selectbox("Source Warehouse (Deduct From)", list(w_opts.keys()), key="trf_from_w")
                    from_wid = w_opts[sel_from_w]
                with trf_c2:
                    # Filter out source warehouse from destination
                    dest_opts = {k: v for k, v in w_opts.items() if v != from_wid}
                    sel_to_w = st.selectbox("Destination Warehouse (Add To)", list(dest_opts.keys()), key="trf_to_w")
                    to_wid = dest_opts[sel_to_w]
                    trf_qty = st.number_input("Transfer Quantity (Units)*", min_value=1, value=10, step=1)
                
                trf_ref = st.text_input("Transfer Order Reference", placeholder="e.g. TRF-NY-SF-901")
                trf_notes = st.text_input("Transfer Notes", placeholder="e.g. Rebalancing regional stock for peak demand")

                submit_trf = st.form_submit_button("🚚 Execute Atomic Transfer (PL/SQL)", use_container_width=True, type="primary")
                if submit_trf:
                    success, msg = db.call_transfer_procedure(
                        product_id=trf_pid,
                        from_wh_id=from_wid,
                        to_wh_id=to_wid,
                        quantity=trf_qty,
                        reference_id=trf_ref or "TRANSFER",
                        notes=trf_notes or "Inter-facility transfer",
                        performed_by="LOGISTICS_MANAGER"
                    )
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"Transfer Error: {msg}")
