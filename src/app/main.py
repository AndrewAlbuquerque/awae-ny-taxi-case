# src/app/main.py
import streamlit as st
from db_connector import get_connection

st.set_page_config(page_title="NYC Taxi Medallion Dashboard", layout="wide")
st.title("🚖 NYC Taxi Data Lakehouse - Medallion Architecture")

# 1. Initialize safe DuckDB connection with S3 credentials mapping
try:
    con = get_connection()
except Exception as e:
    st.error(f"Failed to connect to the database or AWS S3: {e}")
    st.stop()

# Define the global S3 path pointing to the curated granular gold zone
S3_PATH = "s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet"

# ==============================================================================
# SECTION 1: GLOBAL OPERATIONAL KPIs (THE TOP 3 METRICS)
# ==============================================================================
st.subheader("Gold Layer Operational Baseline KPIs")

query_global_metrics = f"""
    SELECT 
        COUNT(*) as total_trips,
        ROUND(SUM(total_amount), 2) as net_revenue,
        ROUND(AVG(passenger_count), 2) as average_passengers
    FROM read_parquet('{S3_PATH}')
"""

with st.spinner("Fetching global metrics from S3 Gold Zone..."):
    df_global = con.execute(query_global_metrics).df()

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips Across Services", f"{int(df_global['total_trips'].values[0]):,}")
col2.metric("Total Revenue Accumulated", f"US$ {df_global['net_revenue'].values[0]:,}")
col3.metric("Average Passengers per Trip", f"{df_global['average_passengers'].values[0]:.2f}")

st.markdown("---")

# ==============================================================================
# SECTION 2: CASE BUSINESS QUESTIONS BREAKDOWN
# ==============================================================================
st.header("📋 Case Business Questions Breakdown")

# --- QUESTION 2 ZONE ---
st.subheader("Question 2: Yellow Taxi Monthly Average Ticket Analysis")
st.caption("Analytical evaluation of the average total_amount received per month across the Yellow Taxi fleet under three analytical dimensions.")

query_q2_r1 = f"""
    SELECT 
        pickup_year AS "Year",
        pickup_month AS "Month",
        ROUND(AVG(total_amount), 2) AS "Average Ticket (US$)"
    FROM read_parquet('{S3_PATH}')
    WHERE taxi_type = 'yellow'
    GROUP BY pickup_year, pickup_month
    ORDER BY pickup_year, pickup_month;
"""

query_q2_r2 = f"""
    SELECT 
        pickup_month AS "Month Part",
        ROUND(AVG(total_amount), 2) AS "Sessional Average (US$)"
    FROM read_parquet('{S3_PATH}')
    WHERE taxi_type = 'yellow'
    GROUP BY pickup_month
    ORDER BY pickup_month;
"""

query_q2_r3 = f"""
    SELECT ROUND(AVG(total_amount), 2) AS global_average_ticket
    FROM read_parquet('{S3_PATH}')
    WHERE taxi_type = 'yellow';
"""

with st.spinner("Processing Question 2 analytical cubes..."):
    df_q2_r1 = con.execute(query_q2_r1).df()
    df_q2_r2 = con.execute(query_q2_r2).df()
    df_q2_r3 = con.execute(query_q2_r3).df()

# Display Q2 answers inside organized inner columns
q2_col1, q2_col2 = st.columns([2, 1])

with q2_col1:
    st.markdown("**View 1: Monthly Trend per Year Block**")
    st.dataframe(df_q2_r1, use_container_width=True, hide_index=True)
    
    st.markdown("**View 2: Sessional Sazonal Average (Strictly by Month Part)**")
    st.dataframe(df_q2_r2, use_container_width=True, hide_index=True)

with q2_col2:
    st.markdown("**View 3: Global Reference**")
    st.metric(
        label="Global Yellow Ticket Average", 
        value=f"US$ {df_q2_r3['global_average_ticket'].values[0]:.2f}",
        help="A single value baseline considering all processed records for yellow taxis."
    )

st.markdown("---")

# --- QUESTION 3 ZONE ---
st.subheader("Question 3: Hourly Passenger Distribution Analysis (May 2023)")
st.caption("Average number of passengers (passenger_count) per each hour of the day for trips taken in May considering the entire fleet.")

query_q3 = f"""
    SELECT 
        pickup_hour AS "Hour of Day",
        ROUND(AVG(passenger_count), 2) AS "Average Passengers"
    FROM read_parquet('{S3_PATH}')
    WHERE pickup_year = 2023 AND pickup_month = '05'
    GROUP BY pickup_hour
    ORDER BY pickup_hour ASC;
"""

with st.spinner("Processing Question 3 distribution metrics..."):
    df_q3 = con.execute(query_q3).df()

# Display Q3 using a layout combining chart and data tabular format
q3_col1, q3_col2 = st.columns([2, 1])

with q3_col1:
    st.markdown("**Visual Hourly Traffic Profile Graph**")
    # Draw a line chart representing the average passenger load per hour
    st.line_chart(data=df_q3.set_index("Hour of Day"), y="Average Passengers")

with q3_col2:
    st.markdown("**Data Table Representation**")
    st.dataframe(df_q3, use_container_width=True, hide_index=True, height=380)