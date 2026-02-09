In this step, you'll define the data zones for your data product. Zones represent distinct stages in your data processing pipeline, typically implemented as separate databases. Common zones include:

1. **RAW** — Landing zone for source data (minimal transformation)
2. **CURATED** — Cleansed, validated, and transformed data
3. **PUB** (Published) — Business-ready data for consumption

Each zone you define will become a separate database with its own access controls and database roles.

**Account Context:** This is a planning step. Databases are created in Task 2.

## Why is this important?

Zone separation provides:
- **Data Lineage**: Clear progression from raw to refined data
- **Access Control**: Different zones can have different access policies
- **Performance**: Separate databases allow independent scaling
- **Governance**: Each zone can have its own retention and quality rules
- **Cost Attribution**: Storage and compute can be tracked by zone

## Prerequisites

- Data product identity defined (Step 1.2)
- Understanding of your data processing stages

## Key Concepts

**Common Zone Patterns**

| Pattern | Zones | Use Case |
|---------|-------|----------|
| Medallion | RAW → CURATED → PUB | Most common; clear data quality progression |
| Bronze-Silver-Gold | BRONZE → SILVER → GOLD | Alternative naming for medallion pattern |
| Simple | RAW → PUB | Simple pipelines with minimal transformation |
| Extended | RAW → STG → CURATED → PUB | Complex pipelines with staging area |

**Zone Characteristics**

| Zone | Data Quality | Access | Typical Users |
|------|--------------|--------|---------------|
| RAW | As-is from source | Restricted | Data engineers |
| CURATED | Cleansed, validated | Limited | Data engineers, analysts |
| PUB | Business-ready | Broad | Business users, applications |

**Database per Zone**
Each zone becomes a database following your naming convention:
- `<prefix>_RAW`
- `<prefix>_CURATED`
- `<prefix>_PUB`

**More Information:**
* [Database Design Best Practices](https://docs.snowflake.com/en/user-guide/databases-best-practices)
* [Data Mesh Patterns](https://docs.snowflake.com/en/user-guide/data-mesh)


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

#### Define the data zones for your data product. (`data_zones`: object-list)
**What is this asking?**
Define each data zone (logical layer) for your data product. Zones represent 
stages in your data pipeline.

**Common Zone Patterns:**

**Three-Zone (Medallion):**
| Zone | Purpose | Time Travel |
|------|---------|-------------|
| RAW | Landing zone for source data | 1 day |
| CURATED | Cleansed and validated data | 7 days |
| CONSUMPTION | Business-ready analytics | 7 days |

**Four-Zone:**
| Zone | Purpose | Time Travel |
|------|---------|-------------|
| LANDING | Raw ingestion | 1 day |
| BRONZE | Light transformation | 1 day |
| SILVER | Business logic applied | 7 days |
| GOLD | Aggregated/consumption | 7 days |

**Why does this matter?**
- Each zone becomes a separate database
- Zone structure affects data lineage and access patterns
- Time travel settings impact storage costs

**Recommendation:** Start with 3 zones. You can add more later.


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
