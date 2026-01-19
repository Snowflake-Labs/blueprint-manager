In this step, you'll execute SQL to create the schemas within your data product databases. This step produces:

1. **Schemas with Managed Access** — Each schema is created with `WITH MANAGED ACCESS`, ensuring the schema owner controls all grants
2. **Schema Access Roles** — Each schema gets three database roles (`SC_R_*`, `SC_W_*`, `SC_C_*`) for fine-grained access control
3. **Comprehensive Privilege Grants** — Each schema role receives appropriate privileges on all object types (tables, views, functions, procedures, streams, tasks, etc.)
4. **Future Grants Configured** — Privileges are automatically granted on future objects
5. **Role Hierarchy Established** — Schema roles connect to database roles (`DB_R`, `DB_W`, `DB_C`)
6. **FinOps Tags Applied** — Each schema is tagged with DOMAIN, ENVIRONMENT, DATAPRODUCT, ZONE, and DATA_CLASSIFICATION

This step implements the layered database role pattern:
```
Account Role (e.g., DP_READ) → Database Role (DB_R) → Schema Role (SC_R_SALES)
```

This pattern enables:
- Fine-grained access control at the schema level
- Self-service administration by delegated admins
- Cross-data-product sharing via database role grants

**Account Context:** Execute this SQL from the target account with SYSADMIN role.

## **Why is this important?**

Schemas organize data within databases:
- **Logical Organization**: Group related tables and objects
- **Namespace Separation**: Avoid naming conflicts between sources
- **Granular Access Control**: Schema-level roles enable precise permissions
- **Documentation**: Schema names and comments describe their purpose

Think of schemas as folders within a filing cabinet — each folder has its own access card (schema role) that can be shared with different people.

## **Prerequisites**

- Databases created in the Create Databases step (with DB_R, DB_W, DB_C roles)
- Schema definitions from the Plan Schema Organization step

## **Key Concepts**

**Managed Access Schemas**
All schemas are created with `WITH MANAGED ACCESS`:
- Schema owner controls all grants
- Object creators cannot grant access to their own objects
- Centralizes privilege management for security

**Schema Access Roles (Database Roles)**
Each schema has three database roles for layered access:
- `SC_R_<schema>` — Read access (SELECT on tables, views, functions)
- `SC_W_<schema>` — Write access (INSERT, UPDATE, DELETE, EXECUTE) — inherits from SC_R
- `SC_C_<schema>` — Create access (CREATE objects, DDL) — inherits from SC_W

**Role Hierarchy**
Schema roles inherit from each other and connect to database roles:
```
DB_C ← SC_C_SALES    (Create has full access)
  │      ↑
DB_W ← SC_W_SALES    (Write has read + modify)
  │      ↑
DB_R ← SC_R_SALES    (Read has query access)
```

**Comprehensive Privileges**
Schema roles grant access to all object types:
- **Read**: Tables, Views, External Tables, Dynamic Tables, Materialized Views, Functions
- **Write**: Streams, Procedures, Sequences, Tasks, File Formats, Stages, Alerts
- **Create**: All CREATE privileges on the schema

**Alternative: Stored Procedure Approach**
For organizations that prefer centralized schema provisioning with runtime validation and audit logging, schemas can be created via a stored procedure instead of executing the inline SQL generated below.

The stored procedure approach offers:
- **Runtime Validation**: Verify permissions and schema uniqueness before creation
- **Audit Logging**: Centralized tracking of all schema creations
- **Self-Service**: Delegated admins can create schemas without platform team involvement
- **Consistency**: Enforces standard schema configurations and naming

To use the stored procedure approach:
1. Deploy the `PROVISION_SCHEMA_SP` procedure to your infrastructure database (e.g., `INFRA.UTL_PROVISION.PROVISION_SCHEMA_SP`)
2. Call the procedure instead of executing the inline SQL:
   ```sql
   CALL INFRA.UTL_PROVISION.PROVISION_SCHEMA_SP(
     '<database_name>',
     '<schema_name>',
     <time_travel_days>,
     '<purpose_code>',
     TRUE -- deploy after validation
   );
   ```

The procedure will create the schema, access roles, and grants, then log the action to a central audit table.

**Note:** The inline SQL approach below is recommended for GitOps/version-controlled deployments where code review before execution is preferred.

**More Information:**
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema) — SQL reference
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-privileges#managed-access-schemas) — Privilege management
* [Database Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#database-roles) — Database-level access control

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

#### Define the schemas for your data product. (`schema_definitions`: object-list)

**What is this asking?**
Define each schema that will be created in your data product. For each schema, specify:
- Which zone it belongs to
- The schema name
- Its purpose
- The data classification level

**Why does this matter?**
Schema definitions determine:
- Database structure and organization
- Access control granularity
- Data classification for masking policies

**Schema Naming Guidelines:**
- Use lowercase without underscores
- Be descriptive but concise
- Match your source system or subject area naming

**Example Schema Structure:**

**Raw Zone:**
| Schema | Purpose | Classification |
|--------|---------|----------------|
| `salesforce` | Salesforce CRM data | CONFIDENTIAL |
| `hubspot` | HubSpot marketing data | INTERNAL |
| `stripe` | Stripe payment data | RESTRICTED |

**Curated Zone:**
| Schema | Purpose | Classification |
|--------|---------|----------------|
| `customers` | Unified customer profiles | CONFIDENTIAL |
| `orders` | Order history and details | CONFIDENTIAL |
| `products` | Product catalog | INTERNAL |

**Consumption Zone:**
| Schema | Purpose | Classification |
|--------|---------|----------------|
| `reporting` | BI-ready fact and dimension tables | INTERNAL |
| `analytics` | Aggregations and metrics | INTERNAL |
| `mlfeatures` | Machine learning feature store | CONFIDENTIAL |

**Recommendation:**
Start simple — you can always add schemas later. Most data products have 2-4 schemas per zone.

**More Information:**
* [Data Classification Best Practices](https://docs.snowflake.com/en/user-guide/governance-classify) — Classification guidance

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
