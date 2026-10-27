"""
Reusable UI components and widgets for the Inventory Management System.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

def render_header(title: str, subtitle: str, db_status: Optional[Dict[str, Any]] = None):
    """Renders the top navigation and status header."""
    status_html = ""
    if db_status and db_status.get("success"):
        status_html = f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #10B981; box-shadow: 0 0 10px #10B981;"></div>
            <span style="font-size: 13px; font-weight: 600; color: #E2E8F0;">Oracle 23ai Connected ({db_status.get('user', '')}@{db_status.get('dsn', '')})</span>
        </div>
        """
    else:
        status_html = """
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: #EF4444; box-shadow: 0 0 10px #EF4444;"></div>
            <span style="font-size: 13px; font-weight: 600; color: #FCA5A5;">Disconnected</span>
        </div>
        """

    st.markdown(f"""
    <div class="app-header">
        <div>
            <h1 class="app-title">{title}</h1>
            <div class="app-subtitle">{subtitle}</div>
        </div>
        <div>
            {status_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpi_card(col, label: str, value: str, subtext: str = "", delta: Optional[str] = None):
    """Renders a styled KPI metric card in a Streamlit column."""
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtext}</div>
        </div>
        """, unsafe_allow_html=True)

def render_status_badge(status: str) -> str:
    """Returns HTML for a status pill badge."""
    clean_status = str(status).lower().replace(" ", "_")
    return f'<span class="badge badge-{clean_status}">{status}</span>'

def render_sql_box(title: str, concept: str, sql: str):
    """Renders an educational SQL concept explanation box."""
    st.markdown(f"""
    <div class="sql-concept-box">
        <strong>📚 DBMS Concept:</strong> {concept}
    </div>
    """, unsafe_allow_html=True)
    st.code(sql, language="sql")

def format_currency(amount: float) -> str:
    """Formats float as USD currency string."""
    try:
        return f"${float(amount):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def export_dataframe_button(df: pd.DataFrame, filename: str, label: str = "📥 Export Data (CSV)"):
    """Renders a clean CSV download button for any table."""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime='text/csv',
        use_container_width=False
    )
