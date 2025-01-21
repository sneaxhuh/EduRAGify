import streamlit as st
import pandas as pd
import os
from snowflake_local.connection import session

def get_uploaded_files():
    """
    Fetch and return the list of files from the Snowflake stage.
    """
    try:
        docs = session.sql("LIST @docs").collect()
        if not docs:
            return []
        return [
            {
                "File Name": os.path.basename(doc["name"]),
                "Size (KB)": round(doc["size"] / 1024, 2),  
            }
            for doc in docs
        ]
    except Exception as e:
        st.error(f"Error fetching document list: {e}")
        return []

def delete_file(file_name):
    """
    Delete a file from the Snowflake stage.
    """
    try:
        # Execute the Snowflake REMOVE command
        session.sql(f"REMOVE @docs/{file_name}").collect()
        st.success(f"File '{file_name}' has been deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting file '{file_name}': {e}")

def uploaded_files():
    """
    Display the uploaded files with an option to delete them.
    """
    file_data = get_uploaded_files()

    if not file_data:
        st.info("No files have been uploaded yet.")
        return

    st.subheader("Uploaded Files")
    
    
    df = pd.DataFrame(file_data)

    
    for _, row in df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])

        
        col1.text(f"📄 {row['File Name']}")
        col2.text(f"{row['Size (KB)']} KB")

        
        if col3.button("Delete", key=row['File Name']):
            delete_file(row['File Name'])
              
