-- Update city_dim with SCD Type 2 logic
UPDATE city_dim
SET valid_to = NOW(), current_flag = FALSE
WHERE EXISTS (
    SELECT 1
    FROM staging_weather_data s
    WHERE city_dim.city_name = s.city_name
      AND (city_dim.region != s.region OR city_dim.country != s.country
           OR city_dim.latitude != s.latitude OR city_dim.longitude != s.longitude
           OR city_dim.tz_id != s.tz_id)
      AND city_dim.current_flag = TRUE
);

INSERT INTO city_dim (city_name, region, country, latitude, longitude, tz_id, valid_from, valid_to, current_flag)
SELECT DISTINCT city_name, region, country, latitude, longitude, tz_id, NOW(), '9999-12-31'::TIMESTAMP, TRUE
FROM staging_weather_data
WHERE NOT EXISTS (
    SELECT 1
    FROM city_dim
    WHERE city_dim.city_name = staging_weather_data.city_name
      AND city_dim.current_flag = TRUE
);
