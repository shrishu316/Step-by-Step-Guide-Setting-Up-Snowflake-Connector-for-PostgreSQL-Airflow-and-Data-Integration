


INSERT INTO weather_fact (
    city_id, time_id, condition_id, temperature_celsius, temperature_fahrenheit, humidity, wind_speed_kph,
    precipitation_mm, visibility_km, air_quality_co, air_quality_o3, air_quality_us_epa
)
SELECT 
    cd.city_id, td.time_id, wcd.condition_id, s.temperature_celsius, s.temperature_fahrenheit,
    s.humidity, s.wind_speed_kph, s.precipitation_mm, s.visibility_km, s.air_quality_co,
    s.air_quality_o3, s.air_quality_us_epa
FROM staging_weather_data s
JOIN city_dim cd ON s.city_name = cd.city_name
JOIN time_dim td ON s.localtimes = td.localtimes
JOIN weather_condition_dim wcd ON s.conditions = wcd.condition_text
WHERE NOT EXISTS (
    SELECT 1
    FROM weather_fact wf
    WHERE wf.city_id = cd.city_id
      AND wf.time_id = td.time_id
      AND wf.condition_id = wcd.condition_id
      AND (wf.temperature_celsius = s.temperature_celsius OR (wf.temperature_celsius IS NULL AND s.temperature_celsius IS NULL))
      AND (wf.temperature_fahrenheit = s.temperature_fahrenheit OR (wf.temperature_fahrenheit IS NULL AND s.temperature_fahrenheit IS NULL))
      AND (wf.humidity = s.humidity OR (wf.humidity IS NULL AND s.humidity IS NULL))
      AND (wf.wind_speed_kph = s.wind_speed_kph OR (wf.wind_speed_kph IS NULL AND s.wind_speed_kph IS NULL))
      AND (wf.precipitation_mm = s.precipitation_mm OR (wf.precipitation_mm IS NULL AND s.precipitation_mm IS NULL))
      AND (wf.visibility_km = s.visibility_km OR (wf.visibility_km IS NULL AND s.visibility_km IS NULL))
      AND (wf.air_quality_co = s.air_quality_co OR (wf.air_quality_co IS NULL AND s.air_quality_co IS NULL))
      AND (wf.air_quality_o3 = s.air_quality_o3 OR (wf.air_quality_o3 IS NULL AND s.air_quality_o3 IS NULL))
      AND (wf.air_quality_us_epa = s.air_quality_us_epa OR (wf.air_quality_us_epa IS NULL AND s.air_quality_us_epa IS NULL))
);
 