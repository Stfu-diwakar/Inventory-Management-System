"""
Reusable UI components and widgets for the Inventory Management System.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

def render_header(title: str, subtitle: str, db_status: Optional[Dict[str, Any]] = None):
    """Renders the top navigation and status header."""
    if db_status and db_status.get("success"):
        badge_dot = "#10B981"
        badge_text_color = "#E2E8F0"
        status_text = f"Oracle 23ai Connected ({db_status.get('user', '')}@{db_status.get('dsn', '')})"
    else:
        badge_dot = "#EF4444"
        badge_text_color = "#FCA5A5"
        status_text = "Disconnected"

    header_html = (
        '<div class="app-header">'
        '<div class="app-header-left">'
        f'<h1 class="app-title">{title}</h1>'
        f'<div class="app-subtitle">{subtitle}</div>'
        '</div>'
        '<div class="app-header-right">'
        '<div class="db-status-pill">'
        f'<span class="db-status-dot" style="background-color: {badge_dot}; box-shadow: 0 0 10px {badge_dot};"></span>'
        f'<span class="db-status-text" style="color: {badge_text_color};">{status_text}</span>'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

def render_kpi_card(col, label: str, value: str, subtext: str = "", delta: Optional[str] = None):
    """Renders a styled KPI metric card in a Streamlit column."""
    with col:
        card_html = (
            '<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{subtext}</div>'
            '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

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
