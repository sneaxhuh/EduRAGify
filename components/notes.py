import streamlit as st
import os
from snowflake_local.connection import session

def take_notes():
   
    try:
        
        docs = session.sql("LIST @docs").collect()
        doc_list = [os.path.basename(doc["name"]) for doc in docs]

        if not doc_list:
            st.warning("No documents found in the Snowflake stage.")
            return

        
        selected_doc = st.selectbox("Choose a document to summarize", doc_list)
        if st.button("Generate Notes"):
            st.info(f"Generating notes for: {selected_doc}")

            
            prompt = (
                f"Make short notes from the document {selected_doc}.\n"
                f"Ensure they are concise and presented as bullet points."
            )

            
            cmd = """
                SELECT snowflake.cortex.complete(
                    ?, 
                    ?
                ) AS notes
            """
            result = session.sql(cmd, params=[st.session_state.model_name, prompt]).to_pandas()

            if not result.empty:
                notes = result["NOTES"].iloc[0]
                st.subheader("Generated Notes")
                st.text_area("Notes Preview", notes, height=300)

                
                download_filename = f"{os.path.splitext(selected_doc)[0]}_notes.txt"
                st.download_button(
                    label="Download Notes",
                    data=notes,
                    file_name=download_filename,
                    mime="text/plain",
                )
            else:
                st.warning("No notes generated. Please check the document or try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
