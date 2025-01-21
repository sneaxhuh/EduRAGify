import streamlit as st
from components.summarizer import summarize_documents
from components.quiz import generate_quiz
from components.notes import take_notes
from snowflake_local.rag import doc_query_general, config_options, init_messages
from snowflake_local.connection import session
import os
from streamlit_option_menu import option_menu
from components.data_ingestion import upload_to_snowflake_stage, save_note_as_pdf
from components.files import uploaded_files

def main():
    st.title("EduRagify")

    with st.sidebar:
        tab = option_menu(
        menu_title="Select a Tab",
        options=[
            "Data Ingestion",  
            "Summarizer",      
            "Quiz Generator",   
            "Document Query",  
            "Notes" ,
            "Files Uploaded"           
        ],
        icons = ['database-add','pen','question-circle','file-earmark-richtext','journal-bookmark','floppy']
    )

    st.session_state.rag = st.sidebar.checkbox("Use your own documents as context?")


    config_options()
    init_messages()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Data Ingestion Tab
    if tab == "Data Ingestion":
        st.subheader("Upload Files to Snowflake")

        # File uploader for Snowflake upload
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "pptx"])
        

        if uploaded_file:
            st.write(f"Uploaded file: {uploaded_file.name}")

           
            file_path = f"./uploaded_files/{uploaded_file.name}"


            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())


            if st.button("Upload to Snowflake"):
                try:
                    upload_to_snowflake_stage(file_path)
                    st.success(f"File '{uploaded_file.name}' uploaded to Snowflake!")
                except Exception as e:
                    st.error(f"Error uploading file: {e}")

    
        st.subheader("Add a Manual Note")
        manual_note = st.text_area("Enter your note", placeholder="Type your note here...")
        note_filename = st.text_input("File_name")
        if st.button("Save Note"):
            try:
                save_note_as_pdf(manual_note, note_filename)
            
                upload_to_snowflake_stage(note_filename)
                st.success(f"Your note has been saved and uploaded as {note_filename}!")

            except Exception as e:
                st.error(f"Error saving or uploading your note: {e}")

    
    elif tab == "Summarizer":
        summarize_documents()

    
    elif tab == "Quiz Generator":
        generate_quiz()

    
    elif tab == "Document Query":
        st.subheader("Ask a Question")
        question = st.text_input("Enter your question")
        if question:
            doc_query_general(question)

    elif tab == "Notes":
        take_notes()
    
    elif tab == "Files Uploaded":
        uploaded_files()

if __name__ == "__main__":
    main()
