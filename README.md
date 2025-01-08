# Step-by-Step-Guide-Setting-Up-Snowflake-Connector-for-PostgreSQL-Airflow-and-Data-Integration




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
![Screenshot from 2025-01-08 15-52-18](https://github.com/user-attachments/assets/aae25988-1574-44c3-b9a4-536c099042ce)

![Screenshot from 2025-01-08 15-53-52](https://github.com/user-attachments/assets/2a19582a-2c31-4fdb-96c1-11790a023d86)


### 1.2 **Run Airflow in the Terminal**:  

```bash
docker-compose up -d
```

### 1.3 **Access Airflow UI**:  
- Go to [http://0.0.0.0:8080/](http://0.0.0.0:8080/).  
- Log in with the credentials created in step 1.1.
![Screenshot from 2025-01-08 17-25-58](https://github.com/user-attachments/assets/1a7c5328-8a9a-40f9-993d-282e683fe5b5)

### 1.4 **Add API Key**:  
- Sign up at [WeatherAPI](https://www.weatherapi.com/my/) to get your API key.
![Screenshot from 2025-01-08 17-01-21](https://github.com/user-attachments/assets/ffee9a9a-cdf3-4180-99eb-4d6c15f1988e)

- Go to **Admin > Variables** in the Airflow UI:
![Screenshot from 2025-01-08 16-55-10](https://github.com/user-attachments/assets/dfaa6bc2-ab44-42da-9ec0-7d37e0e45896)  
  - Add a record with **Key**: `WEATHER_API_KEY` and **Value**: Your API Key.
  ![Screenshot from 2025-01-08 16-57-25](https://github.com/user-attachments/assets/d3704e23-5570-4ebd-a27c-ab9ef379fa0f)



### 1.5 **Configure PostgreSQL in Airflow**:  
- Go to **Admin > Connections** and edit `postgres_default`:
![Screenshot from 2025-01-08 17-09-43](https://github.com/user-attachments/assets/98136758-854e-4339-bece-4348d633c677)

  - Change the database name to `postgres`.
  ![Screenshot from 2025-01-08 17-12-20](https://github.com/user-attachments/assets/90322751-dd48-4137-b588-a676f000f0f7)


### 1.6 **Add Weather API Connection**:  
- Add a new record in **Connections**:
![Screenshot from 2025-01-08 17-15-03](https://github.com/user-attachments/assets/2331f5b6-391e-4360-b1f5-91e6b5dd676d)
  - **Connection ID**: `weatherapi`  
  - **Connection Type**: HTTP  
  - **Host**: `http://api.weatherapi.com`  
  - **Login**: Your email  
  - **Password**: Your Weather API password
  ![Screenshot from 2025-01-08 17-17-37](https://github.com/user-attachments/assets/27d55e65-df7f-4a66-99ec-4ad628520ab4)
  

---

## **2. Run and Test Workflows in Airflow**
1. **Trigger DAGs**:
![Screenshot from 2025-01-08 17-25-58](https://github.com/user-attachments/assets/cd4a76d0-2e06-43b3-b5bc-352f8f7515e0)
   - Explore the DAGs, logs, and errors in the Airflow UI.
   ![Screenshot from 2025-01-08 17-28-07](https://github.com/user-attachments/assets/d30e865a-564e-498b-b775-aac2e6e82e7c)
   - Trigger the **weather_etl** DAG to load weather data into PostgreSQL.
   ![Screenshot from 2025-01-08 17-29-04](https://github.com/user-attachments/assets/3d288b1c-c020-4fe9-8472-6ab312491594)

3. **Monitor Data**:  
   - Check the `staging_weather_data` table in PostgreSQL.
   ![Screenshot from 2025-01-08 17-38-05](https://github.com/user-attachments/assets/3bfc459d-6479-43b6-9707-04bd34d666c9)

   - Trigger the **loading** DAG to transform data into:  
     - `city_dim`  
     - `time_dim`  
     - `weather_condition_dim`  
     - `weather_fact`
     ![Screenshot from 2025-01-08 17-37-14](https://github.com/user-attachments/assets/4be2bac8-c30d-4007-bdcb-8e1d1c0c0f28)
     

---

## **3. Set Up PostgreSQL Connection**

### **Open pgAdmin**:  
1. **Register a server with the following details**:
    ![Screenshot from 2025-01-08 14-37-09](https://github.com/user-attachments/assets/319faa06-8a0d-4efe-b060-fe54ea8a1e52)
  -Note Postgres container IP address 
    - **Name**: PostgreSQL Server  
    - **Connection Tab**:  
        - **Host**: (Postgres container IP address)  
        - **Username**: `postgres`  
        - **Password**: `postgres`  
        - **Database**: `postgres`  
        - **Schema**: `public`  
        - **Port**: `5432`
        ![Screenshot from 2025-01-08 15-21-03](https://github.com/user-attachments/assets/a9e083dc-2d09-4ac0-be31-e3d19bad1cf8)
        ![Screenshot from 2025-01-08 14-38-23](https://github.com/user-attachments/assets/db9f59e2-aabb-497e-883e-c643d0151c8a)
        ![Screenshot from 2025-01-08 14-45-43](https://github.com/user-attachments/assets/e50dc9e2-d159-48b3-abff-7eca41725bad)
      

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
   ![Screenshot from 2025-01-08 21-12-49](https://github.com/user-attachments/assets/c1d29857-f129-424c-9e40-611077ded5bc)
   ![Screenshot from 2025-01-08 21-01-52](https://github.com/user-attachments/assets/d0e79840-d446-4d8e-a5dc-67cbcc6ae203)


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
   ![Screenshot from 2025-01-07 18-14-01](https://github.com/user-attachments/assets/3622033b-aea3-4184-b3e1-1a55660cf5a2)


---

## **5. Configure the Snowflake Connector**
1. **Start Configuration**:  
   - After downloading, click on **Configure**.
   ![Screenshot from 2025-01-07 18-20-35](https://github.com/user-attachments/assets/60666eee-d5a9-431c-8cab-58d6e82d4511)
   ![Screenshot from 2025-01-07 18-24-42](https://github.com/user-attachments/assets/44a7ce92-86a4-4d4c-ab28-60d214b2e7da)
   - Leave the given name as is and proceed by clicking **Configure** again.
   ![Screenshot from 2025-01-07 18-25-55](https://github.com/user-attachments/assets/e0fd9e8d-65ea-4c24-b93d-59c3e5af4377)


2. **Generate Configuration File**:  
   - After configuration, click on **Generate File**.
   ![Screenshot from 2025-01-07 18-26-17](https://github.com/user-attachments/assets/15a88475-76a2-48b4-9f41-a90c8e3a8c62)  
   - Download the **snowflake.json** file.
   - Do not close this tab leave it as it is you have to come back to this tab.

3. **Move Configuration File**:  
   - Move the downloaded `snowflake.json` file to the folder named **configuration**.
   ![Screenshot from 2025-01-07 19-03-10](https://github.com/user-attachments/assets/cbc8424e-edb0-4d90-b5c1-725993cc27db)

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
   ![Screenshot from 2025-01-07 19-02-47](https://github.com/user-attachments/assets/e3a59241-850e-41cb-a391-5ad328823f52)

---

## **7. Update Snowflake with the RSA Public Key**
1. **Go to Snowflake and open another Snowflake tab**:  
   - Navigate to **SNOWFLAKE_CONNECTOR_FOR_POSTGRESQL**.
   ![Screenshot from 2025-01-07 19-14-06](https://github.com/user-attachments/assets/6d0596b2-84fa-4db8-acd9-6f1f57f3a53b)

2. **Run the Following Query**:  
   Replace the `<PUBLIC_KEY>` below with your copied key:  

   ```sql
   ALTER USER SNOWFLAKE_CONNECTOR_FOR_POSTGRESQL_AGENT_USER SET RSA_PUBLIC_KEY='<PUBLIC_KEY>';
   ```
![Screenshot from 2025-01-07 19-16-12](https://github.com/user-attachments/assets/fefd90ac-268c-4cfb-b1ae-aa2991dce504)
---

## **8. Sync Data Between Snowflake and PostgreSQL**
1. **Restart Containers**:  
   - Run the following commands:  

     ```bash
     docker-compose down
     docker-compose up -d
     ```

2. **Refresh Snowflake**:  
   - Go to Snowflake Configure page.
   ![Screenshot from 2025-01-07 18-26-17](https://github.com/user-attachments/assets/14646660-2249-4e0d-8888-2f2b96aa5230)
   - Click on refresh and wait for while.
   ![Screenshot from 2025-01-07 19-19-04](https://github.com/user-attachments/assets/75fdd3bc-f931-4cb6-895d-12e8fb8add6d) 
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
     ![Screenshot from 2025-01-07 17-11-07](https://github.com/user-attachments/assets/44f7d65d-4e6b-4844-a49a-9fafda542d27)
     ![Screenshot from 2025-01-07 17-12-35](https://github.com/user-attachments/assets/1c273922-0f3e-4291-98ef-48846b65ec2e)

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
