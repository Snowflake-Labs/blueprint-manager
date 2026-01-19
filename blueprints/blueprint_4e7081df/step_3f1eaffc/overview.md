In this step, you'll configure the technical parameters for the new account, including the Snowflake edition, cloud region, initial administrator credentials, and local infrastructure settings.

**Account Context:** This step should be executed from your Organization Account.

## **Why is this important?**

These parameters define the capabilities, location, and initial access for the new account:
- **Edition** determines available features and compliance certifications
- **Region** affects data residency, latency, and disaster recovery options
- **Initial administrator** is the first user who can access and configure the account
- **Local infrastructure** provides a writable database for account-specific objects (the replicated infrastructure database is read-only)

## **Prerequisites**

- Account purpose defined (Define Account Purpose step)
- Knowledge of required Snowflake edition for this account's workloads
- Designated initial administrator with valid email address

## **Key Concepts**

**Account Name**
The unique identifier for this account within your organization. Based on your Platform Foundation naming conventions, a suggested name was generated. You can accept it or customize it while maintaining compliance with your naming standards.

**Snowflake Edition**
Each account has an edition that determines its features:
- **Standard**: Core features, basic security
- **Enterprise**: Advanced security, failover, 90-day Time Travel
- **Business Critical**: HIPAA/PCI compliance, customer-managed keys, private connectivity

**Cloud Region**
The geographic location where the account's data and compute resources will reside. Consider data residency requirements, proximity to users, and disaster recovery strategy.

**Initial Administrator**
The first user created in the account with ACCOUNTADMIN role. This user bootstraps all subsequent configuration.

**More Information:**
* [CREATE ACCOUNT](https://docs.snowflake.com/en/sql-reference/sql/create-account) — SQL command reference
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Feature comparison
* [Supported Cloud Regions](https://docs.snowflake.com/en/user-guide/intro-regions) — Available regions

### Configuration Questions

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

#### What Snowflake edition will this account use? (`new_account_edition`: multi-select)
**What is this asking?**
Select the Snowflake edition for this account.

**Why does this matter?**
The edition determines:
- Available features (multi-cluster warehouses, extended Time Travel)
- Compliance certifications (HIPAA, PCI DSS)
- Security options (customer-managed keys, private connectivity)
- Cost per credit

**Options explained:**

**Standard:**
- Core Snowflake features
- 1-day Time Travel
- Basic security features
- Best for: Development environments, proof-of-concepts, cost-sensitive workloads

**Enterprise:**
- Multi-cluster warehouses
- Up to 90-day Time Travel
- Column-level security
- Failover/Failback support
- Best for: Most production workloads

**Business Critical:**
- Everything in Enterprise, plus:
- HIPAA and PCI DSS compliance
- Customer-managed encryption keys (Tri-Secret Secure)
- Private connectivity (PrivateLink)
- Best for: Highly regulated industries, sensitive data

**Recommendation:**
- **Development/Test accounts**: Standard or Enterprise
- **Production accounts**: Enterprise or Business Critical
- **Accounts with sensitive/regulated data**: Business Critical

**More Information:**
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) — Full feature comparison
**Options:**
- Standard
- Enterprise
- Business Critical

#### What cloud region should host this account? (`new_account_region`: text)
**What is this asking?**
Specify the Snowflake Region ID where this account will be created.

**Why does this matter?**
The region affects:
- **Data residency**: Where your data physically resides (critical for compliance)
- **Latency**: Distance from your users and data sources
- **Disaster recovery**: Ability to replicate to other regions
- **Cross-region sharing**: Sharing data across regions incurs additional costs

**How to find available regions:**
```sql
-- Run in any Snowflake account
SHOW REGIONS;
```

**Key Considerations:**
- **Data Residency**: Compliance requirements may mandate specific regions
- **Latency**: Choose a region close to your users and data sources
- **Disaster Recovery**: Consider pairing with another region for failover
- **Organization Account**: Often accounts are in the same region as the org account

**Common Region IDs:**
| Cloud | Region | ID |
|-------|--------|-----|
| AWS | US West 2 (Oregon) | `AWS_US_WEST_2` |
| AWS | US East 1 (N. Virginia) | `AWS_US_EAST_1` |
| AWS | EU West 1 (Ireland) | `AWS_EU_WEST_1` |
| Azure | East US 2 | `AZURE_EASTUS2` |
| Azure | West Europe | `AZURE_WESTEUROPE` |
| GCP | US Central 1 | `GCP_US_CENTRAL1` |

**Default behavior:**
If left blank, the account is created in the same region as the Organization Account.

**More Information:**
* [Supported Cloud Regions](https://docs.snowflake.com/en/user-guide/intro-regions) — Full region list

#### What username should be used for the initial administrator? (`new_account_admin_name`: text)
**What is this asking?**
Specify the username (login name) for the first ACCOUNTADMIN user in this account.

**Why does this matter?**
This is the bootstrap user who will configure the account after creation. Choosing the right person and a proper username format ensures smooth handoff and follows your organization's identity standards.

**This is NOT a display name** — it's the login identifier the administrator will use to access Snowflake.

**Recommendations:**
- Use a standard username format (e.g., `jsmith`, `john.smith`, or email address)
- Choose a trusted member of your platform or security team
- Use lowercase for consistency
- Avoid special characters other than `.`, `_`, or `-`

**Examples:**
- `platform_admin`
- `john.smith`
- `jsmith@company.com`

**Security Notes:**
- Password will be set to require change on first login
- Additional ACCOUNTADMIN users should be added for redundancy
- This user should enable MFA after first login

**More Information:**
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user) — User creation reference

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

#### Provide a brief description of this account's purpose. (`account_description`: text)
**What is this asking?**
Write a short description that explains what this account is for.

**Why does this matter?**
A clear description helps team members understand the account's purpose at a glance. It appears in account listings and documentation, making governance and auditing easier.

**Examples:**
- "Sales domain account - contains all environments for Sales analytics"
- "Finance domain account for financial reporting and analytics"
- "HR domain account for people analytics and workforce planning"

#### What email address should be used for the initial administrator? (`new_account_admin_email`: text)
**What is this asking?**
Provide the email address for the initial ACCOUNTADMIN user.

**Why does this matter?**
This email will receive:
- Account activation notifications
- Password reset links
- Critical security alerts

If the email is unmonitored or inaccessible, you may lose access to password recovery and important security notifications.

**Best Practices:**
- Use a monitored email address
- Consider a shared mailbox for continuity (e.g., `snowflake-admin@company.com`)
- Ensure the named administrator has access to this email

**More Information:**
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user) — User creation reference

#### What name should be used for the local infrastructure database? (`local_infra_database`: text)
**What is the Local Infrastructure Database?**
The Local Infrastructure Database is a writable database within this account that stores account-specific administrative and governance objects. This is separate from the replicated infrastructure database which is read-only.

**Why is this needed?**
The infrastructure database replicated from the Organization Account is **read-only**. Account-specific objects like authentication policies, local procedures, and account-level configurations must be created in a local, writable database.

**Recommended Naming Approach:**
Use a name that clearly identifies this as a local, account-specific infrastructure database. Follow the same naming pattern as your platform infrastructure database. Consider formats like:
- `<domain>_LOCAL` — e.g., `PLAT_LOCAL`, `CDP_LOCAL`
- `<domain>_<account>` — e.g., `PLAT_SALES`, `PLAT_DEV`
- `LOCAL_<purpose>` — e.g., `LOCAL_INFRA`, `LOCAL_ADMIN`

**Example:** `PLAT_LOCAL` — clearly indicates Platform team ownership and local (non-replicated) scope

**Alternative Examples:**
- `CDP_LOCAL` — Cloud Data Platform local objects
- `<ACCOUNT>_INFRA` — Account-specific infrastructure (e.g., `SALES_INFRA`)
- `LOCAL_ADMIN` — Local administration database

**Important:** This name should be distinct from the replicated infrastructure database to avoid confusion.

**More Information:**
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)

#### What schema name should be used for security policies? (`local_policies_schema`: text)
**What is the Policies Schema?**
The Policies Schema is created within the Local Infrastructure Database and contains account-specific security objects including authentication policies, network policies, and other configurations that cannot be replicated.

**Recommended Name:** `POLICIES`

This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:
- `SECURITY` — Security-focused objects
- `AUTH` — Authentication and authorization objects
- `GOVERNANCE` — General governance objects

**Schema Configuration:**
This schema will be created with **Managed Access** enabled, which means:
- Only the schema owner (typically SECURITYADMIN or ACCOUNTADMIN) can grant privileges on objects
- Prevents "shadow" security configurations where object creators grant their own access
- Provides centralized control over who can access security policy objects

**Best Practice:** Use a simple, single-word name that represents the functional purpose.

**More Information:**
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)
* [Authentication Policies](https://docs.snowflake.com/en/user-guide/authentication-policies)

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
