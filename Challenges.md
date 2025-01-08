
---

## **1. Challenges**

### **1.1. Handling Row Duplication in PostgreSQL**
- **Challenge**: When processing and loading data, using the `localtimes` column as a unique identifier caused duplications due to differences in milliseconds. This occurred because the high granularity of milliseconds introduced minor discrepancies during the ETL process.
- **Solution**: To address this, the granularity was reduced by truncating the `localtimes` column to minutes using the following SQL command:  
  ```sql
  DATE_TRUNC('minute', localtimes) AS localtimes
  ```

### **1.2. Ensuring Data Uniqueness in Facts Table**
- **Challenge**: While automating the creation of the facts table, using the `DISTINCT` command did not remove duplicates for records containing `NULL` values. This resulted in redundant rows in the facts table.
- **Solution**: A conditional logic was added to ensure equivalence between `NULL` values in the query. The following condition was used:  
  ```sql
  (wf.air_quality_us_epa = s.air_quality_us_epa OR (wf.air_quality_us_epa IS NULL AND s.air_quality_us_epa IS NULL))
  ```

### **1.3. Key Generation for PostgreSQL to Snowflake Connection**
- **Challenge**: When connecting PostgreSQL to Snowflake using the PostgreSQL-agent, the `snowflake.json` file should have been created automatically to extract public and private keys into the `agent-key` folder. However, this process failed, preventing secure communication.
- **Solution**: The keys were manually generated using the following commands:
  ```bash
  openssl genrsa -out ./agent-keys/database-connector-agent-app-private-key.p8 2048
  chmod 600 ./agent-keys/database-connector-agent-app-private-key.p8
  openssl rsa -in ./agent-keys/database-connector-agent-app-private-key.p8 -pubout -out ./agent-keys/database-connector-agent-app-public-key.pem
  ```
  Additionally, read-only permissions were configured in the `docker-compose.yaml` file to ensure security.

### **1.4. Securing Airflow with Fernet Encryption**
- **Challenge**: Airflow required a secure way to store sensitive information, such as passwords and keys, using encryption.
- **Solution**: A Fernet key was generated and configured in the `airflow.cfg` file to enable encryption. The key was created using the following Python code:
  ```python
  from cryptography.fernet import Fernet

  # Generate a Fernet key
  fernet_key = Fernet.generate_key()

  # Print the key
  print(fernet_key.decode())  # Decode to get a string format
  ```
  This key was saved in the `airflow.cfg` file under the `[core]` section as `fernet_key`.

---

