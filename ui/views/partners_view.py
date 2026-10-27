"""
Business Partners View: Suppliers and Customers Management (Full CRUD).
"""

import streamlit as st
import pandas as pd
from database.dml_manager import DMLManager
from ui.components import export_dataframe_button

def render_partners():
    st.markdown("### 👥 Business Partners: Suppliers & Customers")
    st.caption("Manage procurement vendors, supplier performance ratings, customer accounts, and client tiers.")

    bp_tab1, bp_tab2 = st.tabs(["🏭 Suppliers Management", "🏢 Customers & Accounts"])

    # -------------------------------------------------------------------------
    # TAB 1: SUPPLIERS
    # -------------------------------------------------------------------------
    with bp_tab1:
        s_sub1, s_sub2, s_sub3 = st.tabs(["📋 Suppliers List", "➕ Add Supplier", "✏️ Edit / Delete"])

        with s_sub1:
            suppliers_df = DMLManager.get_suppliers()
            if not suppliers_df.empty:
                st.dataframe(
                    suppliers_df,
                    use_container_width=True,
                    column_config={
                        "SUPPLIER_ID": st.column_config.NumberColumn("ID", width="small"),
                        "SUPPLIER_NAME": st.column_config.TextColumn("Supplier Name", width="large"),
                        "CONTACT_PERSON": st.column_config.TextColumn("Contact"),
                        "EMAIL": st.column_config.TextColumn("Email"),
                        "PHONE": st.column_config.TextColumn("Phone"),
                        "CITY": st.column_config.TextColumn("City"),
                        "RATING": st.column_config.NumberColumn("Rating (⭐)", format="%.1f"),
                        "STATUS": st.column_config.TextColumn("Status"),
                        "PRODUCTS_COUNT": st.column_config.NumberColumn("SKUs Supplied")
                    },
                    hide_index=True
                )
                export_dataframe_button(suppliers_df, "suppliers.csv")
            else:
                st.info("No suppliers found.")

        with s_sub2:
            st.subheader("➕ Register New Supplier")
            with st.form("new_supplier_form", clear_on_submit=True):
                sup_c1, sup_c2 = st.columns(2)
                with sup_c1:
                    sup_name = st.text_input("Supplier / Company Name*", placeholder="e.g. Apex Hardware Supplies")
                    sup_contact = st.text_input("Contact Person Name*", placeholder="e.g. Rachel Miller")
                    sup_email = st.text_input("Email Address*", placeholder="e.g. contact@apexhardware.com")
                    sup_phone = st.text_input("Phone Number*", placeholder="e.g. +1-555-0988")
                with sup_c2:
                    sup_address = st.text_input("Office Address*", placeholder="e.g. 700 Industrial Blvd")
                    sup_city = st.text_input("City*", placeholder="e.g. Austin")
                    sup_rating = st.slider("Quality & Delivery Rating (1.0 - 5.0)", min_value=1.0, max_value=5.0, value=4.5, step=0.1)
                    sup_status = st.selectbox("Status", ["ACTIVE", "INACTIVE"])

                submit_sup = st.form_submit_button("Create Supplier", use_container_width=True, type="primary")
                if submit_sup:
                    if not sup_name.strip() or not sup_email.strip():
                        st.error("Supplier Name and Email are mandatory.")
                    else:
                        try:
                            DMLManager.create_supplier(sup_name, sup_contact, sup_email, sup_phone, sup_address, sup_city, sup_rating, sup_status)
                            st.success(f"✅ Supplier '{sup_name}' added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding supplier: {e}")

        with s_sub3:
            st.subheader("✏️ Modify Supplier Details")
            sups_df = DMLManager.get_suppliers()
            if not sups_df.empty:
                s_map = {f"{r['SUPPLIER_NAME']} ({r['CITY']})": int(r['SUPPLIER_ID']) for _, r in sups_df.iterrows()}
                sel_s_label = st.selectbox("Select Supplier to Edit", list(s_map.keys()))
                sel_s_id = s_map[sel_s_label]
                s_row = sups_df[sups_df["SUPPLIER_ID"] == sel_s_id].iloc[0]

                with st.form("edit_sup_form"):
                    e_s1, e_s2 = st.columns(2)
                    with e_s1:
                        e_name = st.text_input("Supplier Name", value=str(s_row["SUPPLIER_NAME"]))
                        e_contact = st.text_input("Contact Person", value=str(s_row["CONTACT_PERSON"]))
                        e_email = st.text_input("Email", value=str(s_row["EMAIL"]))
                        e_phone = st.text_input("Phone", value=str(s_row["PHONE"]))
                    with e_s2:
                        e_addr = st.text_input("Address", value=str(s_row["ADDRESS"]))
                        e_city = st.text_input("City", value=str(s_row["CITY"]))
                        e_rate = st.slider("Rating", min_value=1.0, max_value=5.0, value=float(s_row["RATING"]), step=0.1)
                        e_stat = st.selectbox("Status", ["ACTIVE", "INACTIVE"], index=0 if s_row["STATUS"] == "ACTIVE" else 1)

                    save_sup = st.form_submit_button("Save Supplier Changes", use_container_width=True)
                    if save_sup:
                        try:
                            DMLManager.update_supplier(sel_s_id, e_name, e_contact, e_email, e_phone, e_addr, e_city, e_rate, e_stat)
                            st.success(f"Supplier ID {sel_s_id} updated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                if st.button("🗑️ Delete Supplier", key="del_sup_btn"):
                    try:
                        DMLManager.delete_supplier(sel_s_id)
                        st.warning(f"Supplier removed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

    # -------------------------------------------------------------------------
    # TAB 2: CUSTOMERS
    # -------------------------------------------------------------------------
    with bp_tab2:
        c_sub1, c_sub2, c_sub3 = st.tabs(["📋 Customers List", "➕ Add Customer", "✏️ Edit / Delete"])

        with c_sub1:
            customers_df = DMLManager.get_customers()
            if not customers_df.empty:
                st.dataframe(
                    customers_df,
                    use_container_width=True,
                    column_config={
                        "CUSTOMER_ID": st.column_config.NumberColumn("ID", width="small"),
                        "CUSTOMER_NAME": st.column_config.TextColumn("Customer Name", width="large"),
                        "EMAIL": st.column_config.TextColumn("Email"),
                        "PHONE": st.column_config.TextColumn("Phone"),
                        "CITY": st.column_config.TextColumn("City"),
                        "CUSTOMER_TYPE": st.column_config.TextColumn("Type"),
                        "TOTAL_ORDERS": st.column_config.NumberColumn("Total Orders"),
                        "TOTAL_SPEND": st.column_config.NumberColumn("Lifetime Spend", format="$%.2f")
                    },
                    hide_index=True
                )
                export_dataframe_button(customers_df, "customers.csv")
            else:
                st.info("No customers found.")

        with c_sub2:
            st.subheader("➕ Register New Customer")
            with st.form("new_cust_form", clear_on_submit=True):
                c_c1, c_c2 = st.columns(2)
                with c_c1:
                    cust_name = st.text_input("Customer Name / Business*", placeholder="e.g. Velocity Dynamics LLC")
                    cust_email = st.text_input("Email*", placeholder="e.g. finance@velocitydyn.com")
                    cust_phone = st.text_input("Phone Number*", placeholder="e.g. +1-555-4422")
                with c_c2:
                    cust_addr = st.text_input("Address*", placeholder="e.g. 400 Tech Hub Blvd")
                    cust_city = st.text_input("City*", placeholder="e.g. Seattle")
                    cust_type = st.selectbox("Customer Classification", ["RETAIL", "WHOLESALE", "CORPORATE"])

                submit_cust = st.form_submit_button("Register Customer", use_container_width=True, type="primary")
                if submit_cust:
                    if not cust_name.strip() or not cust_email.strip():
                        st.error("Name and Email are required.")
                    else:
                        try:
                            DMLManager.create_customer(cust_name, cust_email, cust_phone, cust_addr, cust_city, cust_type)
                            st.success(f"✅ Customer '{cust_name}' registered successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        with c_sub3:
            st.subheader("✏️ Edit Customer")
            custs_df = DMLManager.get_customers()
            if not custs_df.empty:
                c_map = {f"{r['CUSTOMER_NAME']} ({r['CUSTOMER_TYPE']})": int(r['CUSTOMER_ID']) for _, r in custs_df.iterrows()}
                sel_c_label = st.selectbox("Select Customer to Edit", list(c_map.keys()))
                sel_c_id = c_map[sel_c_label]
                c_row = custs_df[custs_df["CUSTOMER_ID"] == sel_c_id].iloc[0]

                with st.form("edit_cust_form"):
                    ec_1, ec_2 = st.columns(2)
                    with ec_1:
                        ec_name = st.text_input("Name", value=str(c_row["CUSTOMER_NAME"]))
                        ec_email = st.text_input("Email", value=str(c_row["EMAIL"]))
                        ec_phone = st.text_input("Phone", value=str(c_row["PHONE"]))
                    with ec_2:
                        ec_addr = st.text_input("Address", value=str(c_row["ADDRESS"]) if "ADDRESS" in c_row else "")
                        ec_city = st.text_input("City", value=str(c_row["CITY"]))
                        types = ["RETAIL", "WHOLESALE", "CORPORATE"]
                        t_idx = types.index(str(c_row["CUSTOMER_TYPE"])) if str(c_row["CUSTOMER_TYPE"]) in types else 0
                        ec_type = st.selectbox("Type", types, index=t_idx)

                    save_cust = st.form_submit_button("Save Customer Changes", use_container_width=True)
                    if save_cust:
                        try:
                            DMLManager.update_customer(sel_c_id, ec_name, ec_email, ec_phone, ec_addr, ec_city, ec_type)
                            st.success(f"Customer updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                if st.button("🗑️ Delete Customer", key="del_cust_btn"):
                    try:
                        DMLManager.delete_customer(sel_c_id)
                        st.warning("Customer deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
