import streamlit as st
import duckdb

def get_connection():
    # Initialize an in-memory DuckDB instance
    con = duckdb.connect()
    
    # Load the httpfs extension to enable HTTPS/S3 queries
    con.execute("INSTALL httpfs; LOAD httpfs;")
    
    # Bind the credentials securely using st.secrets
    con.execute(f"SET s3_access_key_id='{st.secrets['AWS_ACCESS_KEY_ID']}'")
    con.execute(f"SET s3_secret_access_key='{st.secrets['AWS_SECRET_ACCESS_KEY']}'")
    con.execute(f"SET s3_region='{st.secrets['AWS_DEFAULT_REGION']}'")
    
    return con