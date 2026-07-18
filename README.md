# NYC Taxi Medallion Analytics - Data Lakehouse

An end-to-end, ultra-low-cost Data Lakehouse infrastructure designed to ingest, process, clean, and analyze millions of trip records from New York City's Yellow and Green Taxi fleets.

This project implements a serverless architecture leveraging **Apache Spark** via **Databricks Connect** for high-scale processing, coupled with **DuckDB** and **Streamlit** for on-demand serverless analytical reporting directly from **AWS S3**.

---

## 🗺️ System Architecture & Data Flow

The project strictly implements the **Medallion Architecture** combined with a classic **Star Schema (Dimensional Modeling)** design patterns to ensure maximum auditability, performance, and clear business readability.

```text
       [ TLC Public CloudFront Data Source ]
                         |
                         | (HTTP Streamed Request Ingestion via Boto3)
                         v
+-----------------------------------------------------------+
|                      AWS S3 BUCKET                        |
|                                                           |
|  +-----------------------------------------------------+  |
|  | 00. LANDING ZONE (Standard Raw Parquet Files)       |  |
|  |     ├── landing/yellow_tripdata/                    |  |
|  |     └── landing/green_tripdata/                     |  |
|  +------------------------┬----------------------------+  |
|                           |                               |
|                           | (Individual Month Iteration & Schema Baseline)
|                           v                               |
|  +-----------------------------------------------------+  |
|  | 01. BRONZE LAYER (Segregated Domain Delta Tables)   |  |
|  |     ├── bronze/yellow_tripdata_bronze/ (Delta)      |  |
|  |     └── bronze/green_tripdata_bronze/  (Delta)      |  |
|  +------------------------┬----------------------------+  |
|                           |                               |
|                           | (Full Schema Expansion & Timestamp Unification)
|                           v                               |
|  +-----------------------------------------------------+  |
|  | 02. SILVER LAYER (Integrated Aligned Tables)        |  |
|  |     ├── silver/taxi_tripdata_silver/ (Delta Moving) |  |
|  |     |                                               |  |
|  |     |  [3 Static Metadata Dimension Tables]         |  |
|  |     ├── silver/dim_tpep_provider/    (Parquet)      |  |
|  |     ├── silver/dim_ratecode/         (Parquet)      |  |
|  |     └── silver/dim_payment_type/     (Parquet)      |  |
|  +------------------------┬----------------------------+  |
|                           |                               |
|                           | (Dimensional Joins, Business Filters & Time Splits)
|                           v                               |
|  +-----------------------------------------------------+  |
|  | 03. GOLD LAYER (Curated Star Schema Fact Table)     |  |
|  |     └── gold/taxi_trips_curated/ (Parquet Format)   |  |
|  |          └── Only explicit text definitions used    |  |
|  +------------------------┬----------------------------+  |
+---------------------------|-------------------------------+
                            |
                            | (HTTPS On-Demand Remote Querying via HTTPFS)
                            v
     +---------------------------------------------+
     |   ANALYTICAL CONSUMPTION & REPORTING ZONE   |
     |                                             |
     |   [ DuckDB Local SQL Engine ]               |
     |   └── Executes lightning fast calculations   |
     |                                             |
     |   [ Streamlit Cloud Web Application UI ]    |
     |   └── Renders interactive business charts   |
     +---------------------------------------------+

```

### Architectural Breakdown

* **Landing Zone**: Houses immutable raw data exactly as requested from the source, guaranteeing a zero-loss entry baseline.
* **Bronze Layer**: Implements a structured schema baseline using the Delta Lake format, adding critical technical ingestion metadata (`source_file`).
* **Silver Layer**: Handles entity consolidation without filtering records (*Full Retention*). This layer splits metadata into **3 standard Parquet dimension tables** (`dim_tpep_provider`, `dim_ratecode`, `dim_payment_type`) directly derived from official documentation mapping.
* **Gold Layer**: Represents the business-ready environment. It filters out anomalies (`total_amount > 0` and `passenger_count > 0`), performs lookups against the dimension tables, drops technical numeric keys, and enriches the data with isolated time components (`pickup_year`, `pickup_month`, `pickup_day`, `pickup_hour`).

---

## 🛠️ Tech Stack & Core Resources

* **Orchestration & Compute**: Databricks Serverless Compute / Community Runtime via Apache Spark 3.5+.
* **Storage Layer**: AWS S3 (Simple Storage Service) utilized as a high-performance Data Lakehouse via Databricks Unity Catalog External Locations.
* **Table Formats**: Delta Lake (for transactional compliance and safety in Bronze/Silver moving files) and Apache Parquet (optimized compressed format for Gold consumption and Dimension lookups).
* **Local In-Memory Analytics**: DuckDB Engine, allowing massive analytical parallel query processing over remote S3 parquet files using zero persistent cloud compute.
* **Presentation & UI Layout**: Streamlit Web Framework deployed on Streamlit Community Cloud.

---

## 📂 Repository Structure

The code is organized in a clean **Monorepo** structure:

```text
├── analysis/
│   ├── queries_duckdb.sql   # Target analytical business queries using DuckDB
│   └── spark_analysis.py    # Reference validation using PySpark & SparkSQL views
├── src/
│   ├── app/
│   │   ├── db_connector.py  # Secured credentials attachment for DuckDB S3 pipeline
│   │   └── main.py          # Streamlit UI visual mapping layout and charts
│   └── etl/
│       ├── 00_ingestion_to_landing.py  # Multi-source asynchronous HTTP data ingestion
│       ├── 01_landing_to_bronze.py     # Domain isolation, double casting and Delta write
│       ├── 02_bronze_to_silver.py      # Core data movement integration (Full Retention)
│       ├── 02_b_create_dimensions.py   # Overwrites textual dictionary lookup dimension tables
│       └── 03_silver_to_gold.py        # Dimensional joins, corporate filters and time parsing
├── .gitignore
├── INSTALL.md               # Step-by-step Technical Installation Manual
├── README.md                # Project Overview page
└── requirements.txt         # Presentation environment application dependencies

```

---

## 📊 Analytical Business Questions Solved

The curated Gold layer fact table is optimized to seamlessly answer key operational and sessional insights. The queries are solved across both local **DuckDB** and cloud-based **SparkSQL** environments:

### Question 2: What is the average total amount received in a month considering all yellow taxis in the fleet?

The pipeline resolves this under three necessary management horizons:

1. **Response 1 (Time Series)**: The exact average value broken down per specific calendar blocks (Year/Month).
2. **Response 2 (Seasonal Analysis)**: The average value grouped strictly by the numerical month digit, independent of the calendar year, isolating historical seasonality parameters.
3. **Response 3 (Global Average)**: A macro consolidated baseline (single scalar value) indicating the historical average trip price across the entire Yellow fleet.

### Question 3: What is the average number of passengers per hour of the day for trips taken in May considering the entire fleet?

Generates an hourly distribution curve (0 to 23 hours) mapping the vehicle load factor profile to pinpoint traffic peak performance blocks throughout the month of May.

---

## 🚀 Technical Setup & Deployment

To install, configure AWS infrastructure, build secret scopes, and run this project from scratch, please follow the comprehensive manual documented inside [INSTALL.md](https://www.google.com/search?q=./INSTALL.md).