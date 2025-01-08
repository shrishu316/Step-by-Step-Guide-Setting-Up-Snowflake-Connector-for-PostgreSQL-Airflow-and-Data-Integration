INSERT INTO weather_condition_dim (condition_text)
SELECT DISTINCT conditions
FROM staging_weather_data
WHERE NOT EXISTS (
    SELECT 1 
    FROM weather_condition_dim 
    WHERE (weather_condition_dim.condition_text = staging_weather_data.conditions OR (weather_condition_dim.condition_text IS NULL AND staging_weather_data.conditions IS NULL)) 
);
