This is the final step of the core infrastructure setup. Here you'll:

1. **Wire the Role Hierarchy** — Connect READ → WRITE → CREATE → ADMIN
2. **Connect Database Roles** — Link database roles to account roles
3. **Create Account Access Roles** — Specialized roles for account-level privileges
4. **Connect to SCIM** — Enable user provisioning through identity provider

After this step, your data product is fully operational with proper access control.

**Account Context:** Execute this SQL in the target account using SECURITYADMIN.

## Why is this important?

Properly wired role hierarchy enables:
- **Inheritance**: Higher roles automatically get lower role privileges
- **Simplicity**: Assign one role, get appropriate access
- **Flexibility**: RBAC role can delegate access without admin involvement
- **Integration**: SCIM provisioner can manage user assignments

## Prerequisites

- Core roles created (Step 2.1)
- Databases and schemas created (Steps 2.2, 2.3)
- Warehouses and access roles created (Steps 3.1, 3.2)

## Key Concepts

**Core Role Hierarchy**
```
READ ← WRITE ← CREATE ← ADMIN
                         ↓
                       RBAC
```
Each role inherits privileges from the role below it.

**Database Role Integration**
```
DB_R → READ   (all zones)
DB_W → WRITE  (all zones)
DB_C → CREATE (all zones)
```

**Account Access Roles**
| Role | Privilege | Purpose |
|------|-----------|---------|
| `_AR_EXEC_TASK` | EXECUTE TASK | Run scheduled tasks |
| `_AR_VIEW_AUSG` | IMPORTED PRIVILEGES on SNOWFLAKE | View account usage |
| `_AR_APPLY_DDM` | APPLY MASKING POLICY | Apply data masking |
| `_AR_APPLY_RAP` | APPLY ROW ACCESS POLICY | Apply row-level security |
| `_AR_APPLY_TAG` | APPLY TAG | Apply governance tags |

**More Information:**
* [Role Hierarchy](https://docs.snowflake.com/en/user-guide/security-access-control-overview#role-hierarchy-and-privilege-inheritance)
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles)


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

#### Define the schemas for each zone in your data product. (`schema_configuration`: object-list)
**What is this asking?**
Define schemas within each zone. Schemas organize tables by source system 
or subject area.

**Example Configuration:**

**RAW Zone:**
| Schema | Purpose |
|--------|---------|
| SALESFORCE | Salesforce CRM data |
| SAP | SAP ERP data |
| STRIPE | Payment processing data |

**CURATED Zone:**
| Schema | Purpose |
|--------|---------|
| CUSTOMERS | Unified customer data |
| ORDERS | Order history |
| PRODUCTS | Product catalog |

**CONSUMPTION Zone:**
| Schema | Purpose |
|--------|---------|
| REPORTING | BI-ready tables |
| ANALYTICS | Aggregations and metrics |

**Best Practices:**
- Use consistent naming across zones
- Group by source system in RAW, by subject in CURATED
- Keep schema count manageable (2-5 per zone)


#### What prefix is used for your SCIM provisioner role? (`scim_prefix`: text)
**What is this asking?**
If using SCIM for identity management, enter the prefix used for the 
SCIM provisioner role.

**Common SCIM prefixes:**
- `AAD` — Microsoft Entra ID (Azure AD)
- `OKTA` — Okta
- `PING` — PingIdentity

**How this is used:**
The SCIM provisioner role is typically named `<PREFIX>_PROVISIONER`.
For example: `AAD_PROVISIONER`, `OKTA_PROVISIONER`

**Enter `NONE` if:**
- Not using SCIM integration
- Managing users manually
- Using a different identity provisioning approach

**More Information:**
* [SCIM Provisioning](https://docs.snowflake.com/en/user-guide/scim)

