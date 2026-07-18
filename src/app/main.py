import streamlit as st
from db_connector import get_connection

st.set_page_config(page_title="NYC Taxi Medallion Dashboard", layout="wide")
st.title("NYC Taxi Data Lakehouse Case - Medallion Architecture")

try:
    con = get_connection()
except Exception as e:
    st.error(f"Failed to connect to the database/S3: {e}")
    st.stop()

S3_PATH = "s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet"

st.subheader("Gold Layer Enriched Fact Table KPIs")

query_metrics = f"""
    SELECT 
        COUNT(*) as total_trips,
        ROUND(SUM(total_amount), 2) as net_revenue,
        ROUND(AVG(passenger_count), 2) as average_passengers
    FROM read_parquet('{S3_PATH}')
"""

with st.spinner("Fetching analytical data on-demand from S3 Gold Zone..."):
    df_metrics = con.execute(query_metrics).df()

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips Across Services", f"{int(df_metrics['total_trips'].values[0]):,}")
col2.metric("Total Revenue Accumulated", f"US$ {df_metrics['net_revenue'].values[0]:,}")
col3.metric("Average Passengers per Trip", f"{df_metrics['average_passengers'].values[0]:.2f}")