This step validates that data and functionality are intact on the newly promoted primary account. Confirms reads, optional writes, warehouse availability, and governance policy status.

## Why is this important?

- Promotion success does not guarantee data integrity — validation confirms replication did not drop or corrupt data
- Warehouses replicate in suspended state and must be explicitly resumed before workloads can run
- Masking and row access policies must be verified — a failover that silently drops governance controls is a compliance regression
- Warehouse sizing should be confirmed before resuming production workloads, as the target account may have different resource characteristics
- This step's results feed directly into the RTO/RPO measurements recorded in step 3.4

## Prerequisites

- ACCOUNTADMIN role access on the **target account** (now primary)
- Failover (promotion) complete in step 3.2

## Key Concepts

- **Data Validation**: Query critical tables to confirm row counts and data freshness match expectations.
- **Write Test**: Optionally test that writes succeed on the new primary (confirms promotion was successful).
- **Warehouse Resume**: Warehouses replicate in suspended state and must be manually resumed for use.

## What Gets Validated

| Check | Purpose |
|-------|---------|
| Read queries | Confirm data is accessible and queryable |
| Data freshness | Check timestamps on critical tables |
| Write test | Verify the new primary accepts writes |
| Warehouses | Confirm compute resources can be resumed |
| Governance policies | Confirm masking and row access policies are active |

## Warehouse Sizing Before Routing Production Traffic

Warehouses replicate in `SUSPENDED` state at the size they had on the source account. Before resuming warehouses and routing production workloads to the new primary, verify that the sizes are appropriate for the expected demand:

```sql
-- Review replicated warehouse configurations on the new primary
SHOW WAREHOUSES;

-- Resize if needed before resuming at production scale
-- ALTER WAREHOUSE <warehouse_name> SET WAREHOUSE_SIZE = <size>;

-- Then resume
-- ALTER WAREHOUSE <warehouse_name> RESUME;
```

A warehouse that was sized for steady-state production on the source may need to be larger temporarily on the target if it's handling catch-up workloads or if the target account has different resource contention characteristics. Right-size before resuming rather than after, to avoid cold-start performance surprises.

**More Information:**
* [ALTER FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/alter-failover-group) — Post-failover operations
* [POLICY_REFERENCES](https://docs.snowflake.com/en/sql-reference/account-usage/policy_references) — Verify policy attachments post-failover


### Configuration Questions

#### What name suffix should be used for failover group objects? (`dr_failover_group_name`: text)
**What is this asking?**
Provide a name for the failover group and related objects. This will be used
as the identifier for the failover group, connection objects, etc.

**Connection naming:** This value also determines the client redirect connection
name: `{name}_CONN`. For example, `PROD_DR` produces a connection named
`PROD_DR_CONN`. Choose a name that is meaningful in both the failover group
and connection string contexts — your application teams will reference the
connection URL by this name.

**Naming Guidelines:**
- Use uppercase letters, numbers, and underscores
- Keep it short but descriptive
- Common patterns: `DR`, `PROD_DR`, `CRITICAL_DR`

**Examples:**
- `DR` — Simple, for a single failover group (connection: `DR_CONN`)
- `PROD_DR` — For production tier (connection: `PROD_DR_CONN`)
- `CRITICAL_DR` — For critical-tier databases with tight RPO (connection: `CRITICAL_DR_CONN`)


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

