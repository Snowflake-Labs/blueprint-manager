In this step, you'll determine what components should be included in your account-level object names to create a consistent naming standard for objects in your Snowflake environment. Well-defined naming standards make it easier to identify resources, understand their purpose, enforce governance, and automate operations. 

This step focuses on core **account-level object naming conventions** — the standards for how you name Snowflake databases, warehouses, and roles.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

A consistent naming convention is one of the most impactful decisions you'll make for long-term platform maintainability. Object names appear everywhere—in queries, dashboards, cost reports, and audit logs. Once objects are deployed to production and referenced by applications and users, renaming them becomes extremely complex and risky. Establishing clear, scalable naming standards now will pay dividends as your platform grows from dozens to hundreds or thousands of objects.

## External Prerequisites

None

## Key Concepts

Object naming strategy typically comprises these three core components for all account object types:

* **Domain**: Business unit/entity, or department (can be at account or database level)  
* **Environment**: dev, test, prod, etc. (can be at account or database level)  
* **Data Product**: a self-contained unit of data that serves a specific business purpose or support a specific use case (database level - covered in later workflows)

Depending on your account strategy, the names you select for these different components may appear at either the Account Level or Data Product Level (databases, warehouses, roles). Let’s look at a simple example:

* Single-Account Strategy  
  * Database: `finance_analytics_prod`  
* Multi-Account (by Environment)  
  * Account: `prod`   
  * Database: `finance_analytics`  
* Multi-Account (by Domain):  
  * Account: `finance`   
  * Database: `analytics_prod`  
* Multi-Account (Domain + Environment)  
  * Account: `finance_prod`   
  * Database: `analytics`

Additionally, object naming strategy typically adds one of these three as a suffix to the components:

* **Zone (DB)**: raw, curated, published (database level - covered in later workflows)  
* **Workload (WH):**  ingest, transform, bi  
* **Function (RL):** read, create, admin, adhoc

## Best Practices

While a singular object could have a very succinct name (EDW for Database, ETL for Warehouse, ADMIN for role), assume the account will grow over time to include multiple (10’s-100’s) databases, across multiple business units, requiring numerous isolated workload-specific warehouses, and segregated roles to restrict permissions.

* **Include components in object names:** Don’t just use the data product as the object name, include prefixes and suffixes   
* **Arrange the core components** for alphabetical sorting and clustering objects, by placing the most important & unconditional components first: `<domain>_<env>_<dataproduct>`, `<domain>_<dataproduct>_<env>`, or `<env>_<domain>_<dataproduct>`  
* **Abbreviate** components' names for enhanced viewability and less typing (3-8 characters): `sc` vs `supply_chain`, `prd` vs `production`, `cur` vs `curated`  
* **Underscores (snake_case)** to separate components, not to separate words in the component name: `sc_inv_prd_cur`  
* **Uppercase**: All names will appear in uppercase; Snowflake is case insensitive, so will always be displayed in uppercase (unless double-quoted "ProtectCase")  
* **Self-descriptive**: Names should be intuitive and decipherable for users with organization's institutional knowledge and each component of name providing clarity  
* **Don't suffix type:** to keep the object name short as possible, and since type is always contextually clear, don't suffix with `_DB`, `_WH`, or `_RL`

### Key considerations:

* **Account strategy agnostic:** The naming convention should be agnostic of singular vs. multi-account strategy   
  * Over time this strategy could change, and `org_usage` views bring together objects from all accounts  
  * so having globally unique names makes FinOps reporting across accounts easier (so account identifier doesn’t need to be included)  
* **Consistency**: Use the same pattern across account object types, and across data products  
* **Durability w/ Scalability**: Support growth of the data platform without requiring changing the naming convention  
  * Changing conventions or object names is extremely complex and risky once deployed into production  
* **Environment Deployment:** Roles are generally SCIM provisioned, but WH and DB may be deployed into upper environments.    
  * Since the object name contains the environment, it’s important to leverage deployment methods that externalize the environment name into {{jinja}} variables  
* **Succinct:** While Snowflake supports identifiers up to 255 characters, shorter names improve readability and usability  
  * Generally advise names be 30 characters or less, which can achieved by leveraging acronyms wherever possible  
* **Automation**: Enable programmatic resource management   
* **FinOps TAG alignment:** FinOps reporting will leverage global tags that should leverage the same components / values

## Considerations

### Database Considerations

* **Zone suffix:** in many cases, it is best to separate the stages of data processing into different database distinguished by zone  
  * Common zone examples are (bronze, silver, gold), (raw, curated, published), etc.  
  * Recommendation: for data products that wish to separate the stages, create separate databases w/ a zone as the suffix

### Warehouse Considerations

* **Workload suffix:** Isolating data processing or querying into separate warehouses allows for more optimal performance/costs  
  * Warehouses can be configured (sized) differently to best suit the workload they are responsible for  
  * Warehouses can also be associated with specific roles so that they can be used by only those functions  
  * Common workload examples are (ingest, transform, analytics, adhoc)  
  * Recommendation: separate the workloads within a data product by creating separate warehouses w/ a workload as the suffix  
    * Additionally, sometimes within a data product there will be multiple instances of a workload, either different tools or sizes, so those can be added to the warehouse name suffix to make very clear  
      * DO NOT include the specific size of the WH in the name as that likely will change over time (or with adaptive WH, no longer relevant)

### Role Considerations

* **Function suffix:** Within a data product there are several different functions that need to assigned to different users (human or service accounts).  Adopting the least privilege mindset, these functions should be encapsulated in distinct roles.  
  * Common function examples are (admin, create/deploy, write/ingest/transform, read, adhoc)  
  * Recommendation: for data products functions, create separate roles w/ a function as the suffix

## More Information

* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers) — Naming rules and conventions  
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database) — Database creation reference  
* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse) — Warehouse creation reference  
* [CREATE ROLE](https://docs.snowflake.com/en/sql-reference/sql/create-role) — Role creation reference  
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Tagging for governance and cost allocation

### Configuration Questions

#### What do you want to name your organization account? (`org_account_name`: text)
The Organization Account is a special account that provides centralized management capabilities for your Snowflake environment. Enter the name you want to use, or enter `NONE` if you do not want to create an organization account.  

**⚠️ Strong Recommendation: Create an Organization Account**  

We strongly recommend creating an Organization Account, even if you have selected a Single Account strategy. Here's why:  

* **Future-proofing:** If there's any potential for adding accounts later, having the Organization Account already set up makes expansion seamless  
* **Centralized features:** Access to organization-level views, billing, and governance features  
* **Easier migration:** Moving to a multi-account strategy later is significantly easier with an existing Organization Account  
* **No downside:** The Organization Account has minimal overhead and doesn't impact your single-account operations  

**For Multi-Account Strategies:** An Organization Account is **required**. It provides:  
* Centralized view of all accounts  
* Unified billing and cost management  
* Ability to create and manage child accounts programmatically  
* Organization-level policies and governance  

**Recommended Name:** `ORG`  

Since there can be only one Organization Account per organization, the name should clearly indicate this special purpose. We recommend simply naming it `ORG`.  

**Example URLs with name `ORG`:**  
* Custom org name: `https://ACME-ORG.snowflakecomputing.com`  
* System-generated with prefix: `https://XY12345-acme_ORG.snowflakecomputing.com`  
* System-generated without prefix: `https://XY12345-ORG.snowflakecomputing.com`  

**Requirements:**  
* Snowflake Enterprise Edition or higher  
* ORGADMIN role granted in the existing account  

**Enter `NONE` only if you are certain you will never need multi-account capabilities.**  

**More Information:**  
* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts)  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)  

