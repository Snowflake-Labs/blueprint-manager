In this step, you'll define the **domains** (eg. business units or entities) and/or **environments** (eg. dev, test, prod) that will structure your Snowflake accounts. These choices directly impact how your accounts are named and organized. In subsequent steps, they'll also be used to establish the foundation for all object naming in your Snowflake platform, including databases, warehouses, and roles in subsequent steps.

## Account Context

**⚠️ Verify you are in the correct account before proceeding:**
- If you created an Organization Account in the Create Organization Account step, you should now be **logged into that Organization Account**
- If you did not create an Organization Account, continue in your current account

All remaining steps in this workflow will be executed from this account.

## Why is this important?

Consistent domain and environment definitions are essential for organizing your Snowflake platform at scale. These naming components flow through to accounts, databases, warehouses, and roles—creating a unified taxonomy that enables clear cost allocation, simplified governance, and intuitive navigation for all users. Establishing these standards early prevents naming inconsistencies that become increasingly difficult to correct as your platform grows.

## External Prerequisites

N/A

## Key Concepts

Customers with plans to migrate/develop multiple **Data Products** from across their enterprise into the Snowflake data platform will typically organize them by how the business is organized e.g., by **Domains**. Additionally, the software development lifecycle (SLDC) of a data product requires separating the phases into separate **Environments**:

* **Domain**: Business unit/entity, division, or department (e.g., `fin`, `mkt`, `data_eng`)  
* **Environment**: An SDLC stage representing different levels of your development lifecycle (e.g., `dev`, `tst`, `prd`)  
* **Data Product:** a self-contained unit of data that serves a specific business purpose (e.g., `sales_analytics`, `fin_reports`). In Snowflake, Data Products are built, used, and managed through a series of objects such as Databases, Warehouses, and Roles.

Depending on your account strategy, the names you select for these different components may appear at either the Account Level or Data Product Level (databases, warehouses, roles). Let's look at a simple example:

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

Since objects are alphabetically sorted, this also helps to organize accounts, databases, warehouses, and roles when seen in Snowsight and BI tools. Additionally, these components (and others) are going to facilitate FinOps chargeback/showback processes through the use of tags. 

## Best Practices

While a singular object could have a very succinct name (EDW for a Database, ETL for Warehouse, ADMIN for role), assume the account will grow over time to include multiple (10’s-100’s) databases, across multiple business units, requiring numerous isolated workload-specific warehouses, and segregated roles to restrict permissions.

* **Abbreviate** components' names for enhanced viewability and less typing (3-8 characters): `sc` vs `supply_chain`, `prd` vs `production`, `cur` vs `curated`  
* **Underscores (snake_case)** DO NOT use underscores for multi-word domains; the underscore separator should be used to separate components of the name only:  
  * e.g., for Warehouse the name would be `[domain_]dataproduct[_env][_zone]`  
* **Uppercase**: All names will appear in uppercase; Snowflake is case insensitive, so will always be displayed in uppercase (unless double-quoted “ProtectCase”)  
* **Self-descriptive**: Names should be intuitive and decipherable for users with organizational knowledge and each component of name providing clarity

## Domain Options

Domains is a generalized construct to separate data into separate accounts and/or data products. **Examples by Type:**

* **Business Units**: finance, marketing, operations, hr  
* **Entities**: retail, wholesale, manufacturing  
* **Departments**: sales, supplychain, customersvc

## Environment Options

Environment is a generalized construct to separate data into separate accounts and/or data products. **Examples by Type:**

* **Development**: dev  
* **Testing / QA**: test or qa  
* **Staging**: stg or stage  
* **Production**: prod  
* **Sandbox**: sbx

## More Information

* [Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Overview of Snowflake organizations and accounts  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers) — Naming rules and conventions for Snowflake objects  
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Using tags for governance and cost allocation

### Configuration Questions

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
