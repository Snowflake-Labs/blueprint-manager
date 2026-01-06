### Overview
A consistent naming convention for schemas is crucial for ensuring that data is organized logically and is easily discoverable. We recommend a two-component pattern that clearly describes both the schema's purpose and the data it holds. This step also covers key schema properties that will be enabled by default.

### Decisions to Make
The primary decision is to adopt the standardized naming pattern for all schemas:

`{STEM}_{PURPOSE}`

The name is comprised of two distinct components:
* **`{STEM}`:** Identifies the specific "Subject Area" (a noun, like `customers`) or "Business Process" (often verb-based, like `invoicing`) that the data describes.
  * **Subject Area Examples:** `customers`, `products`, `employees`, `orders`, `suppliers`
  * **Business Process Examples:** `invoicing`, `procurement`, `inventory_management`, `accounts_payable`, `payroll`

* **`{PURPOSE}`:** Indicates the data's stage in the processing pipeline or its intended use case.
  * **Examples:**
    * `raw`: For ingesting source data with minimal to no transformations. This is the landing zone.
    * `stage`: For cleaning, preparing, integrating, and transforming raw data before it's modeled for consumption.
    * `marts`: For curated, aggregated, and business-ready data, often modeled as star schemas for analytics and reporting.
    * `serving`: For final, refined data views intended for direct consumption by BI tools or applications.
    * `utils`: For housing utility objects like user-defined functions (UDFs), file formats, or shared procedures.
    * `sandbox`: For individual users or teams to perform ad-hoc analysis and experimentation without impacting production models.

**Combined Example:** A schema containing curated, business-ready data about customer orders would be named `ORDERS_UTILS`.

* **Data Retention Time:** Set the `DATA_RETENTION_TIME_IN_DAYS` parameter. This determines the number of days for which Snowflake's Time Travel feature will be active, allowing you to recover data that has been changed or deleted.

### Key Properties (Enabled by Default):
* **Managed Access:** Your schemas will be created as "Managed Access" schemas. This is a best practice that centralizes privilege management to the schema owner, preventing object owners from granting access independently and ensuring a more secure and auditable environment.

* **Tagging:** For enhanced governance and FinOps, tags will be automatically created and applied to the schema based on the provided `{STEM}` and `{PURPOSE}` name components.

### Personas to Involve
* **Data Product Owner:** Defines the business context and helps choose the appropriate `Stem`.
* **Platform Owner:** Enforces the naming convention across the environment.
* **Data Architect:** Helps design the overall data flow and determines the correct `Purpose`.

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
