This step creates the primary failover group on the source account, defining which objects are replicated, to which target accounts, and on what schedule.

## Why is this important?

- The failover group is the core DR construct — without it, no replication or failover is possible
- Object type selection is a long-term decision: adding types later requires `ALTER FAILOVER GROUP` and triggers a full re-sync of newly added types
- Including `NETWORK POLICIES` is critical — omitting it leaves the target account open to any IP address post-failover
- The `IF NOT EXISTS` clause makes this step idempotent — safe to re-run without duplicating the group

## Prerequisites

- ACCOUNTADMIN role access on the source account
- Business Critical Edition on both source and target accounts
- Target account exists in the same organization (confirmed in step 1.1)
- DR requirements defined (step 2.1)

## Key Concepts

- **Failover Group**: The top-level DR construct that bundles databases and account objects for replication with failover capability.
- **ALLOWED_DATABASES**: Specifies which databases are included in the group.
- **REPLICATION_SCHEDULE**: Defines how frequently the group is refreshed (interval or cron expression).
- **ALLOWED_ACCOUNTS**: Target accounts that can create secondary replicas of this group.

## What Gets Created

| Object | Purpose |
|--------|---------|
| Failover Group | Primary replication group on source account |
| Replication Schedule | Automated refresh interval |
| Target Account Allowlist | Which accounts can replicate this group |

## Integration Replication — Post-Failover Requirements

When `Integrations` is included in your object types, all five supported integration subtypes are replicated. Two subtypes require additional cloud-provider configuration before they function correctly on the target account:

| Integration Type | Post-Failover Action Required |
|---|---|
| Security Integrations | None — replicate automatically (requires `ROLES` in `OBJECT_TYPES`) |
| API Integrations | Update the remote service (API Gateway / Azure APIM / GCS) to trust the target account's IAM identity |
| Storage Integrations | Update cloud IAM trust policy to grant the target account's Snowflake IAM user access to your cloud storage bucket |
| External Access Integrations | None — replicate automatically |
| Notification Integrations | Only some notification types replicate; verify post-failover. SNS-based pipes need the target SQS queue subscribed to your SNS topic |

For storage and notification integration setup steps, see the Snowflake documentation linked in **More Information** below.

## Considerations

> **Note**: The failover group SQL must be executed with ACCOUNTADMIN on the source account. The `IF NOT EXISTS` clause ensures idempotency if re-running the blueprint.

**More Information:**
* [CREATE FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/create-failover-group) — Full syntax and ALLOWED_INTEGRATION_TYPES reference
* [Integration replication](https://docs.snowflake.com/en/user-guide/account-replication-intro#integration-replication) — Which integration types are supported
* [Configure cloud storage access for secondary storage integrations](https://docs.snowflake.com/en/user-guide/account-replication-stages-pipes-load-history) — Post-failover IAM setup


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
