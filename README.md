# Step-by-Step-Guide-Setting-Up-Snowflake-Connector-for-PostgreSQL-Airflow-and-Data-Integration

Sure! Below is the complete `README.md` file that includes all the points from 1 to 8:

```markdown
# **Step-by-Step Guide: Setting Up Snowflake Connector for PostgreSQL, Airflow, and Data Integration**

---

## **1. Set Up Apache Airflow**

### 1.1 **Access Airflow Instructions**:  
- Locate the `How_to_sign_in_airflow.txt` file in your folder.  
- Run the following command to create an Airflow admin user:  

  ```bash
  sudo docker-compose exec airflow-webserver airflow users create \
      --username airflow \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com \
      --password airflow
  ```

### 1.2 **Run Airflow in the Terminal**:  

```bash
docker-compose up -d
```

### 1.3 **Access Airflow UI**:  
- Go to [http://0.0.0.0:8080/](http://0.0.0.0:8080/).  
- Log in with the credentials created in step 1.1.

### 1.4 **Add API Key**:  
- Sign up at [WeatherAPI](https://www.weatherapi.com/my/) to get your API key.  
- Go to **Admin > Variables** in the Airflow UI:  
  - Add a record with **Key**: `WEATHER_API_KEY` and **Value**: Your API Key.  

### 1.5 **Configure PostgreSQL in Airflow**:  
- Go to **Admin > Connections** and edit `postgres_default`:  
  - Change the database name to `postgres`.

### 1.6 **Add Weather API Connection**:  
- Add a new record in **Connections**:  
  - **Connection ID**: `weatherapi`  
  - **Connection Type**: HTTP  
  - **Host**: `http://api.weatherapi.com`  
  - **Login**: Your email  
  - **Password**: Your Weather API password  

---

## **2. Run and Test Workflows in Airflow**
1. **Trigger DAGs**:  
   - Explore the DAGs, logs, and errors in the Airflow UI.  
   - Trigger the **weather_etl** DAG to load weather data into PostgreSQL.  

2. **Monitor Data**:  
   - Check the `staging_weather_data` table in PostgreSQL.  
   - Trigger the **loading** DAG to transform data into:  
     - `city_dim`  
     - `time_dim`  
     - `weather_condition_dim`  
     - `weather_fact`  

---

## **3. Set Up PostgreSQL Connection**

### **Open pgAdmin**:  
1. **Register a server with the following details**:  
    - **Name**: PostgreSQL Server  
    - **Connection Tab**:  
        - **Host**: (Postgres container IP address)  
        - **Username**: `postgres`  
        - **Password**: `postgres`  
        - **Database**: `postgres`  
        - **Schema**: `public`  
        - **Port**: `5432`  

### **Modify PostgreSQL Configuration for Logical Replication**:  
1. **Check Running Docker Containers**:  

   ```bash
   docker ps
   ```

2. **Access the PostgreSQL Container**:  

   ```bash
   docker exec -it airflow-postgres-container bash
   ```

3. **Locate the PostgreSQL Configuration File**:  

   ```bash
   psql -U postgres -c "SHOW config_file;"
   ```

4. **Install Nano Text Editor (if not already installed)**:  

   ```bash
   apt-get update && apt-get install nano
   ```

5. **Edit the `postgresql.conf` File**:  

   ```bash
   nano /var/lib/postgresql/data/postgresql.conf
   ```

6. **Set the `wal_level` Parameter**:  
   - Locate the `wal_level` setting in the file.  
   - Change its value to `logical`:  

     ```bash
     wal_level = logical
     ```

7. **Save and Exit**:  
   - Press `CTRL+O` to save changes, then `CTRL+X` to exit the Nano editor.  

---

## **4. Sign Up and Access Snowflake**
1. **Sign up for Snowflake**:  
   - Use only your email for signup.  
   - You'll receive **$400 credits for a 30-day trial**.

2. **Access the Snowflake Console**:  
   - Open Snowflake and navigate to the left panel.  
   - Click on **DATA PRODUCTS**.

3. **Install Snowflake Connector**:  
   - Search for **Snowflake Connector for PostgreSQL** in the Marketplace or Apps section.  
   - Download the connector.  

---

## **5. Configure the Snowflake Connector**
1. **Start Configuration**:  
   - After downloading, click on **Configure**.  
   - Leave the given name as is and proceed by clicking **Configure** again.  

2. **Generate Configuration File**:  
   - After configuration, click on **Generate File**.  
   - Download the **snowflake.json** file.  

3. **Move Configuration File**:  
   - Move the downloaded `snowflake.json` file to the folder named **configuration**.

---

## **6. Set Up the Environment in the Terminal**
1. **Navigate to the folder** containing the `docker-compose.yml` file.  

2. **Run the Following Commands**:  

   ```bash
   ls ./agent-keys/
   ```

   - This folder should initially be empty.

3. **Generate RSA Keys**:  
   - Generate a private key:  

     ```bash
     openssl genrsa -out ./agent-keys/database-connector-agent-app-private-key.p8 2048
     ```

   - Set file permissions:  

     ```bash
     chmod 600 ./agent-keys/database-connector-agent-app-private-key.p8
     ```

   - Generate a public key:  

     ```bash
     openssl rsa -in ./agent-keys/database-connector-agent-app-private-key.p8 -pubout -out ./agent-keys/database-connector-agent-app-public-key.pem
     ```

4. **Check the Generated Key**:  
   - View the public key:  

     ```bash
     cat ./agent-keys/database-connector-agent-app-public-key.pem
     ```

   - Copy the displayed public key.

---

## **7. Update Snowflake with the RSA Public Key**
1. **Go to Snowflake**:  
   - Navigate to **SNOWFLAKE_CONNECTOR_FOR_POSTGRESQL**.

2. **Run the Following Query**:  
   Replace the `<PUBLIC_KEY>` below with your copied key:  

   ```sql
   ALTER USER SNOWFLAKE_CONNECTOR_FOR_POSTGRESQL_AGENT_USER SET RSA_PUBLIC_KEY='<PUBLIC_KEY>';
   ```

---

## **8. Sync Data Between Snowflake and PostgreSQL**
1. **Restart Containers**:  
   - Run the following commands:  

     ```bash
     docker-compose down
     docker-compose up -d
     ```

2. **Refresh Snowflake**:  
   - Go to Snowflake and refresh the page.  
   - If issues persist, inspect logs using:  

     ```bash
     docker logs -f <container_id>
     ```

3. **Load Data into Snowflake**:  
   - Run the following queries in Snowflake:  

     ```sql
     ALTER SESSION SET AUTOCOMMIT = TRUE;
     USE SCHEMA "SNOWFLAKE_CONNECTOR_FOR_POSTGRESQL".PUBLIC;
     CALL ADD_DATA_SOURCE('PSQLDS1', 'postgres');
     CALL ADD_TABLES('PSQLDS1', 'public', ['weather_condition_dim', 'weather_fact', 'time_dim', 'city_dim']);
     ```

4. **Monitor and Manage Replication**:  
   - Enable scheduled replication every 60 minutes:  

     ```sql
     CALL ENABLE_SCHEDULED_REPLICATION('PSQLDS1', '60 minutes');
     ```

   - Remove or disable replication as needed:  

     ```sql
     CALL REMOVE_TABLE('PSQLDS1', 'public', 'weather_fact');
     CALL DISABLE_SCHEDULED_REPLICATION('PSQLDS1');
     ```

---
