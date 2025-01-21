import streamlit as st
import os
from snowflake_local.connection import session, conn
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile

import re

def generate_filename(note_text):
    prompt = f"Given the content of the note between <file> and </file> describe it in at max 4 words without any special characters. DO NOT give anything extra <file> '{note_text}' </file>"
    cmd = """
            SELECT snowflake.cortex.complete(?, ?) AS response
          """
    try:
        response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
        filename = response[0].RESPONSE
       
        # Clean up the filename (remove extra quotes or spaces)
        filename = re.sub(r'["\s]+', '', filename)  # Removes quotes and spaces from filename
        
        return filename
    except Exception as e:
        st.error(f"Error generating filename: {e}")
        return None


def save_note_as_pdf(note_text, filename):
    try:
        
        buffer = io.BytesIO()  # Create an in-memory buffer

        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        c.drawString(100, height - 100, note_text)  # Writing note text to the PDF
        c.save()
        
        buffer.seek(0)  
        with open(filename, "wb") as f:
            f.write(buffer.getvalue())
        st.success(f"Note saved successfully!")

        # Return the filename to upload it to Snowflake
        return filename
    except Exception as e:
        # Catch and report any exceptions
        st.error(f"Error saving note as PDF: {e}")
        return None


def upload_to_snowflake_stage(file_path):
    try:
        stage_name = "DOCS"
        stage_path = f"@{conn['database']}.{conn['schema']}.{stage_name}"

        
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file at {file_path} does not exist.")

        
        sanitized_filename = os.path.basename(file_path).replace(" ", "_")
        sanitized_file_path = os.path.join(os.path.dirname(file_path), sanitized_filename)

        
        if file_path != sanitized_file_path:
            os.rename(file_path, sanitized_file_path)
            

        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, sanitized_filename)
            
            # Copy the file to the temporary directory
            with open(sanitized_file_path, "rb") as src_file, open(temp_file_path, "wb") as temp_file:
                temp_file.write(src_file.read())
            
            # Use the PUT command with the temporary file path
            put_command = f"PUT file://{os.path.abspath(temp_file_path)} {stage_path}/ AUTO_COMPRESS = FALSE"
            put_result = session.sql(put_command).collect()
            

        # Refresh and process the stage as before
        refresh_command = f"ALTER STAGE {stage_name} REFRESH;"
        session.sql(refresh_command).collect()
       

        # Execute the insertion command
        insertion_command = """
        INSERT INTO docs_chunks_table (relative_path, size, file_url,
                                       scoped_file_url, chunk)
        SELECT relative_path, 
               size, 
               file_url, 
               build_scoped_file_url(@docs, relative_path) AS scoped_file_url,
               func.chunk AS chunk
        FROM directory(@docs),
             TABLE(text_chunker (TO_VARCHAR(SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@docs, 
                                  relative_path, {'mode': 'LAYOUT'})))) AS func;
        """
        session.sql(insertion_command).collect()

    
    except FileNotFoundError as fnf_error:
        st.error(f"File not found: {fnf_error}")
    except Exception as e:
        st.error(f"Error uploading file: {e}")
