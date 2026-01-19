In this step, you'll define the data processing zones for your data product. This step captures:

1. **Zone List** (`zone_list`) — The stages of data processing (e.g., `raw`, `curated`, `consumption`)

Each zone you define here becomes a separate database in the Database & Schema Setup task. For example, if you define zones `raw`, `curated`, and `consumption`, you'll get three databases with names following your naming conventions (e.g., `SALES_ANALYTICS_RAW`, `SALES_ANALYTICS_CURATED`, `SALES_ANALYTICS_CONSUMPTION`).

Zones are used in subsequent steps:
- **Create Databases**: Each zone becomes a database with a ZONE tag applied
- **Plan Schema Organization**: Schemas are organized within zones
- **Grant Role Privileges**: Zone-based access is controlled through the role hierarchy

**Account Context:** This step captures planning information for database creation in the Database & Schema Setup task.

## **Why is this important?**

Zones provide logical separation of data at different stages of processing:
- **Clarity**: Users know what to expect from data in each zone
- **Access Control**: Different roles can access different zones
- **Data Quality**: Raw data is preserved while transformations create clean data
- **Troubleshooting**: Issues can be traced back through the pipeline

Think of zones as floors in a factory — raw materials come in on the ground floor, processing happens on the middle floors, and finished products go out from the top floor.

## **Prerequisites**

- Data product identity defined in the Define Data Product Identity step
- Understanding of your data processing stages

## **Key Concepts**

**Data Zones**
Logical containers (implemented as databases or database prefixes) that organize data by its stage in the processing pipeline.

**Common Zone Pattern**
Most data products follow a three-zone pattern:
1. **Raw (RAW)**: Data as ingested from source systems (minimal transformation)
2. **Curated (CUR)**: Cleaned, standardized, and enriched data
3. **Consumption/Published (PUB)**: Business-ready data models and aggregations

**Best Practice:** Use short abbreviations (3-4 characters) for zone names. This keeps database names concise while remaining descriptive.

**Zone Characteristics**

| Zone | Abbrev. | Data State | Typical Users | Access Level |
|------|---------|------------|---------------|--------------|
| **Raw** | `raw` | As-is from source | Data engineers | Restricted |
| **Curated** | `cur` | Cleaned and standardized | Data engineers, analysts | Limited |
| **Published** | `pub` | Business-ready | Analysts, BI tools, applications | Broad |

**More Information:**
* [Data Mesh Principles](https://martinfowler.com/articles/data-mesh-principles.html) — Data product concepts
* [Snowflake Data Architecture](https://docs.snowflake.com/en/user-guide/data-architecture) — Database organization

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
