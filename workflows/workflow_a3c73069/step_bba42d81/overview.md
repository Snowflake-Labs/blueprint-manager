### Overview
Account-level functional roles represent the business functions or types of access related to a Data Product (e.g., "read-only access to Salesforce data"). These roles do not get permissions on tables or views directly. Instead, they serve as containers for more granular database-level roles.

### Decisions to Make
The primary decision is to establish a consistent naming convention and choose the set of roles that best fits your access control needs.

First, all functional roles should follow a standard naming pattern:

`{DATA_PRODUCT}_{ACCESS_LEVEL}_ROLE`
* `{DATA_PRODUCT}`: The name of the Data Product this role governs (e.g., `SALESFORCE`, `HUBSPOT`, `ERP`).

Next, you will decide on the overall RBAC (Role-Based Access Control) approach for your data products. The chosen approach will determine which `{ACCESS_LEVEL}` roles you create. The options are:
* **Owner + Reader:** This simple approach provides two distinct roles: `OWNER` for managing the data product and `READER` for consuming data. This is suitable for environments where data creation is handled by a small, centralized team.
* **Owner + Create/Write + Reader:** This approach introduces a combined `CREATE_WRITE` role. This is useful when you have a clear distinction between data producers (who create and write) and data consumers (who only read), but the creation and writing functions are often performed by the same people or processes.
* **Owner + Create + Write + Reader:** This approach provides the most granular control by separating access into `CREATE` and `WRITE` roles. This is ideal for complex environments where different users may have permission to create objects but not write data, or vice versa. It offers greater flexibility but also increases the number of roles to manage.

### Example Role Names:
* `SALESFORCE_OWNER_ROLE`
* `SALESFORCE_READER_ROLE`
* `SALESFORCE_CREATE_WRITE_ROLE`

### Personas to Involve
* **Data Product Owner:** Defines the access requirements for their data product.
* **Platform Owner:** Implements the role structure.
* **Security Lead:** Ensures the roles adhere to the principle of least privilege.

### Configuration Questions

#### Please provide the list of data products you’d like to use for your database naming. (`dataproduct_list`: list)
The **Data Product** is the required core component that identifies a logical grouping of data. It ensures that every database can be clearly tied to a specific business initiative or dataset. A single Data Product (e.g., `PAYROLL`) could consist of databases across multiple accounts and environments, all linked by this common name. 

### Guidance:
* This part of the name must always be provided. 
* Think of a data product as a distinct dataset or business initiative, such as 'payroll', 'sap', or 'jdoe_sandbox'. 
* Enter one or more data products that will logically group your data. 

#### Please provide the list of zones you’d like to use for your database naming. (`zone_list`: list)
The **Zone** is an optional component that represents a specific stage in your data's lifecycle. It helps differentiate between datasets at various levels of transformation and readiness. For instance, data might land in a 'RAW' zone before it is cleaned and modeled for analytics in a 'CURATED' zone.

### Guidance:
* This part of the name is optional and should only be used if it aligns with your data strategy.
* Consider the different states your data will be in, from ingestion to final consumption.
* Common examples include:
  * **RAW**: For data in its original, unaltered format.
  * **STG** (Staging): For intermediate data undergoing cleaning and transformation.
  * **CURATED**: For enriched, modeled, and production-ready data.

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

#### Please select the RBAC model that best fits your organization's needs for account-level roles. (`functional_role_approach`: multi-select)
This determines how granular the separation of duties will be for your data products. The choice impacts how roles are structured for creating, writing to, and reading from your databases. Selecting the right model—**Small**, **Medium**, or **Large**—is key to balancing operational speed with governance and security as your organization scales.

**Guidance:**
* Use the table below to help determine which approach is the best fit for your business needs.

* **Small:** Best for initial proofs-of-concept, sandboxes, or new production environments with fewer than 10 users where speed is more critical than complex structure.

* **Medium:** A good fit for growing organizations (10-50 users) that require more structure than the "Small" model but are not yet at the enterprise level.

* **Large:** Necessary for enterprise-level organizations (50+ users), multi-tenant SaaS applications, or those with heavy compliance requirements (like SOX or HIPAA) that demand maximum isolation and audibility.

| Scenario | Recommended Approach | Rationale |
| :--- | :--- | :--- |
| POC/Sandbox (< 3 months) | Small | Speed over structure |
| New production (< 10 users) | Small | Balance & growth-ready |
| Growing org (10-50 users) | Medium | Structured but manageable |
| Enterprise (50+ users) | Large | Full governance needed |
| Multi-tenant SaaS | Large | Maximum isolation required |
| Compliance-heavy (SOX, HIPAA) | Large | Audit requirements |
**Options:**
- Small – Owner + Reader
- Medium – Owner + Create/Write + Reader
- Large – Owner + Create + Write + Reader
