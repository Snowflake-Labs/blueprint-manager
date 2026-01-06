In this step you'll create an Infrastructure Database. A centralized **Infrastructure Database** is a cornerstone of the Snowflake Data Platform. It serves as the primary repository for platform-wide objects, including FinOps TAGs, Network Rules, and shared procedures.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account. 

## Why is this important?

By housing these objects in a single, dedicated database, you ensure that governance is consistent across your entire organization. In multi-account environments, this database can be shared from your Organization Account to child accounts, ensuring that every business unit uses the same standardized metadata and security boundaries.

## External Prerequisites

* **Organization Prefix:** Decide on a consistent prefix (e.g., `PLAT`, `CDP`, `SNOW`) that represents your organization.  
* **Platform Team Domain:** Define the acronym for the team that will own these central objects (e.g., `CDP` for Cloud Data Platform).

## Considerations

* **Unification via Prefixes:** While the prefix can be any string of your choosing, the purpose of a consistent and meaningful prefix is to establish a name that unifies all accounts and objects within your organization.  
* **Global Uniqueness:** While Snowflake does not validate the global uniqueness of a database name, it is highly recommended to specify a name that represents your organization to prevent collisions during future replication or sharing.  
* **Ownership Identification:** The central Snowflake platform team will generally own certain account-level objects; therefore, it is important to use the **Platform Domain** acronym in the naming convention to clearly identify platform-owned objects versus business-unit-owned objects.  
* **Managed Access:** Using Managed Access for schemas ensures that only the Platform Team (via the `SECURITYADMIN` or `SYSADMIN` roles) can grant privileges, preventing "shadow" security configurations.

## Key Concepts

* **Platform Domain:** A designated acronym (e.g., `plat`, `snow`, `cdp`) used to identify the central platform team and distinguish their objects from those of other business domains.  
* **Infrastructure Database:** A central "hub" database for metadata, security, and administrative objects.  
* **Managed Access Schema:** A security model where the schema owner controls all object privileges, rather than individual object creators.

## Best Practices

* **Standardize Early:** Define your infrastructure naming now. It is difficult to change once hundreds of objects and policies are referencing it.  
* **Consistent Prefixes:** Use a prefix that unifies all accounts within the organization, making it obvious which objects belong to the central platform team.  
* **Least Privilege:** Use the custom functional roles created in this step to perform platform maintenance instead of using the highly-privileged `ACCOUNTADMIN` role.

## How to Test

* Verify database existence: `SHOW DATABASES LIKE '{{ platform_database_name }}';`  
* Confirm Managed Access status: `SHOW SCHEMAS IN DATABASE {{ platform_database_name }};` (Verify the `governance` schema shows `TRUE` for `is_managed_access`).

## More Information

* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database) — SQL command reference  
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema) — SQL command reference  
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas) — Centralized privilege management  
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Using tags for governance  
* [Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Sharing objects across accounts

### Configuration Questions

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
