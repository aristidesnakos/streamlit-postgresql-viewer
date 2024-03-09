from st_aggrid import AgGrid, GridOptionsBuilder
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

# Get a list of table names from the database
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    table_names = [row[0] for row in cursor.fetchall()]

# Create a dropdown for selecting the table name
table_name = st.selectbox("Select a table:", table_names)

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

        # Display the data using the ag-Grid library
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gridOptions = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT',
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True,
            height=600,
            width='100%',
            reload_data=True
        )

        data = grid_response['data']
        selected = grid_response['selected_rows']
        df = pd.DataFrame(selected)

        st.text("Note: The database connection will be closed when you close this app.")

# Close the database connection when the app is closed
connection.close()