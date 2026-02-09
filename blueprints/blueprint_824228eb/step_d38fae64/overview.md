In this step, you'll create the five core account-level roles for your data product:

1. **ADMIN** (`<prefix>_ADMIN`) — Full administrative control; owns databases, schemas, and warehouses
2. **CREATE** (`<prefix>_CREATE`) — Can create objects; receives account access roles for tasks, masking, tagging
3. **WRITE** (`<prefix>_WRITE`) — Can modify data (INSERT, UPDATE, DELETE)
4. **RBAC** (`<prefix>_RBAC`) — Owns database access roles; enables delegated access governance
5. **READ** (`<prefix>_READ`) — Read-only access across the data product

Role ownership is determined by your SCIM configuration:
- **With SCIM**: Roles owned by `<scim_prefix>_PROVISIONER`
- **Without SCIM**: Roles owned by `USERADMIN`

**Account Context:** Execute this SQL in the target account with USERADMIN role.

## Why is this important?

Core roles provide:
- **Separation of Duties**: Different roles for different responsibilities
- **Delegated Administration**: Data product teams manage their own access
- **Principle of Least Privilege**: Users get only what they need
- **SCIM Compatibility**: Role ownership supports identity provider management

## Prerequisites

- Target account accessible with USERADMIN role
- Data product identity defined (Step 1.2)
- SCIM prefix configured (or NONE)
- (Optional) Account access roles exist (`_AR_EXEC_TASK`, `_AR_APPLY_DDM`, etc.)

## Key Concepts

**Role Hierarchy**

```
SYSADMIN
└── <dataproduct>_ADMIN
    ├── <dataproduct>_CREATE ← _AR_EXEC_TASK, _AR_VIEW_AUSG, _AR_APPLY_*
    └── <dataproduct>_RBAC
```

**Role Responsibilities**

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| ADMIN | Own infrastructure, manage CREATE/RBAC roles | Directly assigned to users (typically) |
| CREATE | Create objects, execute tasks, apply policies | Own infrastructure |
| WRITE | Modify data | Create objects |
| RBAC | Grant access roles to users/roles | Modify data |
| READ | Query data | Modify anything |

**SCIM Role Ownership**

Role ownership depends on your SCIM configuration:
- **With SCIM**: Roles are owned by your SCIM provisioner role (e.g., `OKTA_PROVISIONER`), enabling automatic user assignment through your identity provider
- **Without SCIM**: Roles are owned by `USERADMIN`, requiring manual user assignment in Snowflake

**More Information:**
* [CREATE ROLE](https://docs.snowflake.com/en/sql-reference/sql/create-role) — Role creation
* [Role Hierarchy](https://docs.snowflake.com/en/user-guide/security-access-control-overview#role-hierarchy-and-privilege-inheritance)
* [SCIM Provisioning](https://docs.snowflake.com/en/user-guide/scim)


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
