{{ config(
    materialized="table",
    schema="gold",
    tags=["gold"],
) }}

WITH siver_weather AS (
    SELECT * FROM {{ ref('silver_weather') }}
)

SELECT
    city_name,
    DATE(recorded_at) AS metric_date,
    ROUND(CAST(AVG(temperature_2m) AS NUMERIC), 2) AS avg_temperature,
    MIN(temperature_2m) AS min_temperature,
    MAX(temperature_2m) AS max_temperature,
    ROUND(CAST(AVG(relative_humidity_2m) AS NUMERIC), 2) AS avg_humidity,
    COUNT(*) AS total_measurements
FROM siver_weather
GROUP BY 1, 2
ORDER BY metric_date DESC, city_name ASC