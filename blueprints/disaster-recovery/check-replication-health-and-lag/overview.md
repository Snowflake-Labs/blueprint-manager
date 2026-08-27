This step measures current replication lag and refresh history to determine your effective Recovery Point Objective (RPO).

## Why is this important?

- Replication lag directly determines how much data could be lost during an actual DR event — a 4-hour lag means 4 hours of potential data loss
- Average refresh duration must be less than the replication interval, or refreshes queue up and effective RPO silently degrades
- Understanding current health before implementing changes establishes a meaningful baseline to compare against after Task 2
- This step is only meaningful after Task 2 completes; on a first-run assessment it confirms the starting state (no replication)

## Prerequisites

- ACCOUNTADMIN role access
- Failover group created (Task 2) for health data to be meaningful; on first run, results will be empty — this is expected

## Key Concepts

- **RPO (Recovery Point Objective)**: The maximum acceptable data loss measured in time. Determined by how frequently replication runs and how long each refresh takes.
- **Replication Lag**: The time between the last successful refresh and the current moment.
- **Refresh History**: Historical record of replication operations including duration and bytes transferred.

## What Gets Measured

| Metric | Purpose |
|--------|---------|
| Last successful refresh | When data was last synced |
| Average refresh duration | How long each replication cycle takes |
| Replication lag | Current time behind primary |
| Refresh failures | Any issues in the last 7 days |

## Considerations

> **Note**: If replication lag exceeds your RPO requirement, consider increasing replication frequency (e.g., from hourly to every 10 minutes) or splitting critical databases into a separate failover group with more aggressive scheduling.

**More Information:**
* [REPLICATION_GROUP_REFRESH_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/replication_group_refresh_history) — Function reference
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — RPO and RTO concepts


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


#### What is your target RPO (Recovery Point Objective) in minutes? (`dr_rpo_target`: text)
**What is this asking?**
RPO defines the maximum acceptable data loss during a disaster, measured in
time. A 10-minute RPO means you accept losing up to 10 minutes of data.

**Common Values:**
- `5` — Near-zero data loss (aggressive, higher replication cost)
- `10` — Standard for critical business data
- `30` — Acceptable for most analytical workloads
- `60` — Standard for non-critical or batch-oriented data

**Relationship to Replication Frequency:**
Your replication frequency should be equal to or less than your RPO target.
Example: 10-minute RPO requires at least 10-minute replication frequency.


#### How often should replication run? (`dr_replication_frequency`: single-select)
**What is this asking?**
Select the replication interval. This directly sets your RPO — data
ingested between refreshes could be lost during failover.

**Options:**
- `10 MINUTE` — 10-minute RPO (recommended for critical data)
- `30 MINUTE` — 30-minute RPO (standard workloads)
- `60 MINUTE` — 1-hour RPO (non-critical data)
- `120 MINUTE` — 2-hour RPO (low-criticality data)
- `USING CRON 0 0 * * * UTC` — Daily at midnight UTC

**Note:** Snowflake's `REPLICATION_SCHEDULE` only accepts `<n> MINUTE`
or `USING CRON <expr> <timezone>` syntax. The selected value is used
verbatim in the generated SQL.

**Recommendation:** Start with `10 MINUTE` for critical databases.
You can create separate failover groups with different frequencies for
different RPO tiers.

**Options:**
- 10 MINUTE
- 30 MINUTE
- 60 MINUTE
- 120 MINUTE
- USING CRON 0 0 * * * UTC
