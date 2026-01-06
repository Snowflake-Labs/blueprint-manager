### Overview
A standardized naming convention for databases is crucial for creating a logical and easily navigable data landscape. It provides instant context about the data's source, its stage in the processing pipeline (e.g., raw, curated), and its business domain. This consistency is vital for data governance, security, and enabling self-service analytics.

A key principle is to **avoid repeating name components already defined at the account level**. For example, if you have a dedicated `PROD` account, you do not need to include PROD in the database name. This approach also simplifies code reusability across environments; deployment scripts can reference the same database name (e.g., `CURATED_ERP_FINANCE_AR`) without needing to change it for each environment, which prevents potential mistakes during deployments.

### Decisions to Make
The naming pattern for your databases is flexible and should be defined based on the order of importance that best suits your organization. A key consideration is that user interfaces, including Snowsight, typically list databases in alphanumeric order. Therefore, the order of the name components can be used as a deliberate strategy for grouping and organizing your databases visually.
The recommended name components are:
* **`ENVIRONMENT`** (_Optional_): The stage of the development lifecycle (e.g., `PROD`, `DEV`, `TEST`, `QA`).
* **`DOMAIN`** (_Optional_): The business area or function the data belongs to (e.g., `FINANCE`, `HR`, `MARKETING`, `SALES`).
* **`DATA_PRODUCT`** (_Required_): This is the core component that identifies a logical grouping of data. A single Data Product (e.g., `PAYROLL`) could consist of databases across multiple accounts and environments, all tied together by this name. **This part of the name should always be provided.**
* **`ZONE`** (_Optional_): Represents the stage of the data in its lifecycle. Common zones include:
  * `RAW`: For data ingested in its original, untransformed state.
  * `STAGING`: For intermediate data processing and transformation.
  * `CURATED`: For cleaned, modeled, and production-ready data intended for end-users.

The optional components allow for flexibility. For example, a temporary sandbox database may only need a `DATA_PRODUCT` name, like `JDOE_SANDBOX`.

#### Example Names (based on different ordering strategies):
* `FINANCE_ERP_RAW` (Pattern: `{DOMAIN}_{DATA_PRODUCT}_{ZONE}`)
* `PAYROLL_HR_CURATED` (Pattern: `{DATA_PRODUCT}_{DOMAIN}_{ZONE}`)
* `RAW_MARKETING_HUBSPOT` (Pattern: `{ZONE}_{DOMAIN}_{DATA_PRODUCT}`)

### Personas to Involve
* **Data Architect:** Defines the overall data organization and naming standards.
* **Data Product Owner:** Owns the data product and provides the business context for naming.
* **Platform Owner:** Ensures the naming convention is implemented consistently.

### Best Practices & Recommendations
* **Mandate the `DATA_PRODUCT` Component:** This ensures every database can be logically tied to a business initiative or dataset.
* **Document Your Conventions:** Maintain a central document or data dictionary that defines your chosen naming pattern and the values for each component to ensure consistency across teams.
* **Use Underscores:** Use underscores (`_`) as separators for clarity and consistency.


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
