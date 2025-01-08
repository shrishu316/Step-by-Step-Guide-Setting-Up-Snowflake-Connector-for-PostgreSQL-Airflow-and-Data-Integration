----------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS city_dim (
    city_id SERIAL PRIMARY KEY,          -- Surrogate primary key for uniqueness and relationships
    city_name TEXT NOT NULL,        -- Name of the city
    region TEXT NOT NULL,           -- Region the city belongs to
    country TEXT NOT NULL,          -- Country of the city
    latitude DOUBLE PRECISION,      -- Latitude coordinate
    longitude DOUBLE PRECISION,     -- Longitude coordinate
    tz_id TEXT,                     -- Timezone ID
    valid_from TIMESTAMP,           -- Start of the validity period
    valid_to TIMESTAMP,             -- End of the validity period
    current_flag BOOLEAN,           -- Indicates if this is the current record for the city
    UNIQUE (city_name, region, country, current_flag) -- Enforces logical uniqueness
);

----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS time_dim (
    time_id SERIAL PRIMARY KEY,
    localtimes TIMESTAMP NOT NULL,
    year INT,
    month INT,
    day INT,
    hour INT,
    minute INT,
    weekday TEXT
);

-----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS weather_condition_dim (
    condition_id SERIAL PRIMARY KEY,
    condition_text TEXT NOT NULL UNIQUE
);


-------------------------------------------------------------------------


CREATE TABLE IF NOT EXISTS weather_fact (
    fact_id SERIAL PRIMARY KEY,
    city_id INT REFERENCES city_dim(city_id),
    time_id INT REFERENCES time_dim(time_id),
    condition_id INT REFERENCES weather_condition_dim(condition_id),
    temperature_celsius FLOAT,
    temperature_fahrenheit FLOAT,
    humidity INT,
    wind_speed_kph FLOAT,
    precipitation_mm FLOAT,
    visibility_km FLOAT,
    air_quality_co FLOAT,
    air_quality_o3 FLOAT,
    air_quality_us_epa INT
);
------------------------------------------------------------------------------

----------to check duplicates

SELECT localtimes, COUNT(*)
FROM staging_weather_data
GROUP BY localtimes
HAVING COUNT(*) > 1;


SELECT localtimes
FROM time_dim
WHERE localtimes IN (
    SELECT localtimes 
    FROM staging_weather_data
    GROUP BY localtimes
    HAVING COUNT(*) > 1
);