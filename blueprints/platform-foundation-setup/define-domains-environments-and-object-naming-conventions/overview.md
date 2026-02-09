In this step, you'll define the organizational taxonomy and naming standards that structure your entire Snowflake platform. You will create tags that will be added to the infrastructure database and schema created in the previous step:

1. **DOMAIN Tag** — With allowed values representing your business units, departments, or entities (e.g., FIN, MKT, HR)
2. **ENVIRONMENT Tag** — With allowed values representing your Software Development Lifecycle (SDLC) stages (e.g., DEV, TEST, PROD)
3. **Component Ordering Standard** — The sequence in which Domain, Environment, and Data Product appear in object names
4. **Additional Tags** — Tags where you can optionally define values in later workflows:
   - `DATAPRODUCT` — Identifies the specific data product (values defined per data product)
   - `WORKLOAD` — Classifies warehouse workload types (e.g., INGEST, TRANSFORM, BI)
   - `ZONE` — Classifies database data zones (e.g., RAW, CURATED, PUBLISHED)
   - `DATA_CLASSIFICATION` — Indicates data sensitivity level (e.g., PUBLIC, CONFIDENTIAL)

Depending on your account strategy, Domain and Environment values will appear at either the **account level** (in account names) or **database object level** (in database, warehouse, and role names). The naming convention you select here will be applied consistently across all accounts and data products in subsequent workflows.

## Why is this important?

Consistent domain, environment, and naming standards are essential for organizing your Snowflake platform at scale. These standards:

* **Simplify navigation** — Consistent naming makes objects easy to find in Snowsight, BI tools, and queries
* **Enable FinOps cost allocation** — Tags allow you to track and allocate costs by business unit and environment
* **Support governance** — Clear ownership boundaries defined by domain enable effective data stewardship
* **Future-proof your platform** — Establishing standards now prevents naming inconsistencies that become difficult to correct as your platform grows

Once objects are deployed to production and referenced by applications and users, renaming can become complex and risky, so we recommend planning carefully.

**Why create additional tags (DATAPRODUCT, WORKLOAD, ZONE, DATA_CLASSIFICATION) now?**

We create all six tags in this step—even though you're only defining allowed values for DOMAIN and ENVIRONMENT tags for several important reasons:

* **Centralized governance** — All tags will be stored in your newly created Infrastructure Database and Governance Schema, ensuring consistent management
* **Immediate availability** — When you create data products in subsequent workflows, these tags are already available for use
* **Naming alignment** — Object naming components align directly with tags for consistent cost reporting

## Account Context

This step should be executed in your [Organization Account](https://docs.snowflake.com/en/user-guide/organization-accounts) (if created) or your primary account.

## Key Concepts

[**Object Identifiers**](https://docs.snowflake.com/en/sql-reference/identifiers), often simply referred to as object names, are used to identify first-class “named” objects in Snowflake such as accounts, databases, and schemas. In this application, we'll use [**tags**](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) to help standardize object names throughout your account(s). 

A [**tag**](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) is a schema-level object that can be assigned to another Snowflake object. Tags are stored as key-value pairs, where the tag name is the key and you associate a string value when assigning the tag to an object. For example, you might assign the tag `DOMAIN` with value `FIN` to a database to indicate it belongs to the Finance business unit.

Key characteristics of tags in Snowflake:
* **Flexible assignment** — A single tag can be assigned to different object types simultaneously (e.g., a warehouse and a database)
* **Multiple tags per object** — An object can have up to 50 tags assigned at the same time
* **Tag inheritance** — Tags are [inherited](https://docs.snowflake.com/en/user-guide/object-tagging/inheritance) down the securable objects hierarchy—for example, a tag set on a database can be inherited by schemas and tables within it

Allowed Values vs. Any Value:

When creating a tag, you can optionally specify `ALLOWED_VALUES` to restrict which string values can be assigned:

* **Tags with ALLOWED_VALUES** — Only the specified values can be used when assigning the tag. This enforces consistency and prevents typos or unauthorized values. For example, the DOMAIN tag might only allow `FIN`, `MKT`, `OPS`—any attempt to assign `FINANCE` or `finance` would fail.

* **Tags without ALLOWED_VALUES** — Any string value can be used when assigning the tag. This provides flexibility when values aren't known in advance or vary widely across use cases.

In this workflow:
* `DOMAIN` and `ENVIRONMENT` tags use **ALLOWED_VALUES** based on your selections—ensuring all objects use consistent, pre-approved values for cost allocation
* `DATAPRODUCT`, `WORKLOAD`, `ZONE`, and `DATA_CLASSIFICATION` tags accept **any value**—allowing flexibility as these values are defined per data product in later workflows

## Best Practices

**Recommended Object Naming Strategy**

We recommend that account and database objects names consist of the following three core components: 

* **Domain** — Business unit, entity, or department (e.g., FIN, MKT, OPS, HR). Defines ownership boundaries for governance and cost allocation.
* **Environment** — Software Development Lifecycle (SDLC) stage representing different levels of your development lifecycle (e.g., DEV, TEST, PROD)
* **Data Product** — A self-contained unit of data serving a specific business purpose (e.g., ANALYTICS, REPORTING). Defined in later workflows.

How the naming components are applied depends on your account strategy. Below is a simple example where:
* **Domain** = Fin
* **Environment** = Prod
* **Data Product** = Analytics

| Strategy | Account Name | Database Name |
|----------|--------------|---------------|
| Single Account | N/A | `FIN_ANALYTICS_PROD` |
| Multi-Account (Environment) | `PROD` | `FIN_ANALYTICS` |
| Multi-Account (Domain) | `FIN` | `ANALYTICS_PROD` |
| Multi-Account (Domain + Environment) | `FIN_PROD` | `ANALYTICS` |

**Component Naming Best Practices**

* **Uppercase** — All names display in uppercase; Snowflake is case-insensitive
* **Abbreviate** — Use 3-8 character abbreviations for readability (e.g., `SC` vs `SUPPLY_CHAIN`, `PRD` vs `PRODUCTION`)
* **No underscores within components** — Use underscores only to separate components names, not within component names
* **Self-descriptive** — Names should be intuitive for users with organizational knowledge
* **30 characters max** — Keep names under 30 characters for usability
* **No type suffixes** — Don't add `_DB`, `_WH`, or `_RL` to object names; these will be redundant in context

**Component Order Considerations**

* Objects are displayed alphabetically in Snowsight, IDEs, and BI tools
* Place the most important grouping component first
* Most organizations prefer domain-first ordering for business-centric clustering

**Additional Naming Components (Applied in Later Workflows)**

Beyond the three core components (Domain, Environment, Data Product), object names typically include an additional suffix based on the object type. These suffixes align with the additional tags (ZONE, WORKLOAD) created in this step:

*Database Naming — Zone Suffix*

In many cases, it's best to separate the stages of data processing into different databases distinguished by zone:
* Common zone examples: `RAW`, `CURATED`, `PUBLISHED` (or `BRONZE`, `SILVER`, `GOLD`)
* **Recommendation:** For data products that separate processing stages, create separate databases with a zone suffix
* Example: `FIN_ANALYTICS_PROD_RAW`, `FIN_ANALYTICS_PROD_CURATED`

*Warehouse Naming — Workload Suffix*

Isolating data processing or querying into separate warehouses allows for optimal performance and cost management:
* Warehouses can be sized differently to suit specific workloads
* Warehouses can be associated with specific roles for access control
* Common workload examples: `INGEST`, `TRANSFORM`, `BI`, `ADHOC`, `ML`
* **Recommendation:** Separate workloads within a data product by creating warehouses with a workload suffix
* Example: `FIN_ANALYTICS_PROD_TRANSFORM`, `FIN_ANALYTICS_PROD_BI`

## **More Information**

* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers) — Naming rules and conventions
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Using tags for governance and cost allocation
* [Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Overview of Snowflake organizations and accounts

### Configuration Questions

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
