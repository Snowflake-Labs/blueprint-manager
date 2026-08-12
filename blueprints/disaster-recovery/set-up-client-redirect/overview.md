This step creates connection objects that provide a stable URL for transparent client failover. When failover occurs, the connection URL automatically redirects to the new primary account.

## Why is this important?

- Without client redirect, all application connection strings must be manually updated during a DR event, adding significant time to RTO
- The connection URL is the only stable endpoint that survives failover without manual intervention — applications must be migrated to it before a real outage occurs
- The connection is named `{dr_failover_group_name}_CONN` — application teams need this name to update connection strings
- Part 2 (creating the secondary connection) must run on the **target account** before failover can be transparent

## Prerequisites

- ACCOUNTADMIN role access on both source and target accounts
- Primary failover group created (step 2.2) and secondary created on target (step 2.3)
- Business Critical Edition on both accounts
- `dr_enable_client_redirect` answer set to `Yes`

## Key Concepts

- **Client Redirect**: A Snowflake feature where a connection URL transparently resolves to the current primary account, regardless of which account is primary.
- **Connection Object**: A named Snowflake object that provides the stable connection URL.
- **Connection URL**: The URL clients use instead of direct account URLs. Automatically redirects after failover.

## Connection Naming Convention

> **Important:** The connection object is named `{dr_failover_group_name}_CONN`. For example,
> if `dr_failover_group_name` is `PROD_DR`, the connection will be named `PROD_DR_CONN` and
> the connection URL will follow the pattern `<org>-PROD_DR_CONN.snowflakecomputing.com`.
>
> Update **all** application connection strings to use this connection URL **before** executing
> a failover. Applications using direct account URLs will not be automatically redirected.

## What Gets Created

| Object | Purpose |
|--------|---------|
| Primary Connection | Connection object on source account |
| Secondary Connection | Replica connection on target account |
| Connection URL | Stable URL for client applications |

## Considerations

> **Note**: After creating client redirect, update ALL application connection strings to use the connection URL. Applications using direct account URLs will NOT be automatically redirected during failover.

**More Information:**
* [CREATE CONNECTION](https://docs.snowflake.com/en/sql-reference/sql/create-connection) — SQL reference
* [Client Redirect](https://docs.snowflake.com/en/user-guide/client-redirect) — Configuration and failover behavior


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
