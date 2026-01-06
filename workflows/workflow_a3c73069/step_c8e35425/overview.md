### Overview
This is a critical security step. For each schema you create, you will also create a set of granular, schema-specific database roles. These roles are granted privileges directly on the schema and its objects. They form the lowest level of our RBAC hierarchy.

### Decisions to Make
You will create a set of access roles for each schema based on the access levels you've chosen for your Data Product (e.g., Read, Write, Create).
* **Role Naming Pattern:** `{DATABASE_NAME}.{STEM}_{PURPOSE}_{ACCESS}_ROLE`
* **Example:** For a `READ` role on the `ORDERS_UTILS` schema in the `DEV_SALESFORCE_CURATED` database, the role name would be: `DEV_SALESFORCE_CURATED.ORDERS_UTILS_READ_ROLE`

Once the roles are created, you must grant them the appropriate privileges on the schema.

### Personas to Involve
* **Platform Owner:** Creates the roles and applies the grants.
* **Security Lead:** Audits the privileges to ensure they adhere to the principle of least privilege.

### Best Practices & Recommendations
* **Consistent Naming:** Strictly adhere to the `Stem_Purpose` naming convention to maintain a well-organized and intuitive data environment.
* **Granular Roles:** Create the schema-level access roles immediately upon schema creation. This ensures that a secure foundation is in place before any data is loaded.
* **Role Hierarchy:** Grant the newly created schema-level roles to their corresponding database-level access roles (e.g., grant `ORDERS_UTILS_READ_ROLE` to the database's `READ` role). This crucial step connects the schema-level permissions into the broader database access model.

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

#### Please provide the list of schema "stems" you’d like to use for your schema naming. (`stem_list`: list)
The **Stem** is a required component of a schema name that identifies the specific "Subject Area" (e.g., customers, products) or "Business Process" (e.g., invoicing, payroll) that the data describes. It provides a clear, logical grouping for the tables and views within a database, making the data landscape easier to navigate and understand.

#### Guidance:
* The **Stem** should be a noun for a "Subject Area" or verb-based for a "Business Process".
* **Subject Area Examples:** `customers`, `products`, `employees`, `orders`, `suppliers`.
* **Business Process Examples:** `invoicing`, `procurement`, `inventory_management`, `accounts_payable`, `payroll`.
* Enter one or more stems that accurately categorize the data you plan to store. For example, a schema containing curated data about customer orders could be named `ORDERS_UTILS`, where `ORDERS` is the stem.

#### Please provide the list of schema "purposes" you’d like to use for your schema naming. (`purpose_list`: list)
The **Purpose** is the required first component of a schema name that describes the type of data it contains. This component is crucial for organizing your data according to its stage in the analytics lifecycle, aligning with concepts like the medallion architecture (Bronze, Silver, Gold). It provides immediate context about the data's quality, structure, and intended use.

#### Guidance:
* The **Purpose** should clearly indicate the data's role.
* Consider all stages of your data pipeline, from initial ingestion to final business consumption.
* Standard purposes include:
  * **RAW:** For schemas containing raw, unaltered data directly from source systems (Bronze).
  * **STG** (Staging): For schemas holding transient data that is being cleaned, transformed, and prepared for loading into marts (Silver).
  * **MARTS**: For schemas with curated, business-ready data, often in dimensional models for analytics and reporting (Gold).
  * **UTILS**: For utility schemas that contain operational objects like pipes, tasks, and streams rather than user data.
