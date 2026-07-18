-- Queries to be used over DuckDB to answer same questions of the case.

--============================ QUESTION 01 ========================================
-- Response 1: Average ticket value per year/month block
SELECT 
    pickup_year,
    pickup_month,
    ROUND(AVG(total_amount), 2) AS average_ticket_value
FROM read_parquet('s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet')
WHERE taxi_type = 'yellow'
GROUP BY pickup_year, pickup_month
ORDER BY pickup_year, pickup_month;

-- Response 2: Average ticket value strictly by month part independent of the year
SELECT 
    pickup_month,
    ROUND(AVG(total_amount), 2) AS average_ticket_for_this_month
FROM read_parquet('s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet')
WHERE taxi_type = 'yellow'
GROUP BY pickup_month
ORDER BY pickup_month;

-- Response 3: Global average ticket baseline (Single Value)
SELECT 
    ROUND(AVG(total_amount), 2) AS global_average_ticket
FROM read_parquet('s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet')
WHERE taxi_type = 'yellow';

--============================ QUESTION 02 ========================================
-- Question 3: Average passenger count per hour block in May 2023 (All Fleet)
SELECT 
    pickup_hour,
    ROUND(AVG(passenger_count), 2) AS average_passengers_per_hour
FROM read_parquet('s3://awae-yellow-taxi-case/gold/taxi_trips_curated/*.parquet')
WHERE pickup_year = 2023 AND pickup_month = '05'
GROUP BY pickup_hour
ORDER BY pickup_hour ASC;
