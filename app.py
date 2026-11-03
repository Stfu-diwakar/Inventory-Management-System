"""
Main Streamlit Application Entrypoint.
Project: Inventory Management System (DBMS Project)
Database: Oracle SQL (23ai / 21c / 19c)
"""

import streamlit as st
from config import APP_CONFIG
from database.connection import db
from ui.styles import get_custom_css
from ui.components import render_header

# 1. Page Configuration
st.set_page_config(
    page_title=f"{APP_CONFIG.APP_NAME} | Oracle SQL DBMS",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject CSS Design System
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 3. Import View Modules
from ui.views.dashboard_view import render_dashboard
from ui.views.products_view import render_products
from ui.views.warehouses_view import render_warehouses
from ui.views.orders_view import render_orders
from ui.views.stock_movement_view import render_stock_movement
from ui.views.partners_view import render_partners
from ui.views.sql_workbench_view import render_sql_workbench
from ui.views.dcl_security_view import render_dcl_security
from ui.views.settings_view import render_settings

# 4. Check Oracle Connection Status (Cached or Instant)
@st.cache_data(ttl=15)
def get_cached_status():
    return db.test_connection()

db_status = get_cached_status()

# 5. Render Top Header
render_header(
    title=f"📦 {APP_CONFIG.APP_NAME}",
    subtitle=f"{APP_CONFIG.PROJECT_TITLE} • Powered by {APP_CONFIG.DATABASE_SYSTEM}",
    db_status=db_status
)

# 6. Sidebar Navigation
with st.sidebar:
    st.markdown("### 🏢 Navigation Menu")
    menu_options = [
        "📊 Dashboard & Analytics",
        "📦 Products & Catalog (CRUD)",
        "🏢 Warehouses & Stock Matrix",
        "🛒 Orders & POS Billing",
        "🔄 Stock Movements & Transfers",
        "👥 Suppliers & Customers",
        "📜 SQL Workbench & DBMS Demo",
        "🛡️ DCL, Roles & Audit Security",
        "⚙️ Database Settings & Diagnostics"
    ]

    selected_menu = st.radio("Go to:", menu_options, index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 🔌 Oracle SQL Status")
    if db_status.get("success"):
        st.markdown(
            f"- **Status**: 🟢 <span style='color:#10B981;font-weight:600;'>Online</span>\n"
            f"- **Engine**: Oracle 23ai Free\n"
            f"- **User**: `{db_status.get('user')}`\n"
            f"- **Tables**: `{db_status.get('table_count')}`",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "- **Status**: 🔴 <span style='color:#EF4444;font-weight:600;'>Disconnected</span>\n"
            "- Please verify Oracle Service is active.",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption("DBMS Academic Project\nSemester 3 Data Analytics\nInterface: Python + Streamlit")

# 7. Route to Selected View
if not db_status.get("success") and selected_menu != "⚙️ Database Settings & Diagnostics":
    st.error(f"Cannot connect to Oracle SQL Database: {db_status.get('message')}")
    st.info("Please navigate to **⚙️ Database Settings & Diagnostics** to adjust credentials or start the Oracle service.")
else:
    if selected_menu == "📊 Dashboard & Analytics":
        render_dashboard()
    elif selected_menu == "📦 Products & Catalog (CRUD)":
        render_products()
    elif selected_menu == "🏢 Warehouses & Stock Matrix":
        render_warehouses()
    elif selected_menu == "🛒 Orders & POS Billing":
        render_orders()
    elif selected_menu == "🔄 Stock Movements & Transfers":
        render_stock_movement()
    elif selected_menu == "👥 Suppliers & Customers":
        render_partners()
    elif selected_menu == "📜 SQL Workbench & DBMS Demo":
        render_sql_workbench()
    elif selected_menu == "🛡️ DCL, Roles & Audit Security":
        render_dcl_security()
    elif selected_menu == "⚙️ Database Settings & Diagnostics":
        render_settings()
