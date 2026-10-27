"""
Settings & Diagnostics View: Oracle connection inspector, configuration manager,
and database re-seeding / migration utility.
"""

import streamlit as st
import time
from database.connection import db
from database.db_init import initialize_database
from config import DB_CONFIG

def render_settings():
    st.markdown("### ⚙️ Database Diagnostics & Configuration")
    st.caption("Manage Oracle database credentials, test connectivity, inspect engine parameters, or reset sample data.")

    set_tab1, set_tab2, set_tab3 = st.tabs([
        "🩺 Connection Diagnostics", 
        "🔧 Connection Parameters", 
        "🔄 Database Reset & Re-Seed"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: CONNECTION DIAGNOSTICS
    # -------------------------------------------------------------------------
    with set_tab1:
        st.subheader("🩺 Oracle Connection Health Check")
        
        diag = db.test_connection()
        if diag["success"]:
            st.success("🟢 Connection Status: HEALTHY & ONLINE")
            d_c1, d_c2 = st.columns(2)
            with d_c1:
                st.markdown(f"""
                <div class="content-card">
                    <h5 style="color: #60A5FA; margin-top: 0;">Database Information</h5>
                    <div><strong>Oracle Version:</strong> {diag['version']}</div>
                    <div><strong>Database Banner:</strong> {diag['banner']}</div>
                    <div><strong>Total Tables in Schema:</strong> {diag['table_count']}</div>
                </div>
                """, unsafe_allow_html=True)
            with d_c2:
                st.markdown(f"""
                <div class="content-card">
                    <h5 style="color: #60A5FA; margin-top: 0;">Connection Details</h5>
                    <div><strong>Connected User:</strong> {diag['user']}</div>
                    <div><strong>Target DSN:</strong> {diag['dsn']}</div>
                    <div><strong>Driver Mode:</strong> Python oracledb (Thin Client Mode)</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"🔴 Connection Failed: {diag['message']}")
            st.info("Check if Oracle TNS Listener and database service are running on localhost:1521.")

        if st.button("🔄 Re-test Connection Ping", use_container_width=True):
            st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: CONNECTION PARAMETERS
    # -------------------------------------------------------------------------
    with set_tab2:
        st.subheader("🔧 Modify Connection Settings")
        st.caption("Update connection string parameters dynamically during project demonstration.")

        with st.form("db_config_form"):
            cfg_c1, cfg_c2 = st.columns(2)
            with cfg_c1:
                new_host = st.text_input("Host Address", value=DB_CONFIG.HOST)
                new_port = st.number_input("Port Number", value=DB_CONFIG.PORT, step=1)
                new_service = st.text_input("Service Name / PDB", value=DB_CONFIG.SERVICE_NAME)
            with cfg_c2:
                new_user = st.text_input("Username / Schema", value=DB_CONFIG.USER)
                new_password = st.text_input("Password", value=DB_CONFIG.PASSWORD, type="password")

            save_cfg = st.form_submit_button("Save & Reconnect", use_container_width=True, type="primary")
            if save_cfg:
                db.update_config(new_user, new_password, new_host, new_port, new_service)
                test_res = db.test_connection()
                if test_res["success"]:
                    st.success(f"✅ Successfully reconnected to Oracle as '{new_user}'!")
                    st.rerun()
                else:
                    st.error(f"❌ Connection failed with new credentials: {test_res['message']}")

    # -------------------------------------------------------------------------
    # TAB 3: RESET & RE-SEED DATABASE
    # -------------------------------------------------------------------------
    with set_tab3:
        st.subheader("🔄 Database Schema Re-initialization")
        st.warning("""
        ⚠️ **Caution**: This operation will run `01_ddl_schema.sql`, `02_dml_seed_data.sql`, `04_dcl_permissions.sql`, and `05_stored_procedures.sql`.
        All current tables will be recreated and refreshed with standard enterprise demonstration data.
        """)

        if st.button("🚀 Re-create Schema & Populate Seed Data", type="primary"):
            with st.spinner("Executing DDL, DML, DCL, and PL/SQL scripts on Oracle Database..."):
                start_time = time.time()
                try:
                    logs = initialize_database()
                    duration = round(time.time() - start_time, 2)
                    st.success(f"🎉 Database reset completed in {duration} seconds!")
                    with st.expander("Inspection Logs", expanded=True):
                        for log in logs:
                            st.text(log)
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Reset Error: {e}")
