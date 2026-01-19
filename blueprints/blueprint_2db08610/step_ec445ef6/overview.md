In this step, you'll execute SQL to connect your data product account roles to the database roles created in the Database & Schema Setup task. This step produces:

1. **READ Role Connected** — READ role receives the `DB_R` database role from consumption zone database(s)
2. **WRITE Role Connected** — WRITE role receives the `DB_W` database role from all zone databases
3. **ADMIN/CREATE Connected** — ADMIN and CREATE roles receive `DB_C` database roles for delegated administration

This step implements the layered access pattern:
```
Account Role (DP_READ) → Database Role (DB_R) → Schema Roles (SC_R_*)
```

The database roles (`DB_R`, `DB_W`, `DB_C`) were created in Step 2.1, and schema roles (`SC_R_*`, `SC_W_*`, `SC_C_*`) were created in Step 2.2. This step connects your account-level data product roles to those database roles.

**Why this pattern?**
- **Granularity**: Access is managed at the schema level (SC_*), rolled up to database level (DB_*), then to account level
- **Self-service**: Delegated admins can grant schema roles without needing account-level access
- **Sharing**: Database roles can be shared across data products via cross-database grants

**Account Context:** Execute this SQL from the target account using the data product owner role.

## **Why is this important?**

Privileges define what each role can actually do:
- **READ Role**: Query data in consumption zone via DB_R
- **WRITE Role**: Create and modify data across zones via DB_W
- **ADMIN/CREATE**: Full control via DB_C

Think of this step as connecting the dots — the database roles are the "power outlets" and account roles are the "plugs."

## **Prerequisites**

- Roles created in the Create Data Product Roles step
- Ownership transferred in the Transfer Ownership step
- Database roles (DB_R, DB_W, DB_C) created in the Create Databases step
- Schema roles (SC_R_*, SC_W_*, SC_C_*) created in the Create Schemas step

## **Key Concepts**

**Database Role Grants**
Database roles are granted to account roles:
- Account roles can receive database roles from multiple databases
- This enables a single Reader role to access the consumption zone across all schemas

**Zone-Based Access**
Common pattern for data products:
- **READ**: Access to consumption/published zone only
- **WRITE**: Access to all zones (for ETL/ELT)
- **ADMIN/CREATE**: Full control via DB_C roles

**Role Inheritance**
The layered role pattern provides automatic inheritance:
```
Account Role    Database Role    Schema Roles
─────────────   ─────────────    ─────────────
DP_READ     →      DB_R      ←  SC_R_SALES, SC_R_ORDERS
                     ↑
DP_WRITE    →      DB_W      ←  SC_W_SALES, SC_W_ORDERS
                     ↑
DP_ADMIN    →      DB_C      ←  SC_C_SALES, SC_C_ORDERS
```

