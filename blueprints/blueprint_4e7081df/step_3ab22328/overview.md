In this step, you'll create a database from the shared infrastructure database, giving this account access to centralized governance objects like FinOps tags and cost reporting views.

**Account Context:** This step should be executed from the **newly created account** (not the Organization Account).

## **Why is this important?**

Consuming the infrastructure share provides this account with:
- **Centralized tags**: Access to DOMAIN, ENVIRONMENT, and other governance tags
- **Naming conventions**: Reference to organizational standards
- **Cost reporting views**: Visibility into cross-account cost allocation
- **Single source of truth**: All accounts use the same governance objects

Without this step, the account would be isolated from your organization's governance framework.

## **Prerequisites**

- Account created successfully (Create Account step)
- Logged into the new account as ACCOUNTADMIN
- Infrastructure share granted to this account (done in previous step)

## **Key Concepts**

**Shared Database**
A database created from a Snowflake share. It provides read-only access to objects shared from another account without data duplication or storage costs.

**Provider vs. Consumer**
- **Provider**: The Organization Account that created and owns the share
- **Consumer**: This new account that will access the shared objects

**Read-Only Access**
Shared databases are read-only in the consumer account. You can SELECT from tables and views, but cannot INSERT, UPDATE, or DELETE. The provider account maintains and updates the shared objects.

**Naming the Shared Database**
You'll create a local database that references the share. The name should indicate it's a shared resource (e.g., `infrastructure_shared` or `governance_shared`).

**More Information:**
* [Consuming Shared Data](https://docs.snowflake.com/en/user-guide/data-sharing-consumer) — How to access shared data
* [CREATE DATABASE FROM SHARE](https://docs.snowflake.com/en/sql-reference/sql/create-database) — SQL reference

### Configuration Questions

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

#### What name should be used for this account? (`new_account_name`: text)
**What is this asking?**
Confirm or customize the account name. Based on your Platform Foundation naming conventions, a suggested name was generated in the previous step.

**Naming Requirements:**
- Must be unique within your organization
- Can contain letters, numbers, and underscores
- Cannot start with a number
- Maximum 255 characters
- Will be converted to uppercase internally

**Recommended Format:**
Based on your Platform Foundation settings, follow this pattern:
- If prefix is used: `{prefix}_{domain}_{environment}` or `{prefix}_{environment}_{domain}`
- If no prefix: `{domain}_{environment}` or `{environment}_{domain}`

**Examples:**
- `ACME_SALES_PROD`
- `ACME_DEV_FINANCE`
- `ANALYTICS_TEST`

**Best Practice:**
Use the suggested name from the previous step unless you have a specific reason to customize it. Consistent naming makes governance and cost allocation easier.

#### Which domain will this account represent? (`account_domain`: multi-select)
**What is this asking?**
Select the business domain this account will represent. This account will serve all environments (Dev, Test, Prod) for this domain.

**Why does this matter?**
- The domain becomes part of the account name
- Cost allocation at the account level will be attributed to this domain
- All resources in this account are associated with this domain

**Note on Environments:**
Since you're using a domain-based strategy, environments (Dev, Test, Prod) will be organized **within** this account at the database level. You'll configure environments when creating data products.

**More Information:**
* [Managing Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account management overview

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

#### What name should be used for the shared infrastructure database in this account? (`shared_database_name`: text)
**What is this asking?**
Choose a name for the database that will be created from the infrastructure share. This is a local reference to the shared governance objects.

**Why does this matter?**
This database name will be used in SQL queries when referencing governance objects like tags and cost reporting views.

**Recommendations:**
- Use a name that indicates it's a shared resource
- Keep it consistent across all accounts
- Use lowercase with underscores

**Examples:**
- `infrastructure_shared`
- `governance_shared`
- `platform_shared`

**Default recommendation:** `{{ platform_database_name | lower }}_shared`

**Note:** This creates a read-only database. You cannot create objects in this database.

#### Which environment will this account represent? (`account_environment`: multi-select)
**What is this asking?**
Select the SDLC environment this account will represent. This account will serve all domains (Sales, Finance, HR, etc.) for this environment.

**Why does this matter?**
- The environment becomes part of the account name
- Cost allocation at the account level will be attributed to this environment
- All resources in this account are associated with this environment

**Environment Considerations:**
- **DEV/DEVELOPMENT**: Lower security, experimentation allowed
- **TEST/QA**: Moderate security, controlled changes
- **PROD/PRODUCTION**: Highest security, strict change control

**Note on Domains:**
Since you're using an environment-based strategy, domains will be organized **within** this account at the database level. You'll configure domains when creating data products.

**More Information:**
* [Managing Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account management overview

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
