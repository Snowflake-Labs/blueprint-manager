This step collects the requirements for your DR implementation including target account, databases to protect, replication frequency, and object types.

## Why is this important?

- Selecting the wrong object types leaves account-level security configuration (network policies, roles, users) unprotected — the target account would be open to any IP post-failover
- RPO is directly driven by replication frequency — setting the frequency too low means acceptable data loss assumptions are wrong
- Defining database scope explicitly prevents accidental inclusion of imported or system databases that cannot be replicated
- These choices are codified into the failover group and are non-trivial to change after initial setup

## Prerequisites

- ACCOUNTADMIN role access on the source account
- DR Assessment (Task 1) completed — target account confirmed, existing groups audited, coverage gaps identified
- Target account name and organization name confirmed from step 1.1

## Key Concepts

- **Target Account**: The Snowflake account in a different region that will serve as your DR target. Must be in the same organization.
- **RPO Requirement**: How much data loss is acceptable. Drives replication frequency.
- **Object Types**: Beyond databases, failover groups can include users, roles, warehouses, integrations, network policies, and account parameters.

## What Gets Defined

| Requirement | Purpose |
|-------------|---------|
| Target account | Where replicated data will reside |
| Critical databases | Which databases to include in failover group |
| Object types | Account-level objects to replicate |
| Replication frequency | How often data syncs (drives RPO) |
| Client redirect | Whether to enable transparent failover |

## Considerations

> **Note**: Account objects (USERS, ROLES, WAREHOUSES, etc.) can only belong to ONE failover group. Databases can be split across multiple groups for different RPO tiers.

**More Information:**
* [CREATE FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/create-failover-group) — Full syntax and parameter reference
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Object type support


### Configuration Questions

#### What is your Snowflake organization name? (`snowflake_org_name`: text)
Your Snowflake organization name is the first part of your account URL and connection identifiers. This is a required component of all Account Identifiers.  
  **How to find your organization name:**  
  Look at your current Snowflake URL. The organization name is the portion before the dash:  
  * https://\*\*ACME\*\*-prod.snowflakecomputing.com → Organization name is ACME  
  * https://\*\*XY12345\*\*-prod.snowflakecomputing.com → Organization name is XY12345  
* **Types of Organization Names:**  
  * **Custom Name:** A human-readable name like ACME or INITECH that was requested from Snowflake. These provide better branding and more readable URLs.  
  * **System-Generated:** An auto-assigned alphanumeric code like XY12345 or AB98765, created automatically during self-service sign up. Companies typically keep this name if transparency of your organization name in the URL is unnecessary or undesirable.   
* **To request a custom name:** If you have a system-generated name and want to change it, [contact Snowflake Support](https://community.snowflake.com/s/article/How-To-Submit-a-Support-Case-in-Snowflake-Lodge) or your account team. Custom names must be globally unique, start with a letter, and contain only letters and numbers.  
  **More Information:**  
  * [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) 

#### What is the target DR account name? (`dr_target_account`: text)
**What is this asking?**
Provide the Snowflake account name for your DR target. This is the account
in a different region that will receive replicated data and serve as your
failover destination.

**Format:**
Use the account name only (not the full URL). Example: `MY_DR_ACCOUNT`

**Requirements:**
- Must be in the same Snowflake organization as the source account
- Should be in a different region (for geographic redundancy)
- Must be Business Critical Edition or higher for failover groups

**How to find it:**
Run `SHOW REPLICATION ACCOUNTS;` on the source to list all accounts in your org.


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


#### What is the source (primary) account name? (`dr_source_account`: text)
**What is this asking?**
Provide the Snowflake account name for your source (primary) account. This
is the account that currently holds your production data.

**Format:**
Use the account name only. Example: `MY_PROD_ACCOUNT`

**How to find it:**
Run `SELECT CURRENT_ACCOUNT_NAME();` on your current account.


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


#### Which object types do you want to replicate? (`dr_object_types`: multi-select)
**What is this asking?**
Select all account-level object types that should be included in the failover group.

**Object Types:**
- **DATABASES**: Your databases and all their contents (tables, views, procedures, etc.)
- **USERS**: User accounts and authentication settings
- **ROLES**: Role hierarchy and privilege grants
- **WAREHOUSES**: Warehouse definitions (replicate in suspended state)
- **INTEGRATIONS**: Security, API, and storage integrations
- **NETWORK POLICIES**: IP allowlist/blocklist rules
- **ACCOUNT PARAMETERS**: Account-level configuration settings
- **RESOURCE MONITORS**: Credit usage monitors and quotas
- **SHARES**: Outbound data shares to other accounts or Marketplace listings

**Recommendation:** At minimum select DATABASES, USERS, and ROLES. For full
DR coverage, select all types. Include SHARES if this account has outbound
data shares or Marketplace listings that must remain available post-failover.

**Note:** Account objects (USERS, ROLES, WAREHOUSES, etc.) can only belong
to ONE failover group.

**Options:**
- Databases
- Users
- Roles
- Warehouses
- Integrations
- Network Policies
- Account Parameters
- Resource Monitors
- Shares

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