#### What cloud region should host the Organization Account? (`org_account_region`: text)
  Select the Snowflake Region ID where your Organization Account will be created.  
  
  **How to find available regions:**  
  ```sql  
  -- List all available regions for your organization  
  SHOW REGIONS;  
  ```  
  
  **Key Considerations:**  
  * **Regulated Regions:** If your organization has accounts in a U.S. SnowGov Region, Snowflake recommends creating the Organization Account in that regulated region  
  * **Administrator Location:** Choose a region close to your platform administrators for lower latency  
  * **Primary Account Location:** Consider using the same region as your primary data account(s)  
  * **Data Residency:** While the Organization Account shouldn't contain business data, some organizations prefer to keep all accounts in the same geographic region  
  
  **Common Region IDs:**  
  * AWS US West 2 (Oregon): `AWS_US_WEST_2`  
  * AWS US East 1 (N. Virginia): `AWS_US_EAST_1`  
  * Azure East US 2: `AZURE_EASTUS2`  
  * GCP US Central 1: `GCP_US_CENTRAL1`  
  
  **Note:** If you omit REGION, the organization account is created in the same region as the account running the command.  
  
  **More Information:**  
  * [CREATE ORGANIZATION ACCOUNT](https://docs.snowflake.com/en/sql-reference/sql/create-organization-account)  
  * [Supported Cloud Regions](https://docs.snowflake.com/en/user-guide/intro-regions)  

#### What do you want to name the platform database? (`platform_database_name`: text)
**What is the Platform/Infrastructure Database?**  
The Infrastructure Database is a centralized "hub" database that houses platform-wide objects including FinOps tags, network rules, governance policies, and shared procedures. It is owned by the central platform team and shared across all accounts in multi-account deployments.  

**Recommended Naming Approach:**  
Use a name that clearly identifies this as a platform-owned, infrastructure-focused database. The format should be: `<domain>_<dataproduct>`  

* **Domain:** Use `plat` (short for "platform") or your platform team's acronym (e.g., `cdp`, `snow`, `data`)  
* **Data Product:** Use `infra` or another term indicating infrastructure purpose  

**Example:** `PLAT_INFRA` — clearly indicates Platform team ownership and Infrastructure purpose  

**Alternative Examples:**  
* `CDP_INFRA` — Cloud Data Platform Infrastructure  
* `SNOW_ADMIN` — Snowflake Administration  
* `DATA_PLATFORM` — Data Platform database  

**Important:** Choose carefully! This name will be referenced by hundreds of objects, policies, and procedures. Changing it later is extremely complex and risky.  

**More Information:**  
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  

#### What are your domain abbreviations? (`domain_list`: list)
**What is a Domain?**  
A domain represents a logical grouping of business functions, data, or ownership. Domains define boundaries for governance, cost allocation, and data stewardship.  

**How Domains Are Used:**  
Depending on your account strategy, domains appear at either the account level or database level:  
* Multi-Account (Domain-based): Each domain gets its own Snowflake account  
* Single Account: Domains appear as prefixes in database/warehouse/role names  

**Examples by Type:**  
* **Business Units:** `fin` (Finance), `mkt` (Marketing), `ops` (Operations), `hr` (Human Resources)  
* **Entities:** `retail`, `wholesale`, `mfg` (Manufacturing)  
* **Departments:** `sales`, `sc` (Supply Chain), `custsvc` (Customer Service)  
* **Technical Teams:** `data`, `plat` (Platform), `eng` (Engineering)  

**Best Practices:**  
* Use short abbreviations (3-8 characters) for readability  
* Avoid underscores within domain names—use concatenated abbreviations  
* Choose intuitive names that are self-descriptive to users  
* Consider future growth—add domains you may need later  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  

#### What is your Snowflake organization name? (`snowflake_org_name`: text)
Your Snowflake organization name is the first part of your account URL and connection identifiers. This is a required component of all Account Identifiers.  

**How to find your organization name:**  
Look at your current Snowflake URL. The organization name is the portion before the dash:  
* `https://**ACME**-prod.snowflakecomputing.com` → Organization name is `ACME`  
* `https://**XY12345**-prod.snowflakecomputing.com` → Organization name is `XY12345`  

**Types of Organization Names:**  
* **Custom Name:** A human-readable name like `ACME` or `INITECH` that was requested from Snowflake. These provide better branding and more readable URLs.  
* **System-Generated:** An auto-assigned alphanumeric code like `XY12345` or `AB98765`, created automatically during self-service signup.  

**To request a custom name:** If you have a system-generated name and want to change it, contact Snowflake Support or your account team. Custom names must be globally unique, start with a letter, and contain only letters and numbers.  

**More Information:**  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)  

#### What do you want to name the governance schema? (`governance_name`: text)
**What is the Governance Schema?**  
The Governance schema is created within the Infrastructure Database and contains objects related to security, compliance, and platform governance. This includes FinOps tags, network rules, audit views, and administrative procedures.  

**Recommended Name:** `GOVERNANCE`  

This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:  
* `ADMIN` — Administration  
* `SECURITY` — Security-focused objects  
* `PLATFORM` — Platform-level objects  

**Schema Configuration:**  
This schema will be created with **Managed Access** enabled, which means:  
* Only the schema owner (typically SYSADMIN) can grant privileges on objects  
* Prevents "shadow" security configurations where object creators grant their own access  
* Provides centralized control over who can access governance objects  

**Best Practice:** Use a simple, single-word name that represents the functional purpose.  

**More Information:**  
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)  
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)  

#### Will environment identifiers be required in account-level object names? (`require_env_in_objects`: multi-select)
**What is an Environment?**  
An environment represents an SDLC stage—for example, `dev` (Development), `test` (Testing), or `prod` (Production).  

**When to Require Environment in Object Names:**  
* **Yes (Recommended for Single Account or Multi-Account by Domain):** Environment is not at the account level, so it should be in object names: `FIN_ANALYTICS_PROD`  
* **No (Multi-Account by Environment):** If each environment has its own account, the environment is already clear from context: `FIN_ANALYTICS`  

