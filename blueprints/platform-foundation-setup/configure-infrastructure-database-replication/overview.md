In this step, you'll create a Snowflake REPLICATION GROUP that enables the Infrastructure Database to be replicated to all accounts in your organization. This step produces:

1. **Replication Group** (`infrastructure_replication_group`) — A named replication group that synchronizes the Infrastructure Database to target accounts  
2. **Automatic Refresh Schedule** — Configurable schedule for keeping replicated databases in sync

The replication group is created now so that when you run the **Account Creation** workflow, new accounts can create a replica of the infrastructure database and **apply governance tags to local objects**. Unlike data sharing (where shared objects are read-only), replication creates local copies that can be fully used.

**Why Replication instead of Sharing?**

* **Tags can be applied**: Replicated tags become local objects that can be SET on warehouses, databases, and other resources
* **Network rules work locally**: Replicated network rules can be referenced in local network policies
* **Full functionality**: All governance objects work exactly as if created locally

**How it works:**

* This step (in the Organization Account) creates the *primary* replication group  
* The Account Creation workflow (in each new account) creates a *secondary* replication group and replica database  
* All accounts then have their own local copy of governance objects, kept in sync automatically

**Account Context:** This step should be executed in your Organization Account.

## Why is this important?

In a multi-account strategy, each account needs access to the governance framework established in the Organization Account. Snowflake's database replication provides:

* **Writable governance objects**: Tags and network rules can be applied to local resources  
* **Automatic synchronization**: Changes in the source are replicated on schedule  
* **Point-in-time consistency**: All objects in the replication group are consistent  
* **Centralized management**: Define once, replicate everywhere

## Prerequisites

* Infrastructure database created (this is created in the *Create Infrastructure Database* step of this workflow)
* Multi-account strategy selected (this is selected in the previous *Determine Account Strategy* step of this workflow)
* Organization enabled for replication (all accounts in the same organization can replicate)

## Key Concepts

* [**Database Replication:**](https://docs.snowflake.com/en/user-guide/account-replication-intro) Snowflake's capability to replicate databases and account objects across accounts. Unlike sharing, replicated objects become local copies that can be fully used.

* [**Replication Group:**](https://docs.snowflake.com/en/sql-reference/sql/create-replication-group) A defined collection of objects that are replicated as a unit. The primary replication group exists in the source account; secondary replication groups exist in target accounts.

* [**Primary vs Secondary:**](https://docs.snowflake.com/en/user-guide/account-replication-intro#replication-groups-and-failover-groups)
  * **Primary**: The source replication group (in your Organization Account)  
  * **Secondary**: Replica replication groups (in each target account)

* **Tags and Replication**: Tags stored in the replicated database become local objects in each target account. This means you can `ALTER WAREHOUSE SET TAG` using the replicated tags — something not possible with shared tags.

* **Refresh Schedule**: Replication groups can be configured to automatically refresh on a schedule (e.g., every 10 minutes) or refreshed manually.

## More Information

* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Overview of replication capabilities  
* [CREATE REPLICATION GROUP](https://docs.snowflake.com/en/sql-reference/sql/create-replication-group) — SQL command reference  
* [Replication Considerations](https://docs.snowflake.com/en/user-guide/account-replication-considerations) — Important considerations for replicated objects
* [Replication and Tags](https://docs.snowflake.com/en/user-guide/object-tagging/interaction#replication) — How tags work with replication

### Configuration Questions

#### What name would you like to use for the infrastructure database replication group?   (`infrastructure_replication_group`: text)
**What is this asking?** Choose a name for the REPLICATION GROUP object that will synchronize your infrastructure database to other accounts.  
**Why does this matter?** This name will be used when creating secondary replication groups in target accounts. Choose something descriptive and aligned with your naming conventions.  
**Recommendations:**  
* Use lowercase with underscores  
* Include a clear identifier like infrastructure or governance  
* Keep it concise but descriptive  
* **Examples:**  
* infrastructure_replication_group  
* governance_replication_group  
* platform_replication_group  
* **Default recommendation:** infrastructure_replication_group

#### What do you want to name the platform database? (`platform_database_name`: text)
**What is the Platform/Infrastructure Database?**  
  The Infrastructure Database is a centralized "hub" database that houses platform-wide objects including tags, network rules, governance policies, and shared procedures. It is owned by the central platform team and shared across all accounts in multi-account deployments.  
  **Recommended Naming Approach:**  
  Use a name that clearly identifies this as a platform-owned, infrastructure-focused database. The format should be: \<domain\>\_\<dataproduct\>  
  * **Domain:** Use plat (short for "platform") or your platform team's acronym (e.g., cdp, snow, data)  
  * **Data Product:** Use infra or another term indicating infrastructure purpose  
* **Example:** PLAT\_INFRA — clearly indicates Platform team ownership and Infrastructure purpose  
  **Alternative Examples:**  
  * CDP\_INFRA — Cloud Data Platform Infrastructure  
  * SNOW\_ADMIN — Snowflake Administration  
  * DATA\_PLATFORM — Data Platform database  
* **Important:** Choose carefully\! This name will eventually be referenced by dozens to hundreds of objects, policies, and procedures. Changing it later can be complex and risky.  
  **More Information:**  
  * [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)  
  * [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)

#### What account strategy do you wish to implement? (`account_strategy`: multi-select)
Choose the account strategy that best fits your organization. Your choice determines how domain (business unit/entity) and environment are organized:  
  **Single Account:**  
  * Best for: Small to medium organizations, centralized teams, simpler governance  
  * Naming: Domain \+ Environment \+ Data Product at database level  
  * Pros: Lower operational overhead, easier cross-database queries, centralized management  
  * Cons: Less isolation, shared resource limits, single security boundary  
  * Recommendation: Consider setting up an organization account even for single-account deployments to enable future growth  
* **Multi-Account (Environment-based):**  
  * Best for: Organizations requiring strong environment isolation (dev/test/prod)  
  * Naming: Environment at account level, Domain \+ Data Product at database level  
  * Pros: Complete environment isolation, independent security controls, separate billing  
  * Cons: More complex data sharing, higher operational overhead  
  * Requirement: Organization account required  
* **Multi-Account (Domain-based):**  
  * Best for: Large enterprises with autonomous business units/domains  
  * Naming: Domain at account level, Environment \+ Data Product at database level  
  * Pros: Clear cost allocation per domain, independent governance, domain autonomy  
  * Cons: Higher complexity, requires data sharing for cross-domain analytics  
  * Requirement: Organization account required  
* **Multi-Account (Domain \+ Environment):**  
  * Best for: Large organizations needing both domain and environment isolation  
  * Naming: Domain \+ Environment at account level, Data Product at database level  
  * Pros: Maximum isolation, clear ownership and environment separation  
  * Cons: Highest complexity and operational overhead, most accounts to manage  
  * Requirement: Organization account required  
* **More Information:**  
  * [Organizations](https://docs.snowflake.com/en/user-guide/organizations)  
  * [Managing Multiple Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts)  
**Options:**
- Single Account
- Multi-Account (Environment-based)
- Multi-Account (Domain-based)
- Multi-Account (Domain + Environment)

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

#### What do you want to name your organization account? (`org_account_name`: text)
**Recommended Name:** ORG  
  Since there can be only one Organization Account per organization, the name should clearly indicate this special purpose. We recommend simply naming it ORG.  
  
  **Example URLs with Organization Account name ORG:**  
  * With Custom Org Name: [https://ACME-ORG.snowflakecomputing.com](https://ACME-ORG.snowflakecomputing.com)  
    * Org Name \= ACME  
    * Org Account Name \= Org  
  * System-generated Org Name: [https://XY12345-ORG.snowflakecomputing.com](https://XY12345-ORG.snowflakecomputing.com)  
    * Org Name \= XY12345  
    * Org Account Name \= Org  
* **Requirements:**  
  * Snowflake Enterprise Edition or higher  
  * ORGADMIN role granted in the existing account  
* **More Information:**  
  * [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts)  
  * [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)

#### How frequently should the infrastructure database be replicated to target accounts? (`replication_schedule`: multi-select)
**What is this asking?** Choose how often Snowflake should automatically synchronize the infrastructure database to all target accounts.  
**Why does this matter?** More frequent replication means changes (new tags, updated views) are available sooner in target accounts, but may have minor cost implications.  
**Recommendations:**  
* **Every 10 minutes** — Best for active development, changes propagate quickly
* **Every 30 minutes** — Good balance for most organizations
* **Every hour** — Suitable for stable environments with infrequent changes
* **Manual only** — For environments where you want explicit control over when changes propagate

**Note:** Infrastructure database changes (new tags, views) are typically infrequent, so even hourly refresh is usually sufficient.
**Options:**
- Every 10 minutes
- Every 30 minutes
- Every hour
- Manual only
