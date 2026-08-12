This step creates the secondary (replica) failover group on the target account, sets the replication schedule, and triggers the initial data sync.

## Why is this important?

- The secondary group is what makes failover possible — without it, the primary group has nowhere to fail over to
- The initial refresh is a full data transfer; for large environments this can take hours and should be scheduled during a maintenance window
- Setting the replication schedule on the target side ensures refreshes continue on a predictable cadence
- This step must run on the **target account** — a common mistake that causes confusing errors if run on the source

## Prerequisites

- ACCOUNTADMIN role access on the **target account**
- Primary failover group created on source account (step 2.2)
- Business Critical Edition on target account
- Source and target accounts in the same organization

## Key Concepts

- **Secondary Failover Group**: A replica of the primary group that receives replicated data. Can be promoted to primary during failover.
- **AS REPLICA OF**: SQL clause that links the secondary to its primary source.
- **Initial Refresh**: The first full replication sync — transfers all data from source to target.

## What Gets Created

| Object | Purpose |
|--------|---------|
| Secondary Failover Group | Replica on target account |
| Replication Schedule | Automated refresh on target side |
| Initial Data Sync | First full copy of all included objects |

## Considerations

> **Note**: This step must be executed on the **target account** (not the source). The initial refresh may take significant time depending on data volume. Monitor progress with `REPLICATION_GROUP_REFRESH_PROGRESS`.

**More Information:**
* [CREATE FAILOVER GROUP AS REPLICA OF](https://docs.snowflake.com/en/sql-reference/sql/create-failover-group) — Secondary group creation syntax
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Initial sync and refresh behavior


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

#### What is the source (primary) account name? (`dr_source_account`: text)
**What is this asking?**
Provide the Snowflake account name for your source (primary) account. This
is the account that currently holds your production data.

**Format:**
Use the account name only. Example: `MY_PROD_ACCOUNT`

**How to find it:**
Run `SELECT CURRENT_ACCOUNT_NAME();` on your current account.


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
