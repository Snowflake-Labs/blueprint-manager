### Overview

A Warehouse in Snowflake is a cluster of compute resources that executes your queries, data loading, and data manipulation tasks. A key principle of Snowflake architecture is the separation of storage and compute, which means you can size and scale your warehouses independently of your data volume. A proper warehouse strategy is key to optimizing both performance and cost.

### Decisions to Make
* **Naming Convention:** Adopt a standardized naming pattern for all warehouses to clearly identify their function.
  * **Pattern:** `{DATA_PRODUCT}_{PURPOSE}_WH`
  * **`{DATA_PRODUCT}`:** The name of the Data Product the warehouse serves (e.g., `SALESFORCE`).
  * **`{PURPOSE}`:** The type of workload the warehouse is intended for (e.g., `INGEST`, `TRANSFORM`, `REPORTING`).
  * **Example:** `SALESFORCE_TRANSFORM_WH`
* **Warehouse Size:** Choose the appropriate "T-shirt" size for your warehouse (XSMALL, SMALL, MEDIUM, etc.). The size determines the amount of compute resources per cluster.
* **Auto Suspend:** Set the number of seconds of inactivity after which the warehouse will automatically suspend, stopping credit consumption.
* **Auto Resume:** Decide if the warehouse should automatically resume when a new query is submitted to it.
* **Scaling Policy:** For multi-cluster warehouses, choose STANDARD (minimizes queuing by starting new clusters quickly) or ECONOMY (conserves credits by waiting longer to start new clusters).
* **Min/Max Cluster Count:** For multi-cluster warehouses, define the minimum and maximum number of clusters that can run concurrently.

### Personas to Involve
* **Platform Owner:** Implements the warehouse configurations.
* **FinOps Lead:** Provides guidance on budget and cost optimization.
* **Data Product Owner:** Helps forecast the expected workload and performance requirements.

### Best Practices & Recommendations
* **Start Small:** It's a common best practice to start with a smaller warehouse size (like `X-SMALL`) and scale up only if performance is not adequate. Doubling the size doubles the compute power and credits consumed per hour.
* **Workload Isolation:** Create separate warehouses for different workload types (`INGEST`, `TRANSFORM`, `REPORTING`) to prevent them from competing for resources.
* **Sensible Auto-Suspend:** Set `AUTO_SUSPEND` to a low value (e.g., 60 seconds) to avoid paying for idle compute time.
* **Enable Auto-Resume:** Always set `AUTO_RESUME` to `TRUE` for user-facing warehouses to ensure a seamless experience.
* **Tagging:** Apply tags for `{DATA_PRODUCT}` and `{PURPOSE}` to each warehouse to facilitate cost allocation and FinOps reporting.

### Configuration Questions

#### Please provide the list of data products you’d like to use for your database naming. (`dataproduct_list`: list)
The **Data Product** is the required core component that identifies a logical grouping of data. It ensures that every database can be clearly tied to a specific business initiative or dataset. A single Data Product (e.g., `PAYROLL`) could consist of databases across multiple accounts and environments, all linked by this common name. 

### Guidance:
* This part of the name must always be provided. 
* Think of a data product as a distinct dataset or business initiative, such as 'payroll', 'sap', or 'jdoe_sandbox'. 
* Enter one or more data products that will logically group your data. 

#### Please provide the list of purposes you’d like to use for your warehouse naming. (`warehouse_purpose_list`: list)
The **Warehouse Purpose** defines the specific type of workload a virtual warehouse is designed to support. Clearly identifying a warehouse's purpose is a critical best practice for performance management. It allows you to isolate different workloads (e.g., data loading vs. BI reporting) so they don't compete for resources. This ensures, for example, that a large, ad-hoc analytical query doesn't slow down a time-sensitive data ingestion pipeline.

### Guidance:
* This component helps you create a logical, role-based set of warehouses.
* Consider the different types of compute tasks you'll need, from data ingestion to BI and ad-hoc analysis.
* Common purposes include:
  * **INGEST:** For warehouses dedicated to loading raw data into the platform.
  * **TRANSFORM:** For running dbt, ELT/ETL, and other data transformation jobs.
  * **REPORT:** For warehouses serving known, predictable queries from BI dashboards (e.g., Tableau, Power BI).
  * **ADHOC:** For users and data scientists running unpredictable, exploratory queries that should not impact production reporting.
  * **ANALYTICS:** A general-purpose warehouse for analytical queries that may be heavier than standard reporting.
