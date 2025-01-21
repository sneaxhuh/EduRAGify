from snowflake.snowpark import Session
import streamlit as st


conn = {
    "account": st.secrets["Snowflake"]["SNOWFLAKE_ACCOUNT"],
    "user": st.secrets["Snowflake"]["SNOWFLAKE_USER"],
    "password": st.secrets["Snowflake"]["SNOWFLAKE_PASSWORD"],
    "database": st.secrets["Snowflake"]["SNOWFLAKE_DATABASE"],
    "schema": st.secrets["Snowflake"]["SNOWFLAKE_SCHEMA"]
}



session = Session.builder.configs(conn).create()