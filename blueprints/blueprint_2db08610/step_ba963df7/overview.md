In this step, you'll execute SQL to create the compute warehouses for your data product. This step produces:

1. **Warehouses** — Each warehouse from the Plan Warehouse Requirements step, created with the specified size and auto-suspend settings
2. **FinOps Tags Applied** — Each warehouse is immediately tagged with DOMAIN, ENVIRONMENT, DATAPRODUCT, and WORKLOAD
3. **Initial Suspended State** — Warehouses start suspended to avoid charges until needed
4. **Owner Role Ownership** — Warehouses are owned by the data product owner role

The warehouses are created with your defined sizing and multi-cluster settings. Auto-suspend ensures warehouses automatically stop when idle, controlling costs.

Warehouses created here are used in subsequent steps:
- **Grant Warehouse Access**: Roles are granted USAGE privileges
- **Configure Warehouse Tags**: Additional tags like COST_CENTER can be applied
- **Assign Monitors to Warehouses**: Resource monitors track usage

**Account Context:** Execute this SQL from the target account with SYSADMIN role.

## **Why is this important?**

Warehouses are where compute happens:
- **Right-Sized Compute**: Match warehouse size to workload
- **Cost Efficiency**: Auto-suspend when idle
- **Performance**: Dedicated warehouses prevent resource contention

Think of warehouses as specialized machinery — you need different equipment for different jobs, and you want to turn them off when not in use.

## **Prerequisites**

- Target account accessible with SYSADMIN role
- Warehouse definitions from the Plan Warehouse Requirements step
- Data product roles created in the Role & Access Control task

## **Key Concepts**

**Warehouse Ownership**
Warehouses are owned by the data product owner role:
- Enables delegated administration
- Owner can grant USAGE to other roles
- Aligns with data product governance model

**Initially Suspended**
Warehouses are created in suspended state:
- No cost until first use
- Confirms configuration before incurring charges

**Statement Timeouts**
Consider setting STATEMENT_TIMEOUT_IN_SECONDS:
- Prevents runaway queries from consuming resources
- Common values: 900 (15 min) for interactive, 3600 (1 hour) for ETL

**More Information:**
* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse) — SQL reference
* [Warehouse Properties](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse#optional-properties-objectproperties) — Configuration options

### Configuration Questions

#### Define the warehouses for your data product. (`warehouse_definitions`: object-list)
**What is this asking?**
Define each warehouse that will be created for your data product. For each warehouse, specify:
- Name (used in object naming)
- Purpose (workload type)
- Size (compute capacity)
- Auto-suspend timeout
- Modifier (optional - use when you need multiple warehouses of the same workload type)

**Why does this matter?**
Warehouse configuration directly impacts:
- Query performance (size)
- Cost (size × usage time)
- Resource contention (separate warehouses = isolation)

**Common Warehouse Patterns:**

**Simple (1 warehouse):**
| Warehouse | Purpose | Size | Auto-Suspend | Modifier |
|-----------|---------|------|--------------|----------|
| `general` | general | Small | 300 | (leave blank) |

**Standard (2-3 warehouses):**
| Warehouse | Purpose | Size | Auto-Suspend | Modifier |
|-----------|---------|------|--------------|----------|
| `ingest` | ingest | Medium | 60 | (leave blank) |
| `transform` | transform | Medium | 300 | (leave blank) |
| `report` | report | Small | 300 | (leave blank) |

**Advanced (4+ warehouses):**
| Warehouse | Purpose | Size | Auto-Suspend | Modifier |
|-----------|---------|------|--------------|----------|
| `ingest` | ingest | Large | 60 | (leave blank) |
| `transform` | transform | Large | 300 | (leave blank) |
| `report` | report | Medium | 300 | (leave blank) |
| `analytics` | analytics | Medium | 600 | (leave blank) |

**With Modifiers (multiple warehouses of same type):**
| Warehouse | Purpose | Size | Auto-Suspend | Modifier |
|-----------|---------|------|--------------|----------|
| `query` | report | Medium | 300 | `bi` |
| `query` | report | Large | 300 | `powerbi` |
| `transform` | transform | Large | 300 | `batch` |
| `transform` | transform | Medium | 60 | `stream` |

The modifier is appended to the warehouse name to create unique identifiers when you need multiple warehouses of the same workload type (e.g., `SALES_QUERY_BI_WH` and `SALES_QUERY_POWERBI_WH`).

**Sizing Guidelines:**
- **Development**: X-Small or Small
- **Standard Production**: Small or Medium
- **Heavy Workloads**: Large or X-Large

**Auto-Suspend Guidelines:**
- **Batch jobs** (ingest, transform): 60 seconds — save costs between runs
- **Interactive queries** (report, analytics): 300-600 seconds — balance UX and cost
- **Continuous workloads**: Higher values to avoid resume latency

**Note:** All warehouses are created with multi-cluster scaling enabled (1-3 clusters). Additional clusters only spin up when needed.

**Recommendation:**
Start with 2-3 warehouses. You can always add more or resize as you learn your workload patterns.

**More Information:**
* [Warehouse Sizing](https://docs.snowflake.com/en/user-guide/warehouses-overview#warehouse-size) — Size comparison

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
