import streamlit as st
from shared import authenticate_user, register_user

def sign_in():
    st.title("Welcome to Koopi .Co")

    # Tabs for Login and Register
    option = st.radio("Choose an option", ["Sign In", "Register"])

    if option == "Sign In":
        st.subheader("Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Customer", "Admin"])

        if st.button("Sign In"):
            if authenticate_user(username, password, role):
                st.success(f"Welcome back, {username}!")
                st.session_state["logged_in"] = True
                st.session_state["role"] = role
                st.session_state["username"] = username
            else:
                st.error("Invalid credentials. Please try again.")

    elif option == "Register":
        st.subheader("Register")
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        role = st.selectbox("Role", ["Customer", "Admin"])

        if st.button("Register"):
            if register_user(username, password, role):
                st.success("Registration successful! You can now sign in.")
            else:
                st.error("Username already exists. Please choose another one.")
