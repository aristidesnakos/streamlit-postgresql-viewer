import streamlit as st
import psycopg2
import pandas as pd

# Load your AWS RDS credentials from env_var.py
from env_var import AWS_DB_HOST, AWS_DB_NAME, AWS_DB_USER, AWS_DB_PASSWORD

# Connect to the AWS RDS instance
connection = psycopg2.connect(
    host=AWS_DB_HOST,
    database=AWS_DB_NAME,
    user=AWS_DB_USER,
    password=AWS_DB_PASSWORD
)

# Create a Streamlit app
st.title("AWS RDS Table Viewer")

# Add a text input to enter a table name dynamically
table_name = st.text_input("Enter a table name:")

selected_fields = []

# Create a UI element for selecting table fields
if st.button("Fetch Data"):
    if table_name:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()

        # Get column names (headers) from the cursor description
        headers = [desc[0] for desc in cursor.description]

        # Create a multi-select UI for selecting table fields
        selected_fields = st.multiselect("Select table fields:", headers, default=headers)

        # Create a DataFrame with selected headers
        df = pd.DataFrame(data, columns=selected_fields)

        # Display the data in a larger table
        st.dataframe(df, height=600)  # Adjust the height as needed
    else:
        st.warning("Please enter a table name.")

# Close the database connection when the app is closed
st.text("Note: The database connection will be closed when you close this app.")