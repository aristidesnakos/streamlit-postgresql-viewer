import streamlit as st
import pandas as pd
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder

def fetch_object_names(connection, object_type):
    object_names = []

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

    return object_names

def display_object_data(connection, object_type, object_name):
    if object_type == "Table" and object_name:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {object_name}")
            data = cursor.fetchall()

        # Get column names (headers) from the cursor description
        headers = [desc[0] for desc in cursor.description]

        # Create a multi-select UI for selecting table fields
        selected_fields = st.multiselect("Select table fields:", headers, default=headers)

        # Create a DataFrame with selected headers
        df = pd.DataFrame(data, columns=headers)
        filtered_data = df[selected_fields]

        # Display the data using the ag-Grid library
        gb = GridOptionsBuilder.from_dataframe(filtered_data)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gridOptions = gb.build()

        grid_response = AgGrid(
            filtered_data,
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
                        WHEN 'E' THEN (
                            SELECT array_agg(enumlabel::text)
                            FROM pg_enum
                            WHERE enumtypid = (
                                SELECT oid
                                FROM pg_type
                                WHERE typname = '{object_name}'
                            )
                        )
                        ELSE NULL
                    END AS enum_values
                FROM pg_type
                WHERE typname = '{object_name}'
            """)
            data = cursor.fetchone()

        st.write(f"Type Name: {data[0]}")
        st.write(f"Type Length: {data[1]}")
        st.write(f"Type By Value: {data[2]}")
        st.write(f"Type Category: {data[3]}")

        if data[4] is not None:
            st.write(f"Enum Values: {', '.join(data[4])}")

    else:
        st.warning("Please select an object type and name.")

    # Add a download button if data is available
    download_csv(df, "data")
        
def download_csv(data, filename):
    csv_data = data.to_csv(index=False)
    b64 = BytesIO(csv_data.encode()).getvalue()
    st.download_button(
        label="Download CSV",
        data=b64,
        file_name=f'{filename}.csv',
        mime="text/csv",
    )