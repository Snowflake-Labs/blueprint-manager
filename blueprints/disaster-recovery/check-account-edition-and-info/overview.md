This step verifies your Snowflake account edition and organization membership to confirm DR feature availability.

## Why is this important?

- Business Critical Edition (or higher) is required for failover groups, client redirect, and account object replication — without it, full DR capability is unavailable
- Both source and target accounts must be in the same Snowflake organization for replication to work
- Confirming this upfront prevents wasted effort configuring DR on an account that cannot support it
- The organization name returned by `CURRENT_ORGANIZATION_NAME()` may be an internal locator (e.g., `UZJTRFC`) rather than your company name — use this value exactly in all replication configurations

## Prerequisites

- ACCOUNTADMIN role access on the source account
- Snowflake account accessible via Snowsight or SQL client

## Key Concepts

- **Business Critical Edition**: Required for failover groups, client redirect, and account object replication (users, roles, warehouses, integrations)
- **Standard/Enterprise Edition**: Only supports database and share replication — no failover, no client redirect
- **Organization**: Source and target accounts must belong to the same Snowflake organization

## What Gets Checked

| Item | Why It Matters |
|------|----------------|
| Account name | Identifies the source account for replication |
| Organization name | Both accounts must share the same org |
| Edition | Determines which DR features are available |

## Considerations

> **Note**: If your account is Standard or Enterprise edition, you can still replicate databases but cannot create failover groups or use client redirect. Upgrade to Business Critical for full DR capabilities.

**More Information:**
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Feature comparison by edition
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Overview of DR capabilities


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

