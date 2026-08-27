This step discovers existing replication and failover groups configured in your account, establishing a baseline of current DR infrastructure.

## Why is this important?

- Knowing whether failover groups already exist prevents duplicate configuration and helps identify gaps in coverage
- Distinguishing failover groups (promotable) from replication groups (read-only) is critical — only failover groups can be used for DR
- Confirming replication accounts ensures the target is in the same organization and accessible
- Network policies must be audited here to ensure they are included in the failover group scope — missing them causes a silent security regression post-failover

## Prerequisites

- ACCOUNTADMIN role access on the source account
- At least one other account in the same Snowflake organization (for replication accounts to appear)

## Key Concepts

- **Replication Group**: A collection of objects replicated from source to target accounts as read-only secondaries. Cannot be promoted.
- **Failover Group**: A replication group that additionally supports failover — the secondary can be promoted to primary during an outage.
- **Replication Accounts**: Other accounts in your organization that are enabled for replication.

## What Gets Audited

| Object | Purpose |
|--------|---------|
| Failover Groups | Groups that support promotion (full DR capability) |
| Replication Groups | Read-only replica groups (no failover) |
| Replication Accounts | Target accounts available for replication |
| Replication Databases | Legacy database-level replication (pre-failover groups) |
| Network Policies | Policies that must be replicated to maintain security post-failover |

## Considerations

> **Note**: If no failover or replication groups exist, this is a critical gap — your account has no DR protection. Proceed to Task 2 (Implementation) after completing the assessment.

**More Information:**
* [SHOW FAILOVER GROUPS](https://docs.snowflake.com/en/sql-reference/sql/show-failover-groups) — Command reference
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Replication overview


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

