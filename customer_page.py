import streamlit as st
import stripe
import pandas as pd
import random
import json
from admin_dashboard import admin_dashboard_page
from shared import db
from datetime import datetime
from PIL import Image

# Access the Stripe secret key from Streamlit's secrets
stripe.api_key = st.secrets["stripe"]["STRIPE_SECRET_KEY"]

# Check if the Stripe API key is available
if not stripe.api_key:
    st.error("Stripe secret key is not set. Please check your Streamlit secrets.")

# Stripe payment session creation
def create_checkout_session(customer_name, total_price, order_id, coupon_code=None):
    try:
        # Check if coupon is valid
        discount = 0
        if coupon_code:
            coupon = db.coupons.get(coupon_code)
            if coupon:
                discount = coupon.get('discount', 0)
                total_price *= (1 - discount / 100)
        
        total_price_cents = int(total_price * 100)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'myr',  # Change if necessary
                    'product_data': {
                        'name': f"Coffee Order for {customer_name}"
                    },
                    'unit_amount': total_price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'https://koopi-co.streamlit.app/?success=true&order_id={order_id}',
            cancel_url=f'https://koopi-co.streamlit.app/?cancel=true',
        )
        
        return session.url  # Ensure this returns the URL to proceed to payment
    
    except Exception as e:
        st.error(f"Error creating payment session: {e}")
        return None



def customer_order_process():
    st.title("Coffee Shop - Customer Order")
    st.subheader("Menu")
    
    # Add images for menu items
    menu_images = {
        'Americano': 'https://dolo.com.au/cdn/shop/articles/522979505-shutterstock_1973536478.jpg?v=1690528484',
        'Cappuccino': 'https://www.thespruceeats.com/thmb/oUxhx54zsjVWfPlrgedJU0MZ-y0=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/how-to-make-cappuccinos-766116-hero-01-a754d567739b4ee0b209305138ecb996.jpg',
        'Latte': 'https://images.arla.com/recordid/F2DA5762-13BB-4FF4-88839FDE14DE1993/chocolate-latte.jpg?width=1200&height=630&mode=crop&format=jpg',
        'Caramel Macchiato': 'https://img.freepik.com/premium-photo/closeup-delicious-whipped-creamtopped-coffee-glass-with-coffee-beans-warm-bokeh-lights-background_1298779-1307.jpg'
    }
    
    col1, col2 = st.columns(2)
    
    for index, row in db.menu.iterrows():
        item = row['item']
        price = row['price']
        image_path = menu_images.get(item, None)
        
        with col1 if index % 2 == 0 else col2:
            if image_path:
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <img src="{image_path}" alt="{item}" width="300" height="200">
                        <p><strong>{item}</strong> - RM{price:.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write(f"**{item}** - RM{price:.2f}")
    
    if "username" in st.session_state:
        customer_name = st.session_state["username"]
    else:
        st.error("You need to sign in first.")
        return
    
    selected_item = st.selectbox("Choose your coffee:", db.menu['item'])
    quantity = st.number_input("Enter quantity:", min_value=1, step=1)
    coupon_code = st.text_input("Enter coupon code (if any):")

    
    if customer_name and selected_item:
        price = db.menu[db.menu['item'] == selected_item]['price'].values[0]
        total_price = price * quantity
        
        st.write(f"**Total Price: RM{total_price:.2f}**")
        
        if st.button("Proceed to Payment"):
            # Generate an order ID
            order_id = random.randint(1000, 9999)
            # Add current date and time
            order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            order_data = {
                'order_id': order_id,
                'customer': customer_name,
                'item': selected_item,
                'quantity': quantity,
                'total_price': total_price,
                'status': 'Pending',
                'date': order_date
            }
            
            # Add order to the orders list and save to JSON
            db.orders.append(order_data)
            db.save_orders()  # Save the order to the JSON file
            
            # Create a Stripe Checkout session and get the payment URL
            payment_url = create_checkout_session(customer_name, total_price, order_id, coupon_code)
            
            if payment_url:
                st.markdown(f"[Click here to complete your payment]({payment_url})")
            else:
                st.error("Failed to create payment session.")



def order_notifications_page(customer_name):
    st.title("Order Notifications")
    
    db.load_orders()
    customer_orders = [order for order in db.orders if order['customer'] == customer_name]
    
    # Debugging step
    st.write(f"Customer orders: {len(customer_orders)}")

    if not customer_orders:
        st.write("No orders found.")
        return

    ready_orders = [order for order in customer_orders if order['status'] == 'Ready' and not order['notification_sent']]
    
    # Debugging step
    st.write(f"Ready orders: {len(ready_orders)}")

    if ready_orders:
        for order in ready_orders:
            st.success(f"Your order #{order['order_id']} is Ready! 🎉")
            order['notification_sent'] = True
        db.save_orders()
    else:
        st.write("No notifications at the moment.")





# Success page
def success_page():
    st.title("Payment Successful")
    query_params = st.experimental_get_query_params()
    order_id = query_params.get("order_id", [None])[0]

    if order_id:
        order_id = int(order_id)
        
        # Find and update the order status
        for order in db.orders:
            if order['order_id'] == order_id:
                order['status'] = 'Paid'
                
        # Save updated orders to JSON
        db.save_orders()

        # Display the order data as a DataFrame
        order_data = pd.DataFrame([order for order in db.orders if order['order_id'] == order_id])
        st.write(f"Order ID: {order_id}")
        st.dataframe(order_data)

        # Feedback mechanism
        feedback_rating = st.slider("Rate the coffee (1 to 5):", 1, 5)
        feedback_service = st.slider("Rate the service (1 to 5):", 1, 5)
        
        if st.button("Submit Feedback"):
            feedback_data = {
                'order_id': order_id,
                'rating': feedback_rating,
                'service': feedback_service
            }
            db.feedback.append(feedback_data)
            db.save_feedback()
            st.success("Thank you for your feedback!")


# Cancel page
def cancel_page():
    st.title("Payment Cancelled")
    st.write("Your payment was not completed. Please try again.")


# Order history page
def order_history_page():
    st.title("Order History")
    
    db.load_orders()  # Load the orders from the saved JSON

    if not db.orders:
        st.write("You have no past orders.")
        return
    
    # Convert order data to DataFrame for display
    order_data = pd.DataFrame(db.orders)

    # Get the current logged-in username
    username = st.session_state.get("username", None)
    
    if username:
        # Filter orders by username
        order_data = order_data[order_data["customer"] == username]
    else:
        st.error("No username found in session. Please log in again.")
        return

    # Check if there are orders for the user
    if order_data.empty:
        st.write("You have no past orders.")
        return

    # Exclude the 'customer' column
    if 'customer' in order_data.columns:
        order_data = order_data.drop(columns=['customer'])
    
    # Display the filtered order history
    st.dataframe(order_data)



# Sidebar for navigation
def sidebar_navigation():
    st.sidebar.title("Navigation")
    pages = {
        "Order Process": "order_process",
        "Order History": "order_history",
        "Admin Dashboard": "admin_dashboard"
    }
    selection = st.sidebar.radio("Go to", list(pages.keys()))
    return pages[selection]


# App routing
def main():
    # Get the selected page from the sidebar
    page = sidebar_navigation()

    if page == "order_history":
        order_history_page()
    elif page == "admin_dashboard":
        admin_dashboard_page()  # Call the admin dashboard function
    elif 'success' in st.experimental_get_query_params():
        success_page()
    elif 'cancel' in st.experimental_get_query_params():
        cancel_page()
    else:
        customer_order_process()


# Run the app
if __name__ == "__main__":
    main()
