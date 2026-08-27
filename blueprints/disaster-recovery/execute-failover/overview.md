This step promotes the secondary failover group to primary, making the target account the new active account for all replicated objects.

## Why is this important?

- This is the core DR action — promotion makes the target account writable and moves all failover group objects there
- The time taken from this step to client redirect completion is your actual RTO measurement — record it carefully
- Suspending replication before promotion prevents race conditions with in-flight refreshes
- All workloads are interrupted during the window between promotion and client redirect — minimize this gap

## Prerequisites

- ACCOUNTADMIN role access on the **target account**
- Pre-drill validation complete (step 3.1) — replication confirmed healthy and current
- Stakeholders notified that failover is beginning

## Key Concepts

- **Failover (Promotion)**: The act of promoting a secondary failover group to primary. The target account becomes writable.
- **RTO Measurement**: The time from failover start to when clients are redirected is a key component of Recovery Time Objective.
- **Suspend Before Promote**: Replication must be suspended on the target before promotion to avoid conflicts.

## What Happens

| Action | Effect |
|--------|--------|
| Suspend replication | Stop any in-flight refresh on target |
| Promote to primary | Target becomes the writable primary |
| Record duration | Measure actual failover time (contributes to RTO) |
| Verify promotion | Confirm target shows as primary |

## Considerations

> **Note**: During the time between promoting and redirecting clients, workloads are interrupted. Minimize this gap by having the client redirect step ready to execute immediately after promotion.

**More Information:**
* [ALTER FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/alter-failover-group) — Failover promotion syntax
* [Failover and Failback](https://docs.snowflake.com/en/user-guide/account-replication-failover-groups) — Managing the failover process


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


#### Do you want to enable client redirect for transparent failover? (`dr_enable_client_redirect`: single-select)
**What is this asking?**
Client redirect creates a stable connection URL that automatically points to
whichever account is currently primary. Applications using this URL are
transparently redirected during failover without connection string changes.

**Select "Yes" to:**
- Create a connection object with a stable URL
- Enable automatic client redirection during failover
- Reduce manual intervention needed during DR events

**Select "No" if:**
- You prefer manual connection string management
- Your applications already handle multi-account connections
- You're using DNS CNAME-based routing

**Recommendation:** Yes for production environments. It significantly
reduces RTO by eliminating manual connection string updates.

**Options:**
- Yes
- No
