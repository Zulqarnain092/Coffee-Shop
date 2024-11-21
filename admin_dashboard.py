import pandas as pd
import streamlit as st
from shared import db  # Assumes shared.py contains the database logic

def admin_dashboard_page():
    st.title("Admin Dashboard")

    # Ensure we have orders data
    if not db.orders:
        st.warning("No orders found in the database.")
        return

    # Convert orders to DataFrame for easier analysis
    orders_data = pd.DataFrame(db.orders)

    # Display the order data with the 'date' column
    st.dataframe(orders_data[['order_id', 'customer', 'item', 'quantity', 'total_price', 'status', 'date']])

    # Check for required fields
    required_fields = ['item', 'quantity', 'total_price', 'date']
    missing_fields = [field for field in required_fields if field not in orders_data.columns]
    if missing_fields:
        st.error(f"Orders data is missing required fields: {', '.join(missing_fields)}.")
        return

    # Ensure date column is properly formatted
    try:
        orders_data['date'] = pd.to_datetime(orders_data['date']).dt.normalize()
    except Exception as e:
        st.error(f"Error parsing 'date' field: {e}")
        return

    # Check if orders_data is empty after loading
    if orders_data.empty:
        st.warning("No orders to display.")
        return

    # Mock inventory costs for profit calculation (adjust as needed)
    inventory_costs = {
        'Americano': 1.0,
        'Cappuccino': 1.2,
        'Latte': 1.5,
        'Caramel Macchiato': 2.0
    }

    # Add 'cost' and 'profit' columns
    orders_data['cost'] = orders_data['item'].map(inventory_costs).fillna(0)  # Default cost to 0 if not found
    orders_data['profit'] = orders_data['total_price'] - (orders_data['quantity'] * orders_data['cost'])

    # Normalize the current date for accurate comparison
    today = pd.Timestamp.today().normalize()

    # Calculate Daily, Weekly, and Monthly Totals after 'profit' is added
    daily_data = orders_data[orders_data['date'] == today]
    weekly_data = orders_data[orders_data['date'] >= (today - pd.Timedelta(weeks=1))]
    monthly_data = orders_data[orders_data['date'] >= (today - pd.Timedelta(days=30))]

    # Display Total Sales Report
    st.subheader("Total Sales Report")

    # Create columns for side-by-side layout
    col1, col2, col3 = st.columns(3)

    # Function to create a styled card-like box with fixed dimensions
    def create_card(label, revenue, quantity, profit):
        return f"""
        <div style="padding: 20px; background-color: #f1f1f1; border-radius: 10px; 
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin: 10px; 
                    height: 250px; display: flex; flex-direction: column; justify-content: space-between;">
            <h3 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">{label} Sales</h3>
            <p style="font-size: 16px;"><strong>Revenue:</strong> ${revenue:,.2f}</p>
            <p style="font-size: 16px;"><strong>Quantity Sold:</strong> {quantity}</p>
            <p style="font-size: 16px;"><strong>Profit:</strong> ${profit:,.2f}</p>
        </div>
        """

    # Display Daily, Weekly, Monthly Sales in the columns
    with col1:
        if 'profit' in daily_data.columns:
            total_revenue = daily_data['total_price'].sum()
            total_quantity = daily_data['quantity'].sum()
            total_profit = daily_data['profit'].sum()
            st.markdown(create_card("Daily", total_revenue, total_quantity, total_profit), unsafe_allow_html=True)
        else:
            st.error("The 'profit' column is missing in the daily data.")

    with col2:
        if 'profit' in weekly_data.columns:
            total_revenue = weekly_data['total_price'].sum()
            total_quantity = weekly_data['quantity'].sum()
            total_profit = weekly_data['profit'].sum()
            st.markdown(create_card("Weekly", total_revenue, total_quantity, total_profit), unsafe_allow_html=True)
        else:
            st.error("The 'profit' column is missing in the weekly data.")

    with col3:
        if 'profit' in monthly_data.columns:
            total_revenue = monthly_data['total_price'].sum()
            total_quantity = monthly_data['quantity'].sum()
            total_profit = monthly_data['profit'].sum()
            st.markdown(create_card("Monthly", total_revenue, total_quantity, total_profit), unsafe_allow_html=True)
        else:
            st.error("The 'profit' column is missing in the monthly data.")

    # Sales Breakdown by Coffee Type
    st.subheader("Sales Breakdown by Coffee Type")
    breakdown = orders_data.groupby('item').agg(
        total_sold=('quantity', 'sum'),
        total_revenue=('total_price', 'sum'),
        total_profit=('profit', 'sum')
    ).reset_index()

    if breakdown.empty:
        st.info("No sales data available for breakdown.")
    else:
        # Display separate bar charts for each category
        st.subheader("Total Sold by Coffee Type")
        st.bar_chart(breakdown.set_index('item')['total_sold'])
        
        st.subheader("Total Revenue by Coffee Type")
        st.bar_chart(breakdown.set_index('item')['total_revenue'])
        
        st.subheader("Total Profit by Coffee Type")
        st.bar_chart(breakdown.set_index('item')['total_profit'])
        
        # Display table for sales breakdown after the graphs
        st.dataframe(breakdown)

    # Best and Worst Sellers
    st.subheader("Best and Worst Sellers")
    if not breakdown.empty:
        best_seller = breakdown.loc[breakdown['total_sold'].idxmax()]
        worst_seller = breakdown.loc[breakdown['total_sold'].idxmin()]
        st.write(f"**Best Seller**: {best_seller['item']} ({best_seller['total_sold']} units sold)")
        st.write(f"**Worst Seller**: {worst_seller['item']} ({worst_seller['total_sold']} units sold)")
    else:
        st.info("No sales data available to identify best or worst sellers.")

# Coupon Management
def admin_coupon_page():
    st.title("Create Coupons")
    coupon_code = st.text_input("Enter coupon code:")
    discount = st.number_input("Enter discount percentage:", min_value=1, max_value=100)

    if st.button("Create Coupon"):
        coupon_data = {
            'coupon_code': coupon_code,
            'discount': discount
        }
        db.coupons[coupon_code] = coupon_data
        db.save_coupons()
        st.success(f"Coupon {coupon_code} created with {discount}% discount.")

# Inventory Management
def manage_inventory():
    st.title("Inventory Management")
    for item, stock in db.inventory.items():
        st.write(f"{item}: {stock} units")
        additional_stock = st.number_input(f"Add stock for {item}:", min_value=0, key=f"stock_{item}")
        if st.button(f"Update {item} stock", key=f"button_{item}"):
            db.inventory[item] += additional_stock
            db.save_inventory()  # Save the updated inventory
            st.success(f"Stock updated for {item}. New stock: {db.inventory[item]} units")

# Sidebar for Navigation
st.sidebar.title("Admin Panel")
page = st.sidebar.selectbox("Choose a feature:", ["Dashboard", "Create Coupons", "Manage Inventory"])

if page == "Dashboard":
    admin_dashboard_page()
elif page == "Create Coupons":
    admin_coupon_page()
elif page == "Manage Inventory":
    manage_inventory()
