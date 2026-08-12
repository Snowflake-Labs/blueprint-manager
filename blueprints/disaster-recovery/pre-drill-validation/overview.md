This step verifies that replication is healthy and current before executing a failover drill. Running a drill with stale or broken replication could produce misleading results.

## Why is this important?

- A drill with excessive replication lag means the failback will restore stale data, producing an inaccurate RTO/RPO measurement
- In-flight refresh operations can conflict with the failover promotion — always wait for any active refresh to complete
- Recording a pre-drill baseline (lag, last refresh time) makes it possible to accurately measure actual RPO achieved during the drill
- This step is the go/no-go gate for the drill — if replication is broken or lagging beyond RPO, the drill should be postponed

## Prerequisites

- ACCOUNTADMIN role access on the source account
- Failover group created and actively replicating (Task 2 complete)
- Stakeholder coordination complete (failover temporarily redirects workloads)

## Key Concepts

- **Pre-Drill Baseline**: Record the current state (primary account, last refresh, lag) before making any changes.
- **Replication Lag**: The time difference between the target's data and the source's current state. Must be within acceptable RPO before proceeding.
- **Refresh Progress**: Check for any in-flight refresh operations that should complete before failover.

## What Gets Validated

| Check | Criteria |
|-------|----------|
| Failover groups exist | At least one group configured |
| Replication is current | Lag within RPO threshold |
| No in-flight refresh | No active refresh that could conflict |
| Baseline recorded | Start timestamp and current state documented |

**More Information:**
* [REPLICATION_GROUP_REFRESH_PROGRESS](https://docs.snowflake.com/en/sql-reference/functions/replication_group_refresh_progress) — Monitor in-flight refresh status
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Drill and testing guidance


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

