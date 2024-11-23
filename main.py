import streamlit as st
from sign_in import sign_in
from customer_page import (
    customer_order_process,
    order_history_page,
    success_page,
    cancel_page,
    order_notifications_page,  # Import the notifications page
)
from admin_dashboard import admin_dashboard_page, admin_coupon_page, manage_inventory

# Set page configuration
st.set_page_config(
    page_title="Koopi .Co",
    page_icon="☕",
    layout="centered",         
    initial_sidebar_state="auto"  
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None

if not st.session_state["logged_in"]:
    sign_in()
else:
    if st.session_state["role"] == "Customer":
        # Add Notifications to the menu
        page = st.sidebar.selectbox(
            "Menu", ["Order Process", "Order History", "Notifications"]
        )

        if page == "Order Process":
            customer_order_process()
        elif page == "Order History":
            order_history_page()
        elif page == "Notifications":
            order_notifications_page(st.session_state.get("username", "Customer"))  # Pass the customer name
        elif 'success' in st.experimental_get_query_params():
            success_page()
        elif 'cancel' in st.experimental_get_query_params():
            cancel_page()

    elif st.session_state["role"] == "Admin":
        page = st.sidebar.selectbox(
            "Choose a feature:", ["Dashboard", "Create Coupons", "Manage Inventory"]
        )

        if page == "Dashboard":
            admin_dashboard_page()
        elif page == "Create Coupons":
            admin_coupon_page()
        elif page == "Manage Inventory":
            manage_inventory()

    # Move the Log Out button to the sidebar
    if st.sidebar.button("Log Out"):
        st.session_state["logged_in"] = False
        st.session_state["role"] = None
        st.experimental_rerun()