**Impact:**  
* Including environment makes objects self-describing and globally unique  
* Essential for deployment automation—allows the same templates to deploy to different environments  
* Makes object names longer but enables clear identification in monitoring and cost reports  

**Recommendation:** Include environment unless you're using a Multi-Account (Environment-based) strategy where each account represents a single environment.  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers) 
**Options:**
- Yes
- No

#### What account strategy do you wish to implement? (`account_strategy`: multi-select)
Choose the account strategy that best fits your organization. Your choice determines how domain (business unit/entity) and environment are organized:  

**Single Account:**  
* Best for: Small to medium organizations, centralized teams, simpler governance  
* Naming: Domain + Environment + Data Product at database level  
* Pros: Lower operational overhead, easier cross-database queries, centralized management  
* Cons: Less isolation, shared resource limits, single security boundary  
* Recommendation: Consider setting up an organization account even for single-account deployments to enable future growth  

**Multi-Account (Environment-based):**  
* Best for: Organizations requiring strong environment isolation (dev/test/prod)  
* Naming: Environment at account level, Domain + Data Product at database level  
* Pros: Complete environment isolation, independent security controls, separate billing  
* Cons: More complex data sharing, higher operational overhead  
* Requirement: Organization account required  

**Multi-Account (Domain-based):**  
* Best for: Large enterprises with autonomous business units/domains  
* Naming: Domain at account level, Environment + Data Product at database level  
* Pros: Clear cost allocation per domain, independent governance, domain autonomy  
* Cons: Higher complexity, requires data sharing for cross-domain analytics  
* Requirement: Organization account required  

**Multi-Account (Domain + Environment):**  
* Best for: Large organizations needing both domain and environment isolation  
* Naming: Domain + Environment at account level, Data Product at database level  
* Pros: Maximum isolation, clear ownership and environment separation  
* Cons: Highest complexity and operational overhead, most accounts to manage  
* Requirement: Organization account required  

**More Information:**  
* [Organizations](https://docs.snowflake.com/en/user-guide/organizations)  
* [Managing Multiple Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) 
**Options:**
- Single Account
- Multi-Account (Environment-based)
- Multi-Account (Domain-based)
- Multi-Account (Domain \+ Environment)

#### What core component ordering will be used for account-level object names? (`object_component_order`: multi-select)
**Why Order Matters:**  
Snowflake displays objects alphabetically. The component order determines how objects cluster together in Snowsight, BI tools, and queries.  

**Option 1: `<domain>_<env>_<dataproduct>`**  
* Objects cluster by **domain first**, then by environment  
* All Finance objects together, all Marketing objects together  
* Example: `FIN_PROD_ANALYTICS`, `FIN_DEV_ANALYTICS`, `MKT_PROD_CAMPAIGNS`  
* Best for: Organizations where domain ownership is primary  

**Option 2: `<domain>_<dataproduct>_<env>`**  
* Objects cluster by **domain first**, then by data product  
* All Finance Analytics together across environments  
* Example: `FIN_ANALYTICS_PROD`, `FIN_ANALYTICS_DEV`, `MKT_CAMPAIGNS_PROD`  
* Best for: Data product-centric organizations  

**Option 3: `<env>_<domain>_<dataproduct>`**  
* Objects cluster by **environment first**  
* All Production objects together, all Development objects together  
* Example: `PROD_FIN_ANALYTICS`, `PROD_MKT_CAMPAIGNS`, `DEV_FIN_ANALYTICS`  
* Best for: Operations teams focused on environment-based management  

**Recommendation:** Most organizations prefer `<domain>_<env>_<dataproduct>` or `<domain>_<dataproduct>_<env>` for domain-centric clustering.  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  
**Options:**
- <domain>_<env>_<dataproduct>
- <domain>_<dataproduct>_<env>
- <env>_<domain>_<dataproduct>

#### What abbreviations will you use for environments? (`environment_list`: list)
**What is an Environment?**  
An environment represents a stage in the Software Development Lifecycle (SDLC). Environments isolate data and applications based on their maturity and stability.  

**How Environments Are Used:**  
Depending on your account strategy, environments appear at either the account level or database level:  
* Multi-Account (Environment-based): Each environment gets its own Snowflake account  
* Single Account: Environments appear as suffixes in database/warehouse/role names  

**Common Environment Abbreviations:**  
* `dev` — Development: Where developers build and test code  
* `test` or `qa` — Testing/QA: For quality assurance and integration testing  
* `stg` or `stage` — Staging: Pre-production environment mirroring production  
* `prod` — Production: Live environment serving end users  
* `sbx` — Sandbox: Isolated environments for experimentation  
* `uat` — User Acceptance Testing: For business user validation  
* `dr` — Disaster Recovery: Failover environment for business continuity  

**Best Practices:**  
* Use short abbreviations (3-4 characters) for consistency  
* Keep abbreviations intuitive and recognizable  
* Include all environments you'll need—adding later requires renaming objects  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  

#### What Snowflake edition will you use for the Organization Account? (`org_account_edition`: multi-select)
The Organization Account requires **Enterprise Edition or higher**. Standard Edition does not support Organization Account functionality.  

**Enterprise Edition** (Recommended):  
* Full organization management capabilities  
* Multi-cluster warehouses for concurrency scaling  
* Column-level security and up to 90-day Time Travel  
* Failover/Failback for business continuity  
* Best for: Most organizations  

**Business Critical Edition:**  
* Everything in Enterprise, plus:  
* HIPAA and PCI DSS compliance support  
* Customer-managed encryption keys (Tri-Secret Secure)  
* Private connectivity (AWS PrivateLink, Azure Private Link, GCP Private Service Connect)  
* Best for: Highly regulated industries or when the Organization Account needs to meet strict compliance requirements  

**Recommendation:** Enterprise Edition is typically sufficient for the Organization Account since it primarily serves administrative purposes rather than hosting sensitive business data.  

**More Information:**  
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions)  
**Options:**
- ENTERPRISE
- BUSINESS_CRITICAL

