This step queries actual database storage to establish the data volume baseline for cost calculations.

## Why is this important?

- Total replicable storage is the single most important input to all cost formulas — every estimate in step 5.3 is derived from it
- Categorizing databases (standard vs. imported vs. app package) prevents accidentally including non-replicable databases in the cost estimate
- Identifying the largest databases helps prioritize which ones to include in the failover group vs. leave out for a lower-cost partial DR strategy
- On new accounts with no `ACCOUNT_USAGE` data, this query still returns current storage — it's always meaningful

## Prerequisites

- ACCOUNTADMIN role access
- Access to `SNOWFLAKE.ACCOUNT_USAGE` views (requires IMPORTED PRIVILEGES on SNOWFLAKE database)
- Cost parameters collected (step 5.1)

## Key Concepts

- **Replicable Storage**: Only standard databases can be replicated. Imported databases (from shares), application packages, and system databases are excluded.
- **Database Categorization**: Each database is classified as standard (replicable), imported (not replicable), app package/app, or system.
- **Failsafe Storage**: Additional storage that is part of the total footprint but does not significantly impact replication costs.

## What Gets Measured

| Metric | Purpose |
|--------|---------|
| Storage per database | Identify largest databases for cost allocation |
| Total replicable storage | Base figure for all cost calculations |
| Database categories | Determine what can vs. cannot be replicated |
| Failsafe storage | Complete picture of storage footprint |

**More Information:**
* [DATABASE_STORAGE_USAGE_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/database_storage_usage_history) — Storage metrics reference
* [Replication Cost](https://docs.snowflake.com/en/user-guide/account-replication-cost) — How storage drives replication costs


### Configuration Questions

#### Which databases should be included in the failover group? (`dr_databases`: list)
**What is this asking?**
List the databases to include in the failover group. Only standard databases
can be replicated — imported databases (from shares), system databases, and
application packages are excluded automatically.

**Format:**
Enter each database name on a separate line.

**Examples:**
```
ANALYTICS_DB
SALES_DB
CUSTOMER_DB
WAREHOUSE_DB
```

**Note:** If you want ALL standard databases, leave this list empty and the
blueprint will include all eligible databases.