**More Information:**
* [Database Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#database-roles) — Database-level access control
* [GRANT DATABASE ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-database-role) — SQL reference

### Configuration Questions

#### What is the name of this data product? (`data_product_name`: text)
**What is this asking?**
Provide a descriptive name for your data product. This name will be used in database names, role names, and resource tags.

**Why does this matter?**
The data product name is a key component of object naming:
- Databases: `<domain>_<dataproduct>_<zone>_<env>` (based on your naming convention)
- Roles: `<dataproduct>_owner`, `<dataproduct>_reader`
- Tags: `DATAPRODUCT = '<dataproduct>'`

A clear, descriptive name makes resources easy to identify and manage.

**Naming Guidelines:**
- Use lowercase, single words or concatenated words (no underscores)
- Underscores are reserved for separating naming components (domain, zone, env)
- Be descriptive but concise
- Reflect the business purpose or use case
- Avoid technical jargon unless widely understood
- Avoid reserved words or special characters

**Examples:**
| Name | Description |
|------|-------------|
| `customer360` | Unified customer data and analytics |
| `salesanalytics` | Sales reporting and analysis |
| `supplychain` | Supply chain operations data |
| `finreporting` | Financial reporting and compliance |
| `marketing` | Marketing campaign attribution |
| `productcatalog` | Product information management |
| `inventory` | Inventory tracking and forecasting |

**Recommendation:**
Choose a name that business users would recognize. Ask: "If someone searched for this data, what would they type?"

**More Information:**
* [Identifier Requirements](https://docs.snowflake.com/en/sql-reference/identifiers-syntax) — Valid characters and length limits

#### Which domain does this data product belong to? (`data_product_domain`: multi-select)
**What is this asking?**
Select the business domain (team, department, or organizational unit) that owns this data product.

**Auto-Detection for Multi-Account Strategies:**
- **Domain-based accounts**: Your domain is determined by your target account. Select the matching value.
- **Domain + Environment accounts**: Your domain is derived from the first part of your account name. Select the matching value.
- **Environment-based accounts**: Domain is not determined by your account. Select from the available options.
- **Single Account**: Domain is not determined by your account. Select from the available options.

**Why does this matter?**
Domain assignment determines:
- **Cost Allocation**: Credits consumed are attributed to this domain
- **Ownership**: The domain team is responsible for the data product
- **Access Patterns**: Domain-based roles may have different access levels
- **Governance**: Domain-specific policies may apply

**How domains are used:**
- Object names may include the domain abbreviation
- The `DOMAIN` tag is applied to all resources
- Cost reports can filter by domain

**Available Domains:**
Your organization defined these domains in Platform Foundation. If you need a new domain, update Platform Foundation first.

**If your domain isn't listed:**
Work with your platform team to add the domain to Platform Foundation, then return to this workflow.

**Recommendation:**
For domain-based and domain+environment strategies, select the domain that matches your target account name.

#### Which environment is this data product being deployed to? (`data_product_environment`: multi-select)
**What is this asking?**
Select the SDLC environment for this data product deployment.

**Auto-Detection for Multi-Account Strategies:**
- **Environment-based accounts**: Your environment is determined by your target account. Select the matching value.
- **Domain + Environment accounts**: Your environment is derived from the second part of your account name. Select the matching value.
- **Domain-based accounts**: Environment is not determined by your account. Select from the available options.
- **Single Account**: Environment is not determined by your account. Select from the available options.

**Why does this matter?**
Environment assignment determines:
- **Isolation**: Resources are created in the appropriate context
- **Access Controls**: Production typically has stricter access
- **Resource Sizing**: Dev environments may use smaller warehouses
- **Data Sensitivity**: Production may have real data vs. synthetic in dev

**Common Environments:**
| Abbreviation | Full Name | Purpose |
|--------------|-----------|---------|
| `dev` | Development | Building and testing code |
| `test` | Testing/QA | Quality assurance |
| `stg` | Staging | Pre-production validation |
| `prod` | Production | Live environment |

**Recommendation:**
For environment-based and domain+environment strategies, select the environment that matches your target account name.

#### Which role structure do you want for this data product? (`role_structure`: multi-select)
Choose based on your team's needs:

- **Simple**: Best for small teams or single-purpose data products. The ADMIN handles all modifications, READ users consume.
- **Standard**: Adds a CREATE role for delegated object creation and grant management. Good for medium teams.
- **Full**: Includes a WRITE role for ETL/ELT processes that need to modify data without full admin access.

**Why does this matter?**
More roles mean finer-grained control but also more management overhead. Start with the simplest structure that meets your needs — you can always add roles later.

**More Information:**
* [Access Control Best Practices](https://docs.snowflake.com/en/user-guide/security-access-control-considerations) — Role design patterns
**Options:**
- Simple (Admin + Read only)
- Standard (Admin + Create + Read)
- Full (Admin + Create + Write + Read)

#### Which zone should the Reader role have access to? (`reader_zone_access`: multi-select)
Select the zone that readers should have access to.

**Recommendation:** Select your consumption/final zone (the zone with analytics-ready data).

**Best practices:**
- **Consumption/Gold zone**: Best practice — readers see only validated, documented data
- **Curated/Silver zone**: Only if teams need access to intermediate transformations
- **Raw/Bronze zone**: Use cautiously — may contain sensitive or unvalidated content

**Why does this matter?**
Limiting reader access to the final zone:
- Protects sensitive source data in earlier zones
- Ensures users see validated, documented data
- Simplifies data governance

**Note:** This currently supports single-zone selection. If you need readers to access multiple zones, grant additional privileges manually after running the generated SQL.

**More Information:**
* [Data Governance Best Practices](https://docs.snowflake.com/en/user-guide/data-governance) — Access patterns

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

#### Which account will this data product be deployed to? (`target_account_name`: text)

**What is this asking?**
Enter the name of the Snowflake account where this data product will be created.

**Why does this matter?**
This ensures all generated SQL is clearly documented with the target account, preventing deployment errors and providing clear audit trails.

**How to find your account name:**
- In Snowsight: Click your account name in the bottom-left corner
- Run SQL: `SELECT CURRENT_ACCOUNT_NAME();`
- From your URL: `https://<org>-<account>.snowflakecomputing.com`

**Examples based on strategy:**

**Domain-based strategy:**
- `ACME_SALES` - Sales domain account
- `ACME_FINANCE` - Finance domain account

**Environment-based strategy:**
- `ACME_DEV` - Development environment account
- `ACME_PROD` - Production environment account

**Domain + Environment strategy:**
- `ACME_SALES_DEV` - Sales domain, Development environment
- `ACME_FINANCE_PROD` - Finance domain, Production environment

**Recommendation:**
Copy the exact account name from your Snowflake session to avoid typos.

**More Information:**
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding account names

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

#### What zones will this data product use? (`zone_list`: list)
**What is this asking?**
Define the data zones for your data product. Each zone will become a database (or database prefix, depending on your naming convention).

**Why does this matter?**
Zones organize your data pipeline:
- Each zone has clear ownership and purpose
- Access controls are applied at the zone level
- Data lineage flows from zone to zone

**Common Zone Patterns:**

**Standard Three-Zone (Recommended for most):**
- `raw` - Ingested data, minimal transformation
- `curated` - Cleaned and standardized
- `consumption` - Business-ready models

**Extended Four-Zone (For complex pipelines):**
- `raw` - Ingested data
- `staging` - Intermediate processing
- `curated` - Cleaned and standardized
- `consumption` - Business-ready models

**Simplified Two-Zone (For simple use cases):**
- `raw` - Ingested data
- `consumption` - Business-ready models

**Custom Zones (Industry-specific):**
- `bronze`, `silver`, `gold` - Medallion architecture
- `landing`, `refined`, `published` - ETL terminology
- `ingest`, `transform`, `serve` - Process-oriented

**Naming Guidelines:**
- Use lowercase, single words
- Keep zone names short (5-10 characters)
- Be consistent with your organization's terminology

**Examples:**
```
raw
curated
consumption
```

**Recommendation:**
Start with the standard three-zone pattern unless you have specific requirements for more or fewer zones.

**More Information:**
* [Data Zones Best Practices](https://docs.snowflake.com/en/user-guide/databases-best-practices) — Database organization
