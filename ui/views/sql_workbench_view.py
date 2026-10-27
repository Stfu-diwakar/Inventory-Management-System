"""
SQL Workbench & DBMS Demonstration View.
Interactive query console, pre-built concept demonstrations (Joins, Subqueries,
Aggregations, Window Functions), and Oracle Data Dictionary Schema Explorer.
"""

import time
import streamlit as st
import pandas as pd
from database.query_service import QueryService
from database.connection import db
from ui.components import render_sql_box, export_dataframe_button

def render_sql_workbench():
    st.markdown("### 📜 SQL Workbench & DBMS Concept Demonstrations")
    st.caption("Live interactive execution environment for testing complex Oracle SQL queries, Joins, Aggregations, and inspecting schema catalogs.")

    sql_tab1, sql_tab2, sql_tab3 = st.tabs([
        "💡 DBMS Concept Demonstrations",
        "💻 Interactive SQL Console",
        "🔍 Schema & Data Dictionary Explorer"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PRE-BUILT CONCEPT DEMONSTRATIONS
    # -------------------------------------------------------------------------
    with sql_tab1:
        st.subheader("💡 Curated Academic SQL Demonstrations")
        demo_queries = QueryService.get_demo_queries()

        # Group by category
        categories = list(dict.fromkeys(q["category"] for q in demo_queries))
        sel_cat = st.selectbox("Select DBMS Concept Category", categories)

        cat_queries = [q for q in demo_queries if q["category"] == sel_cat]
        q_options = {q["title"]: q for q in cat_queries}
        sel_q_title = st.selectbox("Select Demonstration Query", list(q_options.keys()))
        selected_q = q_options[sel_q_title]

        render_sql_box(
            title=selected_q["title"],
            concept=selected_q["concept"],
            sql=selected_q["sql"]
        )

        if st.button("🚀 Execute Demonstration Query", type="primary", key="exec_demo_btn"):
            try:
                start_time = time.time()
                result_df = QueryService.execute_custom_query(selected_q["sql"])
                duration_ms = round((time.time() - start_time) * 1000, 2)

                st.success(f"Query executed successfully in {duration_ms} ms. Returned {len(result_df)} rows.")
                if not result_df.empty:
                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                    export_dataframe_button(result_df, f"query_result_{selected_q['id']}.csv")
                else:
                    st.info("Query returned 0 rows.")
            except Exception as e:
                st.error(f"Oracle Execution Error: {e}")

    # -------------------------------------------------------------------------
    # TAB 2: INTERACTIVE SQL CONSOLE
    # -------------------------------------------------------------------------
    with sql_tab2:
        st.subheader("💻 Interactive SQL Query Console")
        st.caption("Type and run custom Oracle SQL queries directly against the connected database.")

        sample_query = "SELECT table_name, num_rows, status FROM user_tables ORDER BY table_name"
        user_sql = st.text_area(
            "SQL Query Editor",
            value=sample_query,
            height=140,
            placeholder="Type your SELECT / INSERT / UPDATE query here..."
        )

        run_col1, run_col2 = st.columns([1, 4])
        with run_col1:
            run_btn = st.button("⚡ Run Query", type="primary", use_container_width=True)

        if run_btn:
            if not user_sql.strip():
                st.warning("Please enter a SQL statement.")
            else:
                cleaned_sql = user_sql.strip().rstrip(";")
                is_select = cleaned_sql.upper().startswith(("SELECT", "WITH"))

                try:
                    start_time = time.time()
                    if is_select:
                        result_df = db.execute_query(cleaned_sql)
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        st.success(f"Query returned {len(result_df)} rows in {elapsed} ms.")
                        if not result_df.empty:
                            st.dataframe(result_df, use_container_width=True, hide_index=True)
                            export_dataframe_button(result_df, "custom_query_export.csv")
                        else:
                            st.info("Query completed with zero rows returned.")
                    else:
                        rowcount = db.execute_dml(cleaned_sql)
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        st.success(f"Statement executed in {elapsed} ms. ({rowcount} row(s) affected). Transaction committed.")
                except Exception as e:
                    st.error(f"Oracle SQL Error: {e}")

    # -------------------------------------------------------------------------
    # TAB 3: SCHEMA EXPLORER
    # -------------------------------------------------------------------------
    with sql_tab3:
        st.subheader("🔍 Oracle Data Dictionary Schema Explorer")
        
        dict_tab1, dict_tab2, dict_tab3, dict_tab4 = st.tabs([
            "📋 Tables (USER_TABLES)",
            "🧱 Table Columns & Types",
            "🔗 Constraints (PK, FK, Check)",
            "👁️ Database Views & Triggers"
        ])

        with dict_tab1:
            try:
                tables_df = db.execute_query("""
                    SELECT 
                        table_name,
                        tablespace_name,
                        status,
                        num_rows,
                        last_analyzed
                    FROM USER_TABLES
                    ORDER BY table_name
                """)
                st.dataframe(tables_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error fetching user tables: {e}")

        with dict_tab2:
            try:
                t_list = db.execute_query("SELECT table_name FROM user_tables ORDER BY table_name")
                if not t_list.empty:
                    sel_tbl = st.selectbox("Inspect Columns for Table", t_list["TABLE_NAME"].tolist())
                    cols_df = db.execute_query("""
                        SELECT 
                            column_id,
                            column_name,
                            data_type,
                            data_length,
                            data_precision,
                            data_scale,
                            nullable,
                            data_default
                        FROM USER_TAB_COLUMNS
                        WHERE table_name = :tbl
                        ORDER BY column_id
                    """, {"tbl": sel_tbl})
                    st.dataframe(cols_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error fetching columns: {e}")

        with dict_tab3:
            try:
                constraints_df = db.execute_query("""
                    SELECT 
                        constraint_name,
                        constraint_type,
                        table_name,
                        r_constraint_name AS referenced_constraint,
                        status
                    FROM USER_CONSTRAINTS
                    WHERE table_name IN (SELECT table_name FROM user_tables)
                    ORDER BY table_name, constraint_type
                """)
                st.dataframe(
                    constraints_df,
                    use_container_width=True,
                    column_config={
                        "CONSTRAINT_TYPE": st.column_config.TextColumn("Type (P=Primary, R=Foreign, C=Check, U=Unique)")
                    },
                    hide_index=True
                )
            except Exception as e:
                st.error(f"Error fetching constraints: {e}")

        with dict_tab4:
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                st.markdown("##### Predefined Database Views")
                try:
                    views_df = db.execute_query("SELECT view_name, text_length FROM user_views ORDER BY view_name")
                    st.dataframe(views_df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")
            with v_col2:
                st.markdown("##### Predefined Database Triggers")
                try:
                    trg_df = db.execute_query("""
                        SELECT trigger_name, trigger_type, triggering_event, table_name, status
                        FROM USER_TRIGGERS
                        ORDER BY trigger_name
                    """)
                    st.dataframe(trg_df, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Error: {e}")
