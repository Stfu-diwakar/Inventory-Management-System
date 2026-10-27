"""
DCL (Data Control Language) & Security View.
Demonstrates Role-Based Access Control (RBAC), GRANT and REVOKE operations,
Oracle Data Dictionary Inspection (USER_TAB_PRIVS_MADE), and Audit Trails.
"""

import streamlit as st
import pandas as pd
from database.dcl_service import DCLService
from database.dml_manager import DMLManager
from ui.components import export_dataframe_button

def render_dcl_security():
    st.markdown("### 🛡️ DCL (Data Control Language) & Security")
    st.caption("Demonstrate Oracle SQL security mechanisms: User Roles, Fine-Grained Object Privileges (GRANT & REVOKE), and DML Audit Logs.")

    dcl_tab1, dcl_tab2, dcl_tab3, dcl_tab4 = st.tabs([
        "📊 RBAC Privilege Matrix",
        "🔍 Data Dictionary (USER_TAB_PRIVS_MADE)",
        "⚡ Interactive GRANT / REVOKE Runner",
        "📜 System Audit Trail (AUDIT_LOGS)"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: RBAC PRIVILEGE MATRIX
    # -------------------------------------------------------------------------
    with dcl_tab1:
        st.subheader("📊 Role-Based Access Control (RBAC) Matrix")
        st.markdown("""
        In enterprise DBMS architectures, users are assigned to **Roles**, and roles are granted specific **Object Privileges** (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) 
        following the **Principle of Least Privilege (PoLP)**.
        """)

        matrix_df = DCLService.get_role_matrix()
        st.dataframe(
            matrix_df,
            use_container_width=True,
            column_config={
                "Table / Resource": st.column_config.TextColumn("Database Object", width="medium"),
                "INV_ADMIN_ROLE": st.column_config.TextColumn("Admin (Full)", width="small"),
                "INV_MANAGER_ROLE": st.column_config.TextColumn("Inventory Mgr", width="medium"),
                "INV_STAFF_ROLE": st.column_config.TextColumn("Cashier / Staff", width="medium"),
                "INV_AUDITOR_ROLE": st.column_config.TextColumn("Auditor (Read-Only)", width="small")
            },
            hide_index=True
        )

        st.markdown("##### Active Security Roles in Oracle Database")
        roles_df = DCLService.get_database_roles()
        st.dataframe(roles_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 2: DATA DICTIONARY GRANTS
    # -------------------------------------------------------------------------
    with dcl_tab2:
        st.subheader("🔍 Active Object Grants from Oracle Data Dictionary")
        st.caption("Live query from `USER_TAB_PRIVS_MADE` showing exactly which privileges have been granted to roles.")

        try:
            privs_df = DCLService.get_granted_privileges()
            if not privs_df.empty:
                # Filter by role
                roles_avail = ["ALL"] + sorted(privs_df["GRANTEE"].unique().tolist())
                sel_filter_role = st.selectbox("Filter by Grantee Role", roles_avail)

                display_df = privs_df if sel_filter_role == "ALL" else privs_df[privs_df["GRANTEE"] == sel_filter_role]

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    column_config={
                        "GRANTEE": st.column_config.TextColumn("Grantee / Role", width="medium"),
                        "TABLE_NAME": st.column_config.TextColumn("Target Table / View", width="large"),
                        "PRIVILEGE": st.column_config.TextColumn("Privilege"),
                        "GRANTABLE": st.column_config.TextColumn("Grant Option")
                    },
                    hide_index=True
                )
                export_dataframe_button(display_df, "oracle_dcl_grants.csv")
            else:
                st.info("No explicit object grants found.")
        except Exception as e:
            st.error(f"Error fetching privileges: {e}")

    # -------------------------------------------------------------------------
    # TAB 3: INTERACTIVE GRANT / REVOKE RUNNER
    # -------------------------------------------------------------------------
    with dcl_tab3:
        st.subheader("⚡ Live DCL Command Execution")
        st.caption("Execute GRANT and REVOKE commands interactively on the live Oracle database and observe immediate reflection in the Data Dictionary.")

        dcl_col1, dcl_col2, dcl_col3 = st.columns(3)
        with dcl_col1:
            sel_priv = st.selectbox("Select Privilege", ["SELECT", "INSERT", "UPDATE", "DELETE", "ALL"])
        with dcl_col2:
            sel_tbl = st.selectbox("Select Target Table", [
                "PRODUCTS", "INVENTORY", "ORDERS", "ORDER_ITEMS", 
                "CATEGORIES", "SUPPLIERS", "WAREHOUSES", "CUSTOMERS", "STOCK_TRANSACTIONS"
            ])
        with dcl_col3:
            sel_target_role = st.selectbox("Select Target Role", [
                "INV_MANAGER_ROLE", "INV_STAFF_ROLE", "INV_AUDITOR_ROLE"
            ])

        g_btn1, g_btn2 = st.columns(2)
        with g_btn1:
            if st.button("🔑 Execute GRANT Command", use_container_width=True, type="primary"):
                result_msg = DCLService.execute_grant(sel_priv, sel_tbl, sel_target_role)
                if "Successfully" in result_msg:
                    st.success(f"✅ {result_msg}")
                    st.rerun()
                else:
                    st.error(result_msg)

        with g_btn2:
            if st.button("🚫 Execute REVOKE Command", use_container_width=True):
                result_msg = DCLService.execute_revoke(sel_priv, sel_tbl, sel_target_role)
                if "Successfully" in result_msg:
                    st.warning(f"⚠️ {result_msg}")
                    st.rerun()
                else:
                    st.error(result_msg)

        st.markdown("---")
        st.markdown("##### DCL SQL Syntax Reference for Viva:")
        st.code(f"""-- Example GRANT Syntax:
GRANT {sel_priv} ON {sel_tbl} TO {sel_target_role};

-- Example REVOKE Syntax:
REVOKE {sel_priv} ON {sel_tbl} FROM {sel_target_role};""", language="sql")

    # -------------------------------------------------------------------------
    # TAB 4: SYSTEM AUDIT TRAIL
    # -------------------------------------------------------------------------
    with dcl_tab4:
        st.subheader("📜 System Audit Trail (AUDIT_LOGS)")
        st.caption("Logged automatically by Oracle database triggers when records are modified or deleted.")

        try:
            audit_df = DMLManager.get_audit_logs(limit=100)
            if not audit_df.empty:
                st.dataframe(
                    audit_df,
                    use_container_width=True,
                    column_config={
                        "LOG_ID": st.column_config.NumberColumn("ID", width="small"),
                        "TIMESTAMP": st.column_config.TextColumn("Timestamp"),
                        "TABLE_NAME": st.column_config.TextColumn("Table"),
                        "ACTION_TYPE": st.column_config.TextColumn("Action"),
                        "RECORD_ID": st.column_config.TextColumn("Record ID"),
                        "PERFORMED_BY": st.column_config.TextColumn("DB User"),
                        "DETAILS": st.column_config.TextColumn("Change Details", width="large")
                    },
                    hide_index=True
                )
                export_dataframe_button(audit_df, "system_audit_logs.csv")
            else:
                st.info("No audit logs recorded yet.")
        except Exception as e:
            st.error(f"Error reading audit logs: {e}")
