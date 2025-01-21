import streamlit as st
import os
from snowflake_local.connection import session
from snowflake_local.rag import doc_query

# Function to summarize documents
def summarize_documents():
    
    # Display the subheader for the document summarization section
    st.subheader("Summarize Your Documents")
    
    try:
        # Fetch the list of documents stored in the Snowflake stage
        docs = session.sql("LIST @docs").collect()
        # Extract document names from the fetched list
        doc_list = [os.path.basename(doc["name"]) for doc in docs]

        # Display a warning if no documents are found
        if not doc_list:
            st.warning("No documents found in the Snowflake stage.")
            return
    except Exception as e:
        # Handle and display errors that occur during document fetching
        st.error(f"Error fetching documents: {e}")
        return

    # Dropdown menu for selecting a document to summarize
    selected_doc = st.selectbox("Choose a document to summarize", doc_list)
    
    # Slider for selecting the word limit for the summary
    word_limit = st.slider(
        "Choose Word Limit for Summary",
        min_value=50, 
        max_value=500, 
        step=50, 
        value=200
    )
    
    # Dropdown menu for selecting the desired English level for the summary
    english_level = st.selectbox(
        "Choose English Level for Summary",
        options=["Easy", "Moderate", "Very Professional"],
        index=1  # Default option set to "Moderate"
    )

    # Button to trigger the summarization process
    if st.button("Summarize"):
        # Ensure a document is selected before proceeding
        if not selected_doc:
            st.error("Please select a document.")
            return

        # Map English level options to corresponding prompts
        english_level_prompt = {
            "Easy": "Use simple and clear language.",
            "Moderate": "Use professional yet accessible language.",
            "Very Professional": "Use highly professional and advanced language."
        }[english_level]

        # Construct the prompt for the summarization model
        prompt = (
            f"Summarize the following document: {selected_doc}.\n"
            f"Ensure the summary is within {word_limit} words. "
            f"{english_level_prompt}"
        )

        try:
            # Query the model to generate the summary
            summary = doc_query(prompt)
            if summary:
                # Display the generated summary
                st.write(f"### Summary of {selected_doc}:")
                st.write(summary)
        except Exception as e:
            # Handle and display errors during summarization
            st.error(f"Error generating summary: {e}")
