import streamlit as st
from database import get_connection, close_connection
from utils import fetch_object_names, display_object_data

def home_page():
    connection = get_connection()
    
    st.title("AWS RDS Object Viewer")

    # Create a dropdown for selecting the object type (table, sequence, or type)
    object_type = st.selectbox("Select an object type:", ["Table", "Sequence", "Type"])

    # Fetch the object names based on the selected type
    object_names = fetch_object_names(connection, object_type)

    # Create a dropdown for selecting the object name
    object_name = st.selectbox("Select an object:", object_names)

    # Create a UI element for selecting fields (for tables only)
    if st.button("Fetch Data"):
        display_object_data(connection, object_type, object_name)

    st.text("Note: The database connection will be closed when you close this app.")
    
    close_connection(connection)