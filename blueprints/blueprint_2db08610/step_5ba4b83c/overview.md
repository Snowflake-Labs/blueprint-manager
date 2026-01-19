In this step, you'll define the schemas that will be created within each zone's database. This step captures:

1. **Schema Definitions** (`schema_definitions`) — An object list containing:
   - Zone assignment (which database)
   - Schema name
   - Purpose/description
   - Data classification level

Each schema definition here becomes a `CREATE SCHEMA` statement in the Create Schemas step. Schemas are created with Managed Access enabled, meaning the database owner (not individual users) controls all grants.

Schema definitions are used in subsequent steps:
- **Create Schemas**: Generates SQL to create each schema with appropriate tags
- **Grant Role Privileges**: Privileges are granted at schema level based on zone access patterns

**Account Context:** This step captures planning information for schema creation in the Database & Schema Setup task.

## **Why is this important?**

Schemas provide organization within databases:
- **Logical Grouping**: Related tables are together
- **Access Control**: Grants can be applied at schema level
- **Namespace Separation**: Avoid naming conflicts between different data sources
- **Managed Access**: Centralized privilege management

Think of schemas as folders within a database — they help organize objects so users can find what they need.

## **Prerequisites**

- Zone structure defined in the Configure Zone Structure step
- Understanding of your data sources and processing stages

## **Key Concepts**

**Schema Organization Patterns**
There are several ways to organize schemas:

1. **By Source System** (Common for raw zone)
   - `salesforce`, `hubspot`, `oracle_erp`
   - Groups data by where it came from

2. **By Subject Area** (Common for curated zone)
   - `customers`, `orders`, `products`, `inventory`
   - Groups data by business domain

3. **By Consumer** (Common for consumption zone)
   - `reporting`, `analytics`, `ml_features`
   - Groups data by how it's used

4. **By Data Product** (For shared databases)
   - `<dataproduct>_raw`, `<dataproduct>_curated`
   - Isolates data products within shared infrastructure

**Managed Access Schemas**
All schemas are created with `WITH MANAGED ACCESS`, meaning:
- Schema owner controls all grants (not object owners)
- Simplifies access management
- Aligns with least-privilege principles

**More Information:**
* [Schema Overview](https://docs.snowflake.com/en/sql-reference/sql/create-schema) — CREATE SCHEMA reference
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-privileges#managed-access-schemas) — Centralized grant management

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
