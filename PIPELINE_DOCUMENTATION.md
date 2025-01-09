# Robust Data Processing Solution

## Objective

This project demonstrates the design and implementation of a robust data processing pipeline that integrates operational and analytical databases, replicates data efficiently, applies transformations, and monitors the entire process. The solution leverages PostgreSQL, Snowflake, and Apache Airflow, ensuring scalability, security, cost-effectiveness, and extensibility. 

The pipeline minimizes the use of cloud services like AWS, GCP, and Azure, offering a robust solution that can be deployed on-premises.

---

## Table of Contents

1. [Why This Design?](#why-this-design)
2. [How Does the Pipeline Work?](#how-does-the-pipeline-work)
3. [Key Features](#key-features)
4. [Why is This Pipeline Better?](#why-is-this-pipeline-better)
5. [Installation and Setup](#installation-and-setup)
6. [Conclusion](#conclusion)

---

## Why This Design?

This design ensures the following:

- **Ease of Integration**: Seamless connection between PostgreSQL (OLTP) and Snowflake (OLAP) using the Snowflake Connector for PostgreSQL.
- **Scalability**: Snowflake handles large-scale analytics with minimal configuration.
- **Automation**: Apache Airflow automates the ETL processes via Directed Acyclic Graphs (DAGs).
- **Minimal Cloud Dependency**: The Snowflake-to-PostgreSQL connector minimizes reliance on external cloud platforms such as AWS, GCP, or Azure, providing flexibility in on-premises deployments.

---

## How Does the Pipeline Work?

### 1. **Operational Database Setup**

- **PostgreSQL** is used as the OLTP database, storing real-time weather data fetched from a Weather API.
- Python scripts periodically update the database to ensure fresh and consistent data.

### 2. **Connecting PostgreSQL to Snowflake**

- The **Snowflake Connector for PostgreSQL** facilitates the secure and efficient replication of data from PostgreSQL to Snowflake.
- **RSA key-based authentication** ensures secure communication, while Snowflake’s scheduling features enable controlled data updates.

### 3. **Data Replication**

- Batch processing replicates data from PostgreSQL to Snowflake using the Snowflake Connector.
- Data replication processes are monitored for success or failure using **Airflow DAGs** and Snowflake's monitoring tools.

### 4. **Data Transformation**

- Raw data in Snowflake is transformed into analytical models:
  - **Fact Table**: `weather_fact`
  - **Dimension Tables**: `city_dim`, `time_dim`, `weather_condition_dim`
- SQL logic resolves challenges like **deduplication** and **null value handling** to ensure data integrity.

### 5. **Monitoring and Query Tracking**

- Query execution and replication statuses are tracked using **Snowflake’s History tab** and system views like `SNOWFLAKE.ACCOUNT_USAGE`.
- **Airflow's monitoring tools** provide visibility into ETL workflows and failures.

---

## Key Features

- **Seamless Integration**: Snowflake Connector for PostgreSQL facilitates smooth, secure data replication.
- **Scalable Architecture**: Leverages Snowflake’s computing resources for handling increasing data volumes.
- **Automated Workflows**: Airflow automates data extraction, transformation, and loading tasks.
- **Query Monitoring**: Track and optimize queries in real-time with Snowflake’s history and profiling tools.
- **Resilient Design**: Handles deduplication, null values, and other common data challenges.
- **Replicable Environment**: Docker containers ensure consistent setup and deployment.
- **Minimal Cloud Dependency**: Reduces reliance on cloud services, making the solution ideal for on-premises deployment.

---

## Why is This Pipeline Better?

- **Secure and Efficient Data Movement**: Ensures secure replication with RSA key-based authentication and reliable scheduling mechanisms.
- **Optimized Workload Distribution**: PostgreSQL is ideal for OLTP tasks, while Snowflake efficiently handles OLAP workloads.
- **Cost-Effective**: Snowflake's pay-as-you-go pricing ensures scalability without unnecessary costs.
- **Modular and Flexible**: The architecture allows easy integration of new data sources and transformations.
- **Proactive Monitoring**: Airflow and Snowflake provide comprehensive monitoring to ensure pipeline health and performance.
- **Reduced Cloud Services Dependency**: Minimizes reliance on cloud providers (AWS, GCP, Azure) while providing an effective on-premises solution.

---

## Prerequisites

- **PostgreSQL** (version 12+)
- **Snowflake** account
- **Apache Airflow** (version 2+)
- **Docker** (optional, for containerized setup)
- **Python** (3.8+)

## Conclusion

This data pipeline integrates **PostgreSQL**, **Snowflake**, the **Snowflake Connector**, and **Apache Airflow** to provide a scalable, secure, and efficient solution for both real-time and batch data processing needs. By minimizing the use of cloud services, this solution is ideal for organizations seeking cost-effective, flexible, and robust data processing systems with an on-premises deployment option.

The architecture’s modularity and built-in monitoring tools ensure that it is future-proof and scalable for a wide range of use cases, from small-scale to enterprise-level applications.

---
