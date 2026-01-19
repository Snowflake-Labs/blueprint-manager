In this step, you'll define the compute warehouses needed for your data product. This step captures:

1. **Warehouse Definitions** (`warehouse_definitions`) — An object list containing:
   - Warehouse name
   - Purpose/workload type (e.g., `ingest`, `transform`, `query`)
   - Size (X-Small through 6X-Large)
   - Auto-suspend timeout
   - Optional modifier (to make warehouse names unique when needed)

Each warehouse definition becomes a `CREATE WAREHOUSE` statement in the Create Warehouses step, with tags applied for cost allocation (DOMAIN, ENVIRONMENT, DATAPRODUCT, WORKLOAD). All warehouses are created with **multi-cluster scaling enabled by default** (1-3 clusters) — additional clusters only spin up when needed, so there's no cost impact if concurrency stays low.

Warehouse definitions are used in subsequent steps:
- **Create Warehouses**: Generates SQL to create each warehouse with tags
- **Grant Warehouse Access**: Assigns USAGE privileges to data product roles
- **Create Resource Monitors**: Monitors are sized based on expected warehouse usage

**Account Context:** This step captures planning information for warehouse creation in the Compute Configuration task.

## **Why is this important?**

Warehouse planning affects both performance and cost:
- **Right-sizing**: Warehouses matched to workload requirements
- **Cost Allocation**: Separate warehouses enable granular cost tracking
- **Performance Isolation**: Different workloads don't compete for resources
- **Optimization**: Each warehouse can be tuned for its specific use case

Think of warehouses as specialized work crews — you might have one crew for loading trucks, another for assembly, and another for quality inspection. Each is sized and equipped for their specific job.

## **Prerequisites**

- Data product identity and zones defined (Define Data Product Identity, Configure Zone Structure, Plan Schema Organization)
- Understanding of your workload patterns and data volumes

## **Key Concepts**

**Warehouse Sizing**
Snowflake warehouses come in t-shirt sizes:
| Size | Credits/Hour | Use Case |
|------|-------------|----------|
| X-Small | 1 | Light queries, development |
| Small | 2 | Standard reporting |
| Medium | 4 | Analytics, moderate loads |
| Large | 8 | Heavy transformations |
| X-Large+ | 16+ | Large-scale processing |

**Workload Types**
Common warehouse workload patterns:
- **Ingest**: Loading data from source systems
- **Transform**: ETL/ELT processing
- **Report**: BI tool queries
- **Analytics**: Ad-hoc analysis
- **ML**: Machine learning workloads

**Auto-Suspend**
Warehouses automatically suspend after idle time to save costs:
- 60 seconds: Aggressive cost savings
- 300 seconds (5 min): Standard for interactive use
- 600 seconds (10 min): For queues with regular activity

**Multi-Cluster Scaling**
All warehouses are created with multi-cluster enabled (1-3 clusters):
- **Min Clusters: 1** — Scales down when idle
- **Max Clusters: 3** — Scales up under concurrent load
- **No cost impact** — Additional clusters only spin up when queries queue

**More Information:**
* [Warehouse Considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations) — Sizing guidance
* [Warehouse Best Practices](https://docs.snowflake.com/en/user-guide/warehouses-best-practices) — Optimization tips
* [Multi-cluster Warehouses](https://docs.snowflake.com/en/user-guide/warehouses-multicluster) — Auto-scaling

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
