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
st.title("AWS RDS Object Viewer")

# Create a dropdown for selecting the object type (table, sequence, or type)
object_type = st.selectbox("Select an object type:", ["Table", "Sequence", "Type"])

object_names = []

# Fetch the object names based on the selected type
if object_type == "Table":
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        object_names = [row[0] for row in cursor.fetchall()]
elif object_type == "Sequence":
    with connection.cursor() as cursor:
        cursor.execute("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema='public'")
        object_names = [row[0] for row in cursor.fetchall()]
elif object_type == "Type":
    with connection.cursor() as cursor:
        cursor.execute("SELECT typname FROM pg_type WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')")
        object_names = [row[0] for row in cursor.fetchall()]

# Create a dropdown for selecting the object name
object_name = st.selectbox("Select an object:", object_names)

selected_fields = []

# Create a UI element for selecting fields (for tables only)
if st.button("Fetch Data"):
    if object_type == "Table" and object_name:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {object_name}")
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

    elif object_type == "Sequence" and object_name:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT last_value, increment_by, max_value FROM {object_name}")
            data = cursor.fetchone()

        st.write(f"Last Value: {data[0]}")
        st.write(f"Increment By: {data[1]}")
        st.write(f"Max Value: {data[2]}")

    elif object_type == "Type" and object_name:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                    typname,
                    typlen,
                    typbyval,
                    typcategory,
                    CASE typcategory
                        WHEN 'A' THEN 'Array'
                        WHEN 'B' THEN 'Base'
                        WHEN 'C' THEN 'Composite'
                        WHEN 'D' THEN 'Domain'
                        WHEN 'E' THEN 'Enum'
                        WHEN 'P' THEN 'Pseudo'
                        WHEN 'R' THEN 'Range'
                        WHEN 'S' THEN 'Special'
                        WHEN 'U' THEN 'User-defined'
                        ELSE 'Unknown'
                    END AS category_description
                FROM pg_type
                WHERE typname = '{object_name}'
            """)
            data = cursor.fetchone()

        st.write(f"Type Name: {data[0]}")
        st.write(f"Type Length: {data[1]}")
        st.write(f"Type By Value: {data[2]}")
        st.write(f"Type Category: {data[3]} ({data[4]})")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT typname, typcategory FROM pg_type WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')")
            type_data = cursor.fetchall()

        type_df = pd.DataFrame(type_data, columns=["Type Name", "Type Category"])
        st.dataframe(type_df)

    else:
        st.warning("Please select an object type and name.")

    st.text("Note: The database connection will be closed when you close this app.")

# Close the database connection when the app is closed
connection.close()