import streamlit as st
import pandas as pd
from database import get_connection, close_connection
from utils import download_csv

def chat_messages_page():
    connection = get_connection()
    st.title("Chat Messages Viewer")

    # Fetch the list of senders from the chat_messages table
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT sender FROM chat_messages WHERE sender != '+14242926185'")
        senders = [row[0] for row in cursor.fetchall()]

    # Create a dropdown for selecting the sender
    selected_sender = st.selectbox("Select a sender:", senders)

    # Create a button to fetch the data
    if st.button("Fetch Messages"):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cm.*
                FROM chat_messages as cm
                JOIN user_info ui ON cm.sender = ui.user_number
                WHERE (cm.sender = '+14242926185' AND cm.message_type IN ('TEXT', 'AUDIO'))
                OR (ui.user_number = %s AND cm.message_type IN ('TEXT', 'AUDIO'))
                ORDER BY cm.message_date
            """, (selected_sender,))
            data = cursor.fetchall()

        # Get column names (headers) from the cursor description
        headers = [desc[0] for desc in cursor.description]

        # Create a DataFrame with the fetched data
        df = pd.DataFrame(data, columns=headers)

        download_csv(df, "chat_messages")

        # Display the data in a table using Streamlit's table component
        st.table(df)

    close_connection(connection)