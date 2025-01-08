INSERT INTO time_dim (localtimes, hour, day, month, year, minute, weekday)
SELECT DISTINCT 
    localtimes,
    EXTRACT(HOUR FROM localtimes) AS hour,
    EXTRACT(DAY FROM localtimes) AS day,
    EXTRACT(MONTH FROM localtimes) AS month,
    EXTRACT(YEAR FROM localtimes) AS year,
    EXTRACT(MINUTE FROM localtimes) AS minute,
    EXTRACT(DOW FROM localtimes) AS weekday
FROM staging_weather_data
WHERE NOT EXISTS (
    SELECT 1 FROM time_dim WHERE time_dim.localtimes = staging_weather_data.localtimes
);
