"""
Custom CSS styling and design system for the Streamlit UI.
Creates a modern, premium, high-contrast dashboard aesthetic.
"""

def get_custom_css() -> str:
    return """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Root styling and typography */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        code, pre, .stCodeBlock {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Top Header Styling */
        .app-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 24px;
            color: #FFFFFF;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .app-title {
            font-size: 26px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0;
            background: linear-gradient(90deg, #60A5FA, #A78BFA, #38BDF8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .app-subtitle {
            font-size: 13px;
            color: #94A3B8;
            margin-top: 4px;
            font-weight: 500;
        }

        /* Metric Cards */
        .kpi-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.2s ease-in-out;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(96, 165, 250, 0.4);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.2);
        }

        .kpi-label {
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94A3B8;
            margin-bottom: 6px;
        }

        .kpi-value {
            font-size: 26px;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.5px;
        }

        .kpi-sub {
            font-size: 12px;
            color: #64748B;
            margin-top: 4px;
        }

        /* Status Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }

        .badge-healthy, .badge-in_stock, .badge-active, .badge-completed {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .badge-low_stock, .badge-pending, .badge-processing {
            background-color: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .badge-out_of_stock, .badge-cancelled, .badge-inactive {
            background-color: rgba(239, 68, 68, 0.15);
            color: #EF4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .badge-db-connected {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34D399;
            border: 1px solid #059669;
            padding: 6px 14px;
            font-size: 12px;
            border-radius: 20px;
            font-weight: 600;
        }

        /* Card Container */
        .content-card {
            background: #1E293B;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 20px;
        }

        /* Custom Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            font-weight: 600;
            border-radius: 8px 8px 0 0;
        }

        /* SQL Result Banner */
        .sql-concept-box {
            background: linear-gradient(90deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.8));
            border-left: 4px solid #3B82F6;
            padding: 12px 18px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 16px;
            font-size: 13px;
            color: #CBD5E1;
        }

        /* Subtle scrollbars */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(148, 163, 184, 0.3);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(148, 163, 184, 0.5);
        }
    </style>
    """
