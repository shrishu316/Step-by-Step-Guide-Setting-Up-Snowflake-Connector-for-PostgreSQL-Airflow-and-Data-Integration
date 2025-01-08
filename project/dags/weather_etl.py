from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task, task_group
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import timedelta

# Configuration
CITIES = ['Tallinn', 'London', 'New York', 'Tokyo', 'New Delhi']
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'weatherapi'
API_KEY = Variable.get('WEATHER_API_KEY')

logger = LoggingMixin().log

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 3,
    'retry_delay': timedelta(seconds=10),
}
#'*/5 * * * *'
# DAG definition
with DAG(
    dag_id='weather_etl',
    default_args=default_args,
    schedule_interval='@hourly',
    catchup=False,
) as dag:

    @task(retries=3, retry_delay=timedelta(seconds=10))
    def extract_weather_data(city: str):
        """Extract weather data for a specific city from weather API."""
        try:
            logger.info(f"Starting extraction for city: {city}")
            http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')

            # Build API Endpoint
            endpoint = f'/v1/current.json?key={API_KEY}&q={city}&aqi=yes'
            response = http_hook.run(endpoint)

            if response.status_code == 200:
                logger.info(f"Successfully fetched weather data for {city}.")
                return response.json()
            else:
                logger.error(f"API call failed for {city} with status code: {response.status_code}")
                raise Exception(f"Failed to fetch weather data for {city}: {response.status_code}")
        except Exception as e:
            logger.error(f"Error in extract_weather_data for {city}: {e}")
            raise

    @task()
    def transform_weather_data(weather_data: dict) -> dict:
        """Transform the extracted weather data."""
        try:
            logger.info(f"Transforming weather data for city: {weather_data['location']['name']}")
            location_data = weather_data['location']
            current_weather = weather_data['current']

            # Use .get() to safely handle missing keys
            air_quality = current_weather.get('air_quality', {})
            transformed_data = {
                'city_name': location_data['name'],
                'region': location_data['region'],
                'country': location_data['country'],
                'latitude': location_data['lat'],
                'longitude': location_data['lon'],
                'tz_id': location_data['tz_id'],
                'localtimes': location_data['localtime'],
                'temperature_celsius': current_weather['temp_c'],
                'temperature_fahrenheit': current_weather['temp_f'],
                'conditions': current_weather['condition']['text'],
                'wind_speed_kph': current_weather['wind_kph'],
                'humidity': current_weather['humidity'],
                'precipitation_mm': current_weather['precip_mm'],
                'visibility_km': current_weather['vis_km'],
                'air_quality_co': air_quality.get('co', None),  # Default to None if 'co' is missing
                'air_quality_o3': air_quality.get('o3', None),  # Default to None if 'o3' is missing
                'air_quality_us_epa': air_quality.get('us-epa-index', None),  # Default to None if 'us-epa-index' is missing
            }

            logger.info(f"Weather data transformed successfully for city: {transformed_data['city_name']}")
            return transformed_data
        except KeyError as e:
            logger.error(f"Missing expected key in weather data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in transform_weather_data: {e}")
            raise

    @task()
    def load_to_staging(transformed_data: dict):
        """Load transformed data into staging tables."""
        try:
            logger.info(f"Loading weather data into staging for city: {transformed_data['city_name']}.")
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()

            # Create staging table if not exists with NOT NULL constraints
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS staging_weather_data (
                city_name TEXT NOT NULL,
                region TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude FLOAT,
                longitude FLOAT,
                tz_id TEXT,
                localtimes TIMESTAMP NOT NULL,
                temperature_celsius FLOAT,
                temperature_fahrenheit FLOAT,
                conditions TEXT,
                wind_speed_kph FLOAT,
                humidity INT,
                precipitation_mm FLOAT,
                visibility_km FLOAT,
                air_quality_co FLOAT,
                air_quality_o3 FLOAT,
                air_quality_us_epa INT,
                processed_at TIMESTAMP DEFAULT NOW()
            );
            """)

            # Add a unique index for deduplication
            cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes WHERE indexname = 'idx_staging_weather_data_unique'
                ) THEN
                    CREATE UNIQUE INDEX idx_staging_weather_data_unique 
                    ON staging_weather_data (city_name, region, country, localtimes);
                END IF;
            END $$;
            """)

            # Set the unique index as the replica identity
            cursor.execute("""
            ALTER TABLE staging_weather_data 
            REPLICA IDENTITY USING INDEX idx_staging_weather_data_unique;
            """)

            # Insert data into the staging table
            cursor.execute("""
            INSERT INTO staging_weather_data (
                city_name, region, country, latitude, longitude, tz_id, localtimes,
                temperature_celsius, temperature_fahrenheit, conditions, wind_speed_kph,
                humidity, precipitation_mm, visibility_km, air_quality_co,
                air_quality_o3, air_quality_us_epa
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (city_name, region, country, localtimes) DO NOTHING;
            """, (
                transformed_data['city_name'], transformed_data['region'], transformed_data['country'],
                transformed_data['latitude'], transformed_data['longitude'], transformed_data['tz_id'],
                transformed_data['localtimes'], transformed_data['temperature_celsius'], 
                transformed_data['temperature_fahrenheit'], transformed_data['conditions'], 
                transformed_data['wind_speed_kph'], transformed_data['humidity'], 
                transformed_data['precipitation_mm'], transformed_data['visibility_km'], 
                transformed_data['air_quality_co'], transformed_data['air_quality_o3'], 
                transformed_data['air_quality_us_epa']
            ))

            conn.commit()
            cursor.close()
            logger.info(f"Data successfully loaded into staging for city {transformed_data['city_name']}.")
        except Exception as e:
            logger.error(f"Error in load_to_staging: {e}")
            raise

    @task_group
    def process_city_data(city: str):
        """Group tasks for processing weather data for a specific city."""
        logger.info(f"Processing data for city: {city}")
        weather_data = extract_weather_data(city=city)
        transformed_data = transform_weather_data(weather_data)
        load_to_staging(transformed_data)

    # Execute city data processing tasks concurrently for each city
    for city in CITIES:
        process_city_data(city)
