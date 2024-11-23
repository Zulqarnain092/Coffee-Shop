import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
import random

class Database:
    def __init__(self):
        self.menu = pd.DataFrame({
            'item': ['Americano', 'Cappuccino', 'Latte', 'Caramel Macchiato'],
            'price': [7.90, 8.50, 9.00, 10.00]
        })
        self.orders_file = "orders.json"
        self.orders = self.load_orders()
        self.feedback_file = "feedback.json"
        self.feedback = self.load_feedback()
        self.coupons_file = "coupons.json"
        self.coupons = self.load_coupons()
        self.inventory_file = "inventory.json"
        self.inventory = self.load_inventory()

    def load_orders(self):
        if os.path.exists(self.orders_file):
            try:
                with open(self.orders_file, 'r') as file:
                    orders = json.load(file)
                    validated_orders = []
                    for order in orders:
                        # Ensure all required keys are in the order
                        if all(key in order for key in ['order_id', 'item', 'quantity', 'total_price', 'status', 'date']):
                            validated_orders.append(order)
                        else:
                            print(f"Invalid order detected: {order}")
                    return validated_orders
            except json.JSONDecodeError:
                st.error("Error loading orders file.")
                return []
        return []

    def load_feedback(self):
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def load_coupons(self):
        if os.path.exists(self.coupons_file):
            try:
                with open(self.coupons_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def load_inventory(self):
        if os.path.exists(self.inventory_file):
            try:
                with open(self.inventory_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                st.error("Error loading inventory file.")
                return {}
        # Initialize with default inventory if file doesn't exist
        return {
            'Americano': 50,
            'Cappuccino': 50,
            'Latte': 50,
            'Caramel Macchiato': 50
        }

    def save_inventory(self):
        """Save inventory to the JSON file."""
        with open(self.inventory_file, 'w') as file:
            json.dump(self.inventory, file, indent=4)

    def save_orders(self):
        """Save orders to the JSON file."""
        with open(self.orders_file, 'w') as file:
            json.dump(self.orders, file, indent=4)

    def save_feedback(self):
        """Save feedback to the JSON file."""
        with open(self.feedback_file, 'w') as file:
            json.dump(self.feedback, file, indent=4)

    def save_coupons(self):
        """Save coupons to the JSON file."""
        with open(self.coupons_file, 'w') as file:
            json.dump(self.coupons, file, indent=4)

    def add_order(self, order_data):
        """Add a new order and save it to the list."""
        self.orders.append(order_data)
        self.save_orders()

    def update_order_status(self, order_id, status):
        """Update the status of an existing order."""
        for order in self.orders:
            if order['order_id'] == order_id:
                order['status'] = status
                self.save_orders()

    def generate_order_id(self):
        """Generate a unique order ID."""
        return random.randint(1000, 9999)  # This could be replaced with a more sophisticated ID generator.

# Mock database
users = {
    "admin": {"password": "admin123", "role": "Admin"},
    "cust": {"password": "cust123", "role": "Customer"}
}

def authenticate_user(username, password, role):
    """Authenticate a user based on username, password, and role."""
    if username in users:
        if users[username]["password"] == password and users[username]["role"] == role:
            return True
    return False

def register_user(username, password, role):
    """Register a new user if the username does not already exist."""
    if username in users:
        return False  # Username already exists
    users[username] = {"password": password, "role": role}
    return True


db = Database()
