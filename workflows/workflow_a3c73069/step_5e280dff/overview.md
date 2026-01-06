### Overview
A Resource Monitor is a crucial FinOps control that helps you manage and prevent unintended credit usage by your warehouses. You can set spending quotas for a group of warehouses over a specific time interval and define actions to be taken when consumption reaches certain thresholds.

### Decisions to Make
* **Naming Convention and Granularity:** Decide on the scope of your resource monitors. This choice affects both the naming pattern and the level of control you have over costs.
  * **Option 1: Monitor by Data Product (Simpler):** This approach provides a single budget for all warehouses associated with a Data Product.
    * **Pattern:** `{DATA_PRODUCT}_MONITOR`
    * **Example:** `SALESFORCE_MONITOR`
  * **Option 2: Monitor by Data Product and Purpose (More Specific):** This allows for more granular control, letting you set different quotas and triggers for different types of workloads (e.g., a tighter budget for predictable `INGEST` jobs vs. a more flexible one for ad-hoc `REPORTING`).
    * **Pattern:** `{DATA_PRODUCT}_{PURPOSE}_MONITOR`
    * **Example:** `SALESFORCE_TRANSFORM_MONITOR`
* **Credit Quota:** Define the total number of Snowflake credits that can be consumed by the assigned warehouses before the monitor takes action.
* **Frequency:** Set the interval at which the used credits reset to zero (`DAILY`, `WEEKLY`, `MONTHLY`).
* **Triggers:** Define one or more thresholds and the action to take when that percentage of the credit quota is reached.
  * **Actions:** `NOTIFY`, `SUSPEND` (waits for queries to finish), `SUSPEND_IMMEDIATE` (cancels running queries).
  * **Example:** Trigger a `NOTIFY` action at 80% of the quota and a `SUSPEND` action at 100%.
* **Notify Users:** Specify the users who should receive an email notification when a trigger threshold is reached.

### Personas to Involve
* **Platform Owner:** Creates and assigns the resource monitors.
* **FinOps Lead:** Sets the budget and credit quotas.
* **Data Product Owner:** Should be notified of consumption patterns and potential overages.

### Best Practices & Recommendations
* **Monitor per Data Product:** Create at least one resource monitor for each Data Product and assign all of its associated warehouses to it. This allows you to manage the budget at the Data Product level.
* **Use Multiple Triggers:** Always set up at least two triggers: a `NOTIFY` trigger as an early warning (e.g., at 75-80%) and a `SUSPEND` or `SUSPEND_IMMEDIATE` trigger at 100% to act as a hard stop and prevent budget overruns.
* **Choose the Right Frequency:** For new or unpredictable workloads, a `WEEKLY` frequency allows for closer monitoring. For stable, production workloads, a `MONTHLY` frequency often aligns better with budgeting cycles.

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

#### How granularly would you like to control your compute budgets? (`resource_monitor_strategy`: multi-select)
This decision defines your strategy for monitoring credit consumption and enforcing budgets. You can choose a simple approach by setting one budget for an entire **Data Product**, or a more granular approach by setting specific, separate budgets for each **Warehouse Purpose** (e.g., Ingest, Transform, Report) within that Data Product.

### Guidance:
* **Monitor per Data Product (Recommended Starting Point)**
  * **What it is:** You create one Resource Monitor (e.g., `SALESFORCE_RM`) and assign it a total monthly quota. All warehouses associated with that Data Product (`SALESFORCE_INGEST_WH`, `SALESFORCE_TRANSFORM_WH`, `SALESFORCE_REPORT_WH`, etc.) will draw from this single, shared credit pool.
  * **Pros:** Simplest to manage and aligns directly with a single Data Product budget.
  * **Cons:** A single runaway workload (e.g., a bad ad-hoc query) could consume the entire budget, potentially blocking other critical workloads like data ingestion.
* **Monitor per Data Product + Warehouse Purpose (Granular Control)**
  * **What it is:** You create multiple, specific Resource Monitors (e.g., `SALESFORCE_INGEST_RM`, `SALESFORCE_TRANSFORM_RM`, `SALESFORCE_REPORT_RM`), each with its own separate credit quota.
  * **Pros:** Provides maximum budget control and workload isolation. You can guarantee that your `INGEST` budget is protected and will never be consumed by `REPORT` or `ADHOC` workloads.
  * **Cons:** More complex to set up and manage, as it creates a much larger number of monitors. This is best for mature organizations with very specific workload budgeting requirements.
**Options:**
- Simple
- Granular