#### What prefix (if any) should be added to all account names? (`account_name_prefix`: text)
An account name prefix is an optional string added to the beginning of every account name for consistency and organization identification.  

**When to use a prefix:**  
* If your organization name is system-generated (e.g., `XY12345`) and you want your company name visible in account names  
* If you want to enforce consistent naming across all accounts  
* If you have multiple organizations or business units sharing Snowflake and need differentiation  

**Example with prefix:**  
* Prefix: `acme`  
* Account names become: `acme_prod`, `acme_dev`, `acme_finance`  
* URL: `https://XY12345-acme_prod.snowflakecomputing.com`  

**Example without prefix:**  
* Account names: `prod`, `dev`, `finance`  
* URL: `https://ACME-prod.snowflakecomputing.com`  

**Recommendations:**  
* If you have a **custom organization name** (like `ACME`), a prefix is typically unnecessary since your identity is already in the URL  
* If you have a **system-generated name**, consider using an abbreviated company name as a prefix  
* Keep prefixes short (3-8 characters) with no underscores  

**Enter `NONE` if you do not want to use an account name prefix.**  

**More Information:**  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)

#### Will domain identifiers be required in account-level object names? (`require_domain_in_objects`: multi-select)
**What is a Domain?**  
A domain is a logical grouping representing a business unit, entity, or department—for example, `fin` (Finance), `mkt` (Marketing), or `ops` (Operations).  

**When to Require Domain in Object Names:**  
* **Yes (Recommended for Single Account or Multi-Account by Environment):** Domain is not at the account level, so it should be in object names for clarity: `FIN_ANALYTICS_PROD`  
* **No (Multi-Account by Domain):** If each domain has its own account, the domain is already clear from context, so object names can be simpler: `ANALYTICS_PROD`  

**Impact:**  
* Including domain makes objects self-describing and globally unique across accounts  
* Helps with FinOps reporting when aggregating usage across accounts  
* Makes object names longer but more informative  

**Recommendation:** Include domain unless you're using a Multi-Account (Domain-based) strategy where each account represents a single domain.  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  
**Options:**
- Yes
- No

#### Will data product identifiers be required in account-level object names? (`require_dataproduct_in_objects`: multi-select)
**What is a Data Product?**  
A data product is a self-contained unit of data that serves a specific business purpose—for example, `analytics`, `reporting`, `ingest`, or `customer360`.  

**When to Require Data Product in Names:**  
* **Yes:** If you expect multiple data products within the same domain/environment. This creates clear separation: `FIN_PROD_ANALYTICS_READ` vs `FIN_PROD_REPORTING_READ`  
* **No:** If each domain typically has only one primary data product, or if you prefer simpler names like `FIN_PROD_READ`  

**Impact:**  
* Databases, warehouses, and roles will include/exclude the data product identifier  
* Example with data product: `MKT_CAMPAIGNS_PROD_TRANSFORM`  
* Example without: `MKT_PROD_TRANSFORM`  

**Recommendation:** Choose "Yes" for organizations with multiple data products per domain. This provides better organization as your platform scales.  

**More Information:**  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  
**Options:**
- Yes
- No
