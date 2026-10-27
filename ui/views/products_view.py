"""
Products & Categories View: Full CRUD Operations, Catalog Search & Filtering.
"""

import streamlit as st
import pandas as pd
from database.dml_manager import DMLManager
from ui.components import format_currency, export_dataframe_button

def render_products():
    st.markdown("### 📦 Product Catalog & Category Management")
    st.caption("Perform complete CRUD (Create, Read, Update, Delete) operations on product catalog and categories.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Product Catalog", 
        "➕ Add New Product", 
        "✏️ Edit / Delete Product", 
        "🏷️ Manage Categories"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: PRODUCT CATALOG & FILTERING
    # -------------------------------------------------------------------------
    with tab1:
        # Filter controls
        f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.5, 1.5, 1.5])
        with f_col1:
            search_term = st.text_input("🔍 Search SKU or Product Name", placeholder="e.g. ThinkStation, Keyboard, SKU-...")
        with f_col2:
            cats_df = DMLManager.get_categories()
            cat_options = {"All Categories": None}
            if not cats_df.empty:
                for _, r in cats_df.iterrows():
                    cat_options[r["CATEGORY_NAME"]] = int(r["CATEGORY_ID"])
            selected_cat_name = st.selectbox("Category", list(cat_options.keys()))
            selected_cat_id = cat_options[selected_cat_name]
        with f_col3:
            sups_df = DMLManager.get_suppliers()
            sup_options = {"All Suppliers": None}
            if not sups_df.empty:
                for _, r in sups_df.iterrows():
                    sup_options[r["SUPPLIER_NAME"]] = int(r["SUPPLIER_ID"])
            selected_sup_name = st.selectbox("Supplier", list(sup_options.keys()))
            selected_sup_id = sup_options[selected_sup_name]
        with f_col4:
            stock_filter = st.selectbox("Stock Status", ["All Statuses", "IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"])

        # Fetch products
        products_df = DMLManager.get_products(
            category_id=selected_cat_id,
            supplier_id=selected_sup_id,
            search_term=search_term if search_term else None
        )

        if stock_filter != "All Statuses" and not products_df.empty:
            products_df = products_df[products_df["STOCK_STATUS"] == stock_filter]

        st.markdown(f"**Found {len(products_df)} products** matching your criteria.")

        if not products_df.empty:
            st.dataframe(
                products_df,
                use_container_width=True,
                column_config={
                    "PRODUCT_ID": st.column_config.NumberColumn("ID", width="small"),
                    "SKU": st.column_config.TextColumn("SKU Code", width="small"),
                    "PRODUCT_NAME": st.column_config.TextColumn("Product Name", width="large"),
                    "CATEGORY_NAME": st.column_config.TextColumn("Category"),
                    "SUPPLIER_NAME": st.column_config.TextColumn("Supplier"),
                    "COST_PRICE": st.column_config.NumberColumn("Cost", format="$%.2f"),
                    "UNIT_PRICE": st.column_config.NumberColumn("Retail", format="$%.2f"),
                    "PROFIT_MARGIN": st.column_config.NumberColumn("Margin ($)", format="$%.2f"),
                    "MARGIN_PCT": st.column_config.NumberColumn("Margin (%)", format="%.1f%%"),
                    "TOTAL_STOCK": st.column_config.NumberColumn("Total Stock"),
                    "STOCK_STATUS": st.column_config.TextColumn("Status"),
                    "DATE_ADDED": st.column_config.TextColumn("Added")
                },
                hide_index=True
            )
            export_dataframe_button(products_df, "product_catalog.csv")
        else:
            st.info("No products match the selected filters.")

    # -------------------------------------------------------------------------
    # TAB 2: ADD NEW PRODUCT (CREATE)
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("➕ Create a New Product (INSERT)")
        st.caption("Inserts a new product into the Oracle PRODUCTS table with integrity checks.")

        cats_df = DMLManager.get_categories()
        sups_df = DMLManager.get_suppliers()

        if cats_df.empty or sups_df.empty:
            st.warning("Please ensure at least one Category and Supplier exist before adding a product.")
        else:
            with st.form("add_product_form", clear_on_submit=True):
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    new_sku = st.text_input("Product SKU (Unique identifier)*", placeholder="e.g. SKU-ACC-101")
                    new_name = st.text_input("Product Name*", placeholder="e.g. USB-C 10-in-1 Aluminum Hub")
                    cat_map = {r["CATEGORY_NAME"]: int(r["CATEGORY_ID"]) for _, r in cats_df.iterrows()}
                    new_cat = st.selectbox("Category*", list(cat_map.keys()))
                    sup_map = {r["SUPPLIER_NAME"]: int(r["SUPPLIER_ID"]) for _, r in sups_df.iterrows()}
                    new_sup = st.selectbox("Supplier*", list(sup_map.keys()))
                with p_col2:
                    new_cost = st.number_input("Cost Price ($)*", min_value=0.0, value=50.0, step=1.0)
                    new_price = st.number_input("Retail Unit Price ($)*", min_value=0.0, value=89.99, step=1.0)
                    new_reorder = st.number_input("Reorder Level Threshold*", min_value=1, value=15, step=1)
                    new_uom = st.selectbox("Unit of Measure", ["PCS", "BOX", "SET", "KG", "MTR"])

                submitted = st.form_submit_button("🚀 Insert Product into Database", use_container_width=True)
                if submitted:
                    if not new_sku.strip() or not new_name.strip():
                        st.error("SKU and Product Name are required fields.")
                    elif new_price < new_cost:
                        st.error("Validation Error: Unit price cannot be less than cost price (chk_price_gte_cost).")
                    else:
                        try:
                            rowcount = DMLManager.create_product(
                                sku=new_sku,
                                name=new_name,
                                category_id=cat_map[new_cat],
                                supplier_id=sup_map[new_sup],
                                cost_price=new_cost,
                                unit_price=new_price,
                                reorder_level=new_reorder,
                                unit_of_measure=new_uom
                            )
                            st.success(f"✅ Product '{new_name}' (SKU: {new_sku.upper()}) added successfully! ({rowcount} row inserted)")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Oracle Database Error: {e}")

    # -------------------------------------------------------------------------
    # TAB 3: EDIT / DELETE PRODUCT (UPDATE & DELETE)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("✏️ Update or Delete Existing Product")
        all_prods = DMLManager.get_products()
        if all_prods.empty:
            st.info("No products available to edit.")
        else:
            prod_options = {f"{r['SKU']} - {r['PRODUCT_NAME']}": int(r["PRODUCT_ID"]) for _, r in all_prods.iterrows()}
            selected_prod_label = st.selectbox("Select Product to Modify", list(prod_options.keys()))
            selected_prod_id = prod_options[selected_prod_label]

            prod_row = all_prods[all_prods["PRODUCT_ID"] == selected_prod_id].iloc[0]

            edit_col1, edit_col2 = st.columns(2)
            with edit_col1:
                edit_sku = st.text_input("SKU", value=str(prod_row["SKU"]))
                edit_name = st.text_input("Product Name", value=str(prod_row["PRODUCT_NAME"]))
                cats_df = DMLManager.get_categories()
                cat_map = {r["CATEGORY_NAME"]: int(r["CATEGORY_ID"]) for _, r in cats_df.iterrows()}
                cat_default_idx = list(cat_map.values()).index(int(prod_row["CATEGORY_ID"])) if int(prod_row["CATEGORY_ID"]) in cat_map.values() else 0
                edit_cat = st.selectbox("Category", list(cat_map.keys()), index=cat_default_idx)

                sups_df = DMLManager.get_suppliers()
                sup_map = {r["SUPPLIER_NAME"]: int(r["SUPPLIER_ID"]) for _, r in sups_df.iterrows()}
                sup_default_idx = list(sup_map.values()).index(int(prod_row["SUPPLIER_ID"])) if int(prod_row["SUPPLIER_ID"]) in sup_map.values() else 0
                edit_sup = st.selectbox("Supplier", list(sup_map.keys()), index=sup_default_idx)

            with edit_col2:
                edit_cost = st.number_input("Cost Price ($)", min_value=0.0, value=float(prod_row["COST_PRICE"]), step=1.0)
                edit_price = st.number_input("Retail Price ($)", min_value=0.0, value=float(prod_row["UNIT_PRICE"]), step=1.0)
                edit_reorder = st.number_input("Reorder Level", min_value=0, value=int(prod_row["REORDER_LEVEL"]), step=1)
                uom_options = ["PCS", "BOX", "SET", "KG", "MTR"]
                uom_idx = uom_options.index(str(prod_row["UNIT_OF_MEASURE"])) if str(prod_row["UNIT_OF_MEASURE"]) in uom_options else 0
                edit_uom = st.selectbox("Unit of Measure", uom_options, index=uom_idx)

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("💾 Save Changes (UPDATE)", use_container_width=True, type="primary"):
                    try:
                        DMLManager.update_product(
                            product_id=selected_prod_id,
                            sku=edit_sku,
                            name=edit_name,
                            category_id=cat_map[edit_cat],
                            supplier_id=sup_map[edit_sup],
                            cost_price=edit_cost,
                            unit_price=edit_price,
                            reorder_level=edit_reorder,
                            unit_of_measure=edit_uom
                        )
                        st.success(f"✅ Product ID {selected_prod_id} updated successfully! (Audit trigger fired)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")

            with btn_col2:
                if st.button("🗑️ Delete Product (DELETE)", use_container_width=True):
                    try:
                        DMLManager.delete_product(selected_prod_id)
                        st.warning(f"⚠️ Product ID {selected_prod_id} was deleted. (Cascade inventory removed, audit log recorded)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")

    # -------------------------------------------------------------------------
    # TAB 4: CATEGORIES MANAGEMENT
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("🏷️ Category CRUD Operations")
        c_grid1, c_grid2 = st.columns([1.5, 1])

        with c_grid1:
            st.markdown("##### Existing Categories")
            categories_df = DMLManager.get_categories()
            if not categories_df.empty:
                st.dataframe(
                    categories_df,
                    use_container_width=True,
                    column_config={
                        "CATEGORY_ID": st.column_config.NumberColumn("ID", width="small"),
                        "CATEGORY_NAME": st.column_config.TextColumn("Category Name", width="medium"),
                        "DESCRIPTION": st.column_config.TextColumn("Description"),
                        "PRODUCT_COUNT": st.column_config.NumberColumn("Products"),
                        "CREATED_DATE": st.column_config.TextColumn("Created")
                    },
                    hide_index=True
                )
            else:
                st.info("No categories exist.")

        with c_grid2:
            st.markdown("##### ➕ Add Category")
            with st.form("new_cat_form", clear_on_submit=True):
                cat_name_input = st.text_input("Category Name*", placeholder="e.g. Smart Home & IoT")
                cat_desc_input = st.text_area("Description", placeholder="Devices and sensors for home automation")
                cat_submit = st.form_submit_button("Add Category", use_container_width=True)
                if cat_submit:
                    if not cat_name_input.strip():
                        st.error("Category Name cannot be empty.")
                    else:
                        try:
                            DMLManager.create_category(cat_name_input, cat_desc_input)
                            st.success(f"✅ Category '{cat_name_input}' created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            st.markdown("##### 🗑️ Remove Category")
            if not categories_df.empty:
                cat_del_options = {r["CATEGORY_NAME"]: int(r["CATEGORY_ID"]) for _, r in categories_df.iterrows()}
                cat_del_name = st.selectbox("Select Category to Delete", list(cat_del_options.keys()))
                if st.button("Delete Category", use_container_width=True):
                    try:
                        DMLManager.delete_category(cat_del_options[cat_del_name])
                        st.warning(f"Category '{cat_del_name}' deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting category: {e}")
