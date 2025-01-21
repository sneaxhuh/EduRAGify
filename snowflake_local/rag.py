import streamlit as st
import json
from snowflake.core import Root
from snowflake_local.connection import session



NUM_CHUNKS = 5
slide_window = 7  
CORTEX_SEARCH_DATABASE = st.secrets["Snowflake"]["SNOWFLAKE_DATABASE"]
CORTEX_SEARCH_SCHEMA = st.secrets["Snowflake"]["SNOWFLAKE_SCHEMA"]
CORTEX_SEARCH_SERVICE = st.secrets["Snowflake"]["CORTEX_SEARCH_SERVICE"]
COLUMNS = ["chunk", "relative_path"]


root = Root(session)

# Cortex Search Service
svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

def init_messages():

    # Initialize chat history
    if st.session_state.clear_conversation or "messages" not in st.session_state:
        st.session_state.messages = []

def config_options():
    st.sidebar.selectbox('Select your model:', (
        'mixtral-8x7b', 'snowflake-arctic', 'mistral-large', 'llama3-8b',
        'llama3-70b', 'reka-flash', 'mistral-7b', 'llama2-70b-chat', 'gemma-7b'
    ), key="model_name")

    

    st.sidebar.checkbox('Chat history?', key="use_chat_history", value = True)
    st.sidebar.button("Start Over", key="clear_conversation", on_click=init_messages)
    st.sidebar.expander("Session State").write(st.session_state)

def get_similar_chunks_search_service(query):
   
    response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)

    st.sidebar.json(response.json())
    return response.json()

def get_chat_history():
    
    chat_history = []
    
    start_index = max(0, len(st.session_state.messages) - slide_window)
    for i in range (start_index , len(st.session_state.messages) -1):
         chat_history.append(st.session_state.messages[i])

    return chat_history


def create_prompt(myquestion):
    if st.session_state.rag:
        if st.session_state.use_chat_history:
            chat_history = get_chat_history()

            if chat_history != []:  
                question_summary = summarize_question_with_history(chat_history, myquestion)
                prompt_context = get_similar_chunks_search_service(question_summary)
            else:
                prompt_context = get_similar_chunks_search_service(myquestion)
        else:
            prompt_context = get_similar_chunks_search_service(myquestion)
            chat_history = ""

        prompt = f"""
        You are an expert chat assistant that extracts information from the CONTEXT provided
        between <context> and </context> tags.
        You offer a chat experience considering the information included in the CHAT HISTORY
        provided between <chat_history> and </chat_history> tags.
        When answering the question contained between <question> and </question> tags,
        be concise and do not hallucinate.
        If you don’t have the information, just say so.

        Do not mention the CONTEXT used in your answer.
        Do not mention the CHAT HISTORY used in your answer.

        Only answer the question if you can extract it from the CONTEXT provided.

        <chat_history>
        {chat_history}
        </chat_history>
        <context>
        {prompt_context}
        </context>
        <question>
        {myquestion}
        </question>
        Answer:
        """

        json_data = json.loads(prompt_context)

        relative_paths = set(item['relative_path'] for item in json_data['results'])

    else:
        prompt = f"""[0]
        'Question:  
        {myquestion} 
        Answer: '
        """
        relative_paths = "None"

    return prompt, relative_paths


def summarize_question_with_history(chat_history, question):

    prompt = f"""
        Based on the chat history below and the question, generate a query that extends the question
        with the chat history provided. The query should be in natural language.
        Answer with only the query. Do not add any explanation.
        
        <chat_history>
        {chat_history}
        </chat_history>
        <question>
        {question}
        </question>
    """
    
   
    cmd = """
        SELECT snowflake.cortex.complete(?, ?) AS response
    """
    result = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    
    
    if result and len(result) > 0:
        sumary = result[0].RESPONSE  # Access the response field in the first row
    else:
        sumary = ""

    return sumary


def complete(myquestion):
    prompt, relative_paths = create_prompt(myquestion)
    cmd = """
            SELECT snowflake.cortex.complete(?, ?) AS response
          """
    df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    return df_response, relative_paths

def doc_query_general(question):
    
    st.session_state.messages.append({"role": "user", "content": question})

    
    with st.chat_message("user"):
        st.markdown(question)

    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        
        with st.spinner(f"{st.session_state.model_name} thinking..."):
            
            response, relative_paths = complete(question)

            message_placeholder.markdown(response[0].RESPONSE)

            
            if relative_paths != "None":
                with st.sidebar.expander("Related Documents"):
                    for path in relative_paths:
                        
                        cmd2 = f"SELECT GET_PRESIGNED_URL(@docs, '{path}', 360) AS URL_LINK FROM directory(@docs)"
                        df_url_link = session.sql(cmd2).to_pandas()
                        url_link = df_url_link.at[0, 'URL_LINK']

                        
                        display_url = f"Doc: [{path}]({url_link})"
                        st.sidebar.markdown(display_url)

    
    st.session_state.messages.append({"role": "assistant", "content": response[0].RESPONSE})

def doc_query(question):
   
        # Process the question and generate a response
        with st.spinner(f"{st.session_state.model_name} thinking..."):
            # Call the answer_question function to get the response and related document paths
            response, relative_paths = complete(question)

            # Display the assistant's response in the chat
            st.write(response[0].RESPONSE)

            # If there are related documents, display them in the sidebar
            if relative_paths != "None":
                with st.sidebar.expander("Related Documents"):
                    for path in relative_paths:
                        # Fetch presigned URL for the related document
                        cmd2 = f"SELECT GET_PRESIGNED_URL(@docs, '{path}', 360) AS URL_LINK FROM directory(@docs)"
                        df_url_link = session.sql(cmd2).to_pandas()
                        url_link = df_url_link.at[0, 'URL_LINK']

                        # Display the document link in the sidebar
                        display_url = f"Doc: [{path}]({url_link})"
                        st.sidebar.markdown(display_url)



