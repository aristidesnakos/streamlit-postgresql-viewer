import streamlit as st
from home_page import home_page
from chat_messages_page import chat_messages_page

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Chat Messages"])

if page == "Home":
    home_page()
elif page == "Chat Messages":
    chat_messages_page()