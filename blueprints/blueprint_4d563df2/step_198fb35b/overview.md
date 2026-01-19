In this step, you'll create a Snowflake SHARE object that makes the Infrastructure Database accessible to all accounts in your organization. This step produces:

1. **Share Object** (infrastructure\_share\_name) — A named share that grants access to the Infrastructure Database  
2. **Share Grants** — Privileges on the database, schemas, and objects (tags, network rules, views) added to the share

The share is created now so that when you run the **Account Creation** workflow, new accounts can immediately consume the share and access governance objects. Without this share, each account would need its own copy of tags and policies, leading to inconsistency and duplication.

**How it works:**

* This step (in the Organization Account) creates the *outbound* share  
* The Account Creation workflow (in each new account) creates an *inbound* database from the share  
* All accounts then reference the same governance objects with zero storage cost

**Account Context:** This step should be executed in your Organization Account.

## Why is this important?

In a multi-account strategy, each account needs access to the governance framework established in the Organization Account. Snowflake's Secure Data Sharing provides:

* **Real-time access**: No data copying or synchronization delays  
* **Single source of truth**: All accounts reference the same governance objects  
* **Zero storage cost**: Shared data doesn't consume storage in target accounts  
* **Centralized management**: Update once, available everywhere

## Prerequisites

* Infrastructure database created (this is created in the *Create Infrastructure Database* step of this workflow)
* Multi-account strategy selected (this is selected in the previous *Determine Account Strategy* step of this workflow)

## Key Concepts

* [**Secure Data Sharing:**](https://docs.snowflake.com/en/user-guide/data-sharing-intro) Snowflake's native capability to share data between accounts without copying. The provider account (your Organization Account) creates a SHARE object and grants access to specific databases, schemas, and objects. Consumer accounts create a database from the share.

* [**Share Object:**](https://docs.snowflake.com/en/user-guide/data-sharing-gs#label-data-sharing-share-options) A named object that defines what is being shared. You grant privileges on database objects to the share, then grant the share to specific accounts.
* [**Account Identifiers for Sharing:**](https://docs.snowflake.com/search?q=account%20identifier) When granting a share to accounts, you use the account's organization-qualified name: \<org\_name\>.\<account\_name\>.
* **Inbound vs Outbound Shares**
  * **Outbound share**: Created in the provider account (this step)  
  * **Inbound share**: Consumed in target accounts (done when creating new accounts)

## More Information

* [Introduction to Secure Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Overview of sharing capabilities  
* [Share Secure Database Objects](https://docs.snowflake.com/en/user-guide/data-sharing-gs#label-data-sharing-share-options) — Understanding share relationships  
* [CREATE SHARE](https://docs.snowflake.com/en/sql-reference/sql/create-share) — SQL command reference  
* [GRANT to SHARE](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege-share) — Granting objects to shares

### Configuration Questions

#### What name would you like to use for the infrastructure database share? (`infrastructure_share_name`: text)
**What is this asking?** Choose a name for the SHARE object that will provide access to your infrastructure database.  

  **Why does this matter?** This name will be visible to all accounts that consume the share. Choose something descriptive and aligned with your naming conventions.  
  **Recommendations:**  
  * Use lowercase with underscores  
  * Include a clear identifier like infrastructure or governance  
  * Keep it concise but descriptive  

* **Examples:**  
  * infrastructure\_share  
  * governance\_share  
  * platform\_share  

* **Default recommendation:** infrastructure\_share

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

#### What do you want to name the governance schema? (`governance_name`: text)
**What is the Governance Schema?**  
  The Governance schema is created within the Infrastructure Database and contains objects related to security, compliance, and platform governance. This includes platform and FinOps tags, network rules, audit views, and administrative procedures.  

  **Recommended Name:** GOVERNANCE  

  This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:  
  * ADMIN — Administration  
  * SECURITY — Security-focused objects  
  * PLATFORM — Platform-level objects  

**Schema Configuration:**  
  This schema will be created with **Managed Access** enabled, which means:  
  * Only the schema owner (typically [SYSADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system) - aka System Administrator) can grant privileges on objects  
  * Prevents "shadow" security configurations where object creators grant their own access  
  * Provides centralized control over who can access governance objects  

**Best Practice:** Use a simple, single-word name that represents the functional purpose.  
  
**More Information:**  
  * [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)  
  * [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)  
  * [System Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system)

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
