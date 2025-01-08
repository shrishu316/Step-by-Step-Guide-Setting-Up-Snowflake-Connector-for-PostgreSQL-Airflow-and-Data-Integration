from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import timedelta

# Configuration
CITIES = ['Tallinn', 'London', 'New York', 'Tokyo', 'New Delhi']
POSTGRES_CONN_ID = 'postgres_default'

logger = LoggingMixin().log

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 3,
    'retry_delay': timedelta(seconds=10),
}

# DAG definition
with DAG(
    dag_id='loading',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
) as dag:

    @task()
    def process_staging_to_star_schema():
        """Transform staging data into the star schema."""
        try:
            logger.info("Processing staging data into star schema.")
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS city_dim (
                city_id SERIAL PRIMARY KEY,         
                city_name TEXT NOT NULL,        
                region TEXT NOT NULL,           
                country TEXT NOT NULL,          
                latitude DOUBLE PRECISION,      
                longitude DOUBLE PRECISION,     
                tz_id TEXT,                     
                valid_from TIMESTAMP,           
                valid_to TIMESTAMP,             
                current_flag BOOLEAN,           
                UNIQUE (city_name, region, country, current_flag) 
            );
            """)
            
            logger.info("Updating city_dim with SCD Type 2 logic.")
            cursor.execute("""
            UPDATE city_dim cd
            SET valid_to = NOW(), current_flag = FALSE
            WHERE EXISTS (
                SELECT 1
                FROM staging_weather_data s
                WHERE cd.city_name = s.city_name
                  AND (cd.region != s.region OR cd.country != s.country 
                       OR cd.latitude != s.latitude OR cd.longitude != s.longitude
                       OR cd.tz_id != s.tz_id)
                  AND cd.current_flag = TRUE
            );
            """)
            
            logger.info("Inserting new records for city_dim.")
            cursor.execute("""
            INSERT INTO city_dim (city_name, region, country, latitude, longitude, tz_id, valid_from, valid_to, current_flag)
            SELECT DISTINCT city_name, region, country, latitude, longitude, tz_id, NOW(), '9999-12-31'::TIMESTAMP, TRUE
            FROM staging_weather_data s
            WHERE NOT EXISTS (
                SELECT 1 
                FROM city_dim cd
                WHERE cd.city_name = s.city_name
                  AND cd.current_flag = TRUE
            );
            """)

            conn.commit()
            cursor.close()
            logger.info("Star schema processing complete.")
        except Exception as e:
            logger.error(f"Error in process_staging_to_star_schema: {e}")
            raise

    @task()
    def process_time_dim():
        """Transform staging data into the time_dim with minute-level precision."""
        try:
            logger.info("Processing staging data into time_dim.")
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()

            cursor.execute("""
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
            """)

            logger.info("Inserting data into time_dim.")
            cursor.execute("""
            INSERT INTO time_dim (localtimes, hour, day, month, year, minute, weekday)
            SELECT DISTINCT 
                DATE_TRUNC('minute', localtimes) AS localtimes,
                EXTRACT(HOUR FROM localtimes) AS hour,
                EXTRACT(DAY FROM localtimes) AS day,
                EXTRACT(MONTH FROM localtimes) AS month,
                EXTRACT(YEAR FROM localtimes) AS year,
                EXTRACT(MINUTE FROM localtimes) AS minute,
                EXTRACT(DOW FROM localtimes) AS weekday
            FROM staging_weather_data
            WHERE NOT EXISTS (
                SELECT 1 
                FROM time_dim 
                WHERE time_dim.localtimes = DATE_TRUNC('minute', staging_weather_data.localtimes)
            );
            """)

            conn.commit()
            cursor.close()
            logger.info("time_dim processing complete.")
        except Exception as e:
            logger.error(f"Error in process_time_dim: {e}")
            raise

    @task()
    def process_weather_condition_dim():
        """Transform staging data into the weather_condition_dim."""
        try:
            logger.info("Processing staging data into weather_condition_dim.")
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()    

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_condition_dim (
                condition_id SERIAL PRIMARY KEY,
                condition_text TEXT NOT NULL UNIQUE
            );
            """)
            
            logger.info("Inserting data into weather_condition_dim.")
            cursor.execute("""
            INSERT INTO weather_condition_dim (condition_text)
            SELECT DISTINCT conditions
            FROM staging_weather_data
            WHERE NOT EXISTS (
                SELECT 1 
                FROM weather_condition_dim 
                WHERE (weather_condition_dim.condition_text = staging_weather_data.conditions OR (weather_condition_dim.condition_text IS NULL AND staging_weather_data.conditions IS NULL)) 
            );
            """)

            conn.commit()
            cursor.close()
            logger.info("weather_condition_dim processing complete.")
        except Exception as e:
            logger.error(f"Error in process_weather_condition_dim: {e}")
            raise

    @task()
    def process_weather_fact():
        """Transform staging data into the weather_fact."""
        try:
            logger.info("Processing staging data into weather_fact.")
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()    

            cursor.execute("""
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
            """)
            
            logger.info("Inserting data into weather_fact.")
            cursor.execute("""
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
            JOIN time_dim td ON DATE_TRUNC('minute', s.localtimes) = td.localtimes
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
            """)

            conn.commit()
            cursor.close()
            logger.info("weather_fact processing complete.")
        except Exception as e:
            logger.error(f"Error in process_weather_fact: {e}")
            raise

    # Define task dependencies for sequential execution
    process_staging_to_star_schema() >> process_time_dim() >> process_weather_condition_dim() >> process_weather_fact()




