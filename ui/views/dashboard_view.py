"""
Dashboard View: Executive analytics, real-time KPIs, Plotly charts,
and critical low stock inventory alerts.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database.dml_manager import DMLManager
from database.connection import db
from ui.components import render_kpi_card, format_currency

def render_dashboard():
    # 1. Fetch live metrics from Oracle SQL
    with st.spinner("Loading database metrics..."):
        metrics = DMLManager.get_dashboard_metrics()

    # 2. Render KPI Cards Grid
    col1, col2, col3, col4, col5 = st.columns(5)
    render_kpi_card(col1, "Total Products", f"{metrics.get('total_products', 0):,}", "Catalog SKUs")
    render_kpi_card(col2, "Total Stock Units", f"{metrics.get('total_units', 0):,}", "Across all warehouses")
    render_kpi_card(col3, "Inventory Valuation", format_currency(metrics.get('retail_valuation', 0.0)), f"Cost: {format_currency(metrics.get('cost_valuation', 0.0))}")
    render_kpi_card(col4, "Low Stock Alerts", f"{metrics.get('low_stock_count', 0)} Items", "Needs replenishment", delta="-Urgent")
    render_kpi_card(col5, "Total Revenue", format_currency(metrics.get('total_revenue', 0.0)), f"{metrics.get('total_orders', 0)} orders completed")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Visual Charts Grid (Plotly)
    chart_col1, chart_col2 = st.columns([1, 1])

    with chart_col1:
        st.subheader("📦 Inventory by Category")
        try:
            cat_df = db.execute_query("""
                SELECT 
                    c.category_name, 
                    NVL(SUM(i.quantity_on_hand), 0) AS total_units,
                    ROUND(NVL(SUM(i.quantity_on_hand * p.unit_price), 0), 2) AS valuation
                FROM CATEGORIES c
                LEFT JOIN PRODUCTS p ON c.category_id = p.category_id
                LEFT JOIN INVENTORY i ON p.product_id = i.product_id
                GROUP BY c.category_name
                HAVING NVL(SUM(i.quantity_on_hand), 0) > 0
                ORDER BY total_units DESC
            """)
            if not cat_df.empty:
                fig_cat = px.pie(
                    cat_df, 
                    names="CATEGORY_NAME", 
                    values="TOTAL_UNITS", 
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_cat.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300,
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            else:
                st.info("No category inventory data available.")
        except Exception as e:
            st.error(f"Error loading category chart: {e}")

    with chart_col2:
        st.subheader("🏢 Warehouse Occupancy & Capacity")
        try:
            wh_df = db.execute_query("""
                SELECT 
                    warehouse_name,
                    current_stock_units,
                    capacity,
                    utilization_percentage
                FROM VW_WAREHOUSE_OCCUPANCY
                ORDER BY utilization_percentage DESC
            """)
            if not wh_df.empty:
                fig_wh = go.Figure()
                fig_wh.add_trace(go.Bar(
                    name="Current Stock",
                    x=wh_df["WAREHOUSE_NAME"],
                    y=wh_df["CURRENT_STOCK_UNITS"],
                    marker_color="#3B82F6"
                ))
                fig_wh.add_trace(go.Bar(
                    name="Total Capacity",
                    x=wh_df["WAREHOUSE_NAME"],
                    y=wh_df["CAPACITY"],
                    marker_color="rgba(148, 163, 184, 0.3)"
                ))
                fig_wh.update_layout(
                    barmode="group",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
                )
                st.plotly_chart(fig_wh, use_container_width=True)
            else:
                st.info("No warehouse data available.")
        except Exception as e:
            st.error(f"Error loading warehouse chart: {e}")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 4. Critical Low Stock Alerts Table
    st.subheader("⚠️ Critical Low Stock & Reorder Alerts")
    try:
        low_stock_df = db.execute_query("""
            SELECT 
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
            ORDER BY units_needed DESC
        """)
        if not low_stock_df.empty:
            st.dataframe(
                low_stock_df,
                use_container_width=True,
                column_config={
                    "SKU": st.column_config.TextColumn("SKU Code", width="small"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product Name", width="large"),
                    "CATEGORY_NAME": st.column_config.TextColumn("Category"),
                    "TOTAL_STOCK": st.column_config.ProgressColumn("Stock Level", format="%d", min_value=0, max_value=50),
                    "REORDER_LEVEL": st.column_config.NumberColumn("Threshold"),
                    "UNITS_NEEDED": st.column_config.NumberColumn("Deficit Units"),
                    "COST_PRICE": st.column_config.NumberColumn("Unit Cost", format="$%.2f"),
                    "STOCK_STATUS": st.column_config.TextColumn("Status")
                },
                hide_index=True
            )
        else:
            st.success("🎉 All catalog inventory is healthy! No products currently below reorder levels.")
    except Exception as e:
        st.error(f"Error loading low stock alerts: {e}")

    # 5. Recent System Stock Movements
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.subheader("🔄 Recent Stock Movements Ledger")
    try:
        trans_df = DMLManager.get_stock_transactions(limit=10)
        if not trans_df.empty:
            st.dataframe(
                trans_df,
                use_container_width=True,
                column_config={
                    "TRANSACTION_ID": st.column_config.NumberColumn("Tx ID", width="small"),
                    "TIMESTAMP": st.column_config.TextColumn("Date & Time"),
                    "SKU": st.column_config.TextColumn("SKU"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product", width="medium"),
                    "WAREHOUSE_NAME": st.column_config.TextColumn("Warehouse"),
                    "TRANSACTION_TYPE": st.column_config.TextColumn("Type"),
                    "QUANTITY": st.column_config.NumberColumn("Units Changed"),
                    "REFERENCE_ID": st.column_config.TextColumn("Reference"),
                    "PERFORMED_BY": st.column_config.TextColumn("Operator")
                },
                hide_index=True
            )
        else:
            st.info("No transaction movements recorded yet.")
    except Exception as e:
        st.error(f"Error loading recent transactions: {e}")
