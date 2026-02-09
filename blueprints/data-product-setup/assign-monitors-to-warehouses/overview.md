After creating the resource monitor, it must be assigned to the warehouses you want to track. A warehouse can only be assigned to one resource monitor at a time, but a resource monitor can track multiple warehouses.

This step assigns the data product's resource monitor to all warehouses configured for the data product. Credit consumption from all assigned warehouses will count toward the monitor's quota.

**Account Context:** Execute this SQL with ACCOUNTADMIN to assign resource monitors.

## Why is this important?

Assigning monitors to warehouses enables:
- **Unified Tracking**: All data product compute in one budget
- **Automatic Enforcement**: Suspend when quota exceeded
- **Cost Attribution**: Clear ownership of compute costs

## Prerequisites

- Resource monitor created (Step 5.1)
- Warehouses created (Step 3.1)

## Key Concepts

**Monitor-Warehouse Relationship**
```
Resource Monitor ──┬── Warehouse 1
                   ├── Warehouse 2
                   └── Warehouse N
```
All warehouses share the monitor's quota.

**Quota Consumption**
- All assigned warehouses contribute to the same quota
- Credits are counted immediately as consumed
- Quota resets according to the frequency setting

**Removing Monitor Assignment**
To remove a warehouse from monitoring:
```sql
ALTER WAREHOUSE <name> SET RESOURCE_MONITOR = NULL;
```

**Changing Monitor Assignment**
To move a warehouse to a different monitor:
```sql
ALTER WAREHOUSE <name> SET RESOURCE_MONITOR = <new_monitor>;
```

**More Information:**
* [ALTER WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse)
* [Resource Monitor Usage](https://docs.snowflake.com/en/user-guide/resource-monitors#viewing-and-modifying-resource-monitors)


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

#### Define the warehouses for your data product. (`warehouse_configuration`: object-list)
**What is this asking?**
Define compute warehouses for your data product workloads.

**Common Patterns:**

**Simple (1 warehouse):**
| Name | Size | Min/Max Clusters | Auto-Suspend |
|------|------|------------------|--------------|
| GENERAL | Small | 1/1 | 300 |

**Standard (2-3 warehouses):**
| Name | Size | Min/Max Clusters | Auto-Suspend |
|------|------|------------------|--------------|
| ETL | Medium | 1/3 | 60 |
| QUERY | Small | 1/2 | 300 |

**Advanced (workload isolation):**
| Name | Size | Min/Max Clusters | Auto-Suspend |
|------|------|------------------|--------------|
| INGEST | Large | 1/3 | 60 |
| TRANSFORM | Medium | 1/3 | 120 |
| INTERACTIVE | Small | 1/2 | 300 |
| REPORTING | Medium | 1/4 | 300 |

**Sizing Guidelines:**
- X-Small/Small: Development, light queries
- Medium: Standard production workloads
- Large+: Heavy ETL, complex analytics

**Auto-Suspend Guidelines:**
- Batch workloads: 60 seconds
- Interactive: 300-600 seconds


#### How many credits should be the limit for the resource monitor? (`resource_monitor_credits`: text)
**What is this asking?**
Set the maximum credit consumption for this data product's warehouses.

**How to estimate:**
- X-Small warehouse ≈ 1 credit/hour
- Small warehouse ≈ 2 credits/hour
- Medium warehouse ≈ 4 credits/hour
- Large warehouse ≈ 8 credits/hour

**Example calculations:**
- Light usage (8hrs/day, Small): 8 × 2 × 22 = 352 credits/month
- Medium usage (12hrs/day, Medium): 12 × 4 × 22 = 1,056 credits/month
- Heavy usage (24/7, Large): 24 × 8 × 30 = 5,760 credits/month

**Recommendation:** Start conservative. You can increase limits later.

**Examples:**
- `500` — Small data product
- `1000` — Medium workload
- `5000` — Heavy ETL and analytics

