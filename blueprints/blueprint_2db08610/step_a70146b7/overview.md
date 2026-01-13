In this step, you'll execute SQL to create the access control roles for your data product. This step produces:

1. **Admin Role** (`<dataproduct>_ADMIN`) — Full administrative control; will own all databases, schemas, and warehouses
2. **Create Role** (`<dataproduct>_CREATE`) — Can create objects and manage grants within the data product (delegated administration)
3. **Write Role** (`<dataproduct>_WRITE`) — Can modify data across zones (INSERT, UPDATE, DELETE)
4. **Read Role** (`<dataproduct>_READ`) — Read-only access to consumption zone
5. **Account Access Role Grants** — Optional grants of account-level access roles for tasks, masking policies, etc.

The roles are created with a hierarchy: ADMIN > CREATE > WRITE > READ. This allows delegated administration—users with the ADMIN role automatically inherit all capabilities of lower roles.

Roles created here are used in subsequent steps:
- **Transfer Ownership**: ADMIN role receives database and schema ownership
- **Grant Role Privileges**: Each role receives database role grants
- **Assign Roles to Users**: Users are assigned to these roles
- **Grant Warehouse Access**: Roles are granted USAGE on warehouses

**Account Context:** Execute this SQL from the target account with USERADMIN role.

## **Why is this important?**

Roles define who can do what with your data:
- **Separation of Duties**: Different roles for different responsibilities
- **Principle of Least Privilege**: Users get only what they need
- **Delegated Management**: Data product teams manage their own access
- **Audit Trail**: Role-based access simplifies compliance

Think of roles as keys to different rooms — the ADMIN has a master key, CREATE users have department keys, WRITE users have editing access, and READ users have visitor passes.

## **Prerequisites**

- Target account accessible with USERADMIN role
- Data product identity defined in the Define Data Product Identity step
- Naming conventions from Platform Foundation
- (Optional) Account access roles created in the Account Creation workflow

## **Key Concepts**

**Role Types**
- **ADMIN**: Full administrative control, owns all objects
- **CREATE**: Can create objects and manage grants (delegated administration)
- **WRITE**: Can modify data (INSERT, UPDATE, DELETE)
- **READ**: Read-only access to consumption zone

**Best Practice:** Always create distinct roles rather than granting privileges directly to users. This enables easier management and auditing.

**Role Inheritance**
Roles can inherit privileges from other roles:
```
SYSADMIN
  └── DATA_PRODUCT_ADMIN
        └── DATA_PRODUCT_CREATE
              ├── DATA_PRODUCT_WRITE ← _AR_EXEC_TASK, _AR_APPLY_DDM, etc.
              └── DATA_PRODUCT_READ
```

**Account Access Roles**
Account-level access roles provide special privileges that can be granted to data product roles:
- `_AR_VIEW_AUSG` — View Account Usage data
- `_AR_EXEC_TASK` — Execute tasks
- `_AR_APPLY_DDM` — Apply dynamic data masking policies
- `_AR_APPLY_RAP` — Apply row access policies
- `_AR_APPLY_TAG` — Apply tags to objects

These are typically created once per account in the Account Creation workflow and then granted to data product roles as needed.

**Naming Convention**
Role names follow the data product naming pattern:
- `<dataproduct>_ADMIN`
- `<dataproduct>_CREATE`
- `<dataproduct>_WRITE`
- `<dataproduct>_READ`

**More Information:**
* [CREATE ROLE](https://docs.snowflake.com/en/sql-reference/sql/create-role) — SQL reference
* [Role Hierarchy](https://docs.snowflake.com/en/user-guide/security-access-control-overview#role-hierarchy-and-privilege-inheritance) — Inheritance patterns

### Configuration Questions

#### Should the data product roles receive account-level access roles? (`grant_account_access_roles`: multi-select)
Account access roles provide special account-level privileges needed for common data product operations.

**Select "Yes" if your data product needs to:**
- Execute Snowflake tasks (scheduled jobs)
- Apply dynamic data masking policies
- Apply row access policies
- Apply tags to objects
- Query Account Usage views

**Select "No" if:**
- This is a read-only data product
- Account access roles don't exist in this account
- You'll manually grant these privileges later

**Note:** Account access roles must exist in the account. They are typically created in the Account Creation workflow with names like `_AR_EXEC_TASK`, `_AR_APPLY_DDM`, etc. These will be granted to the WRITE role (Full structure) or ADMIN role (Simple/Standard structure).
**Options:**
- Yes - Grant account access roles (tasks, masking, tagging)
- No - Skip account access roles

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

#### Which role should the ADMIN role be granted to? (`admin_role_granted_to`: text)
Enter the name of the role that should be the parent of the data product ADMIN role.

**Common options:**
- `SYSADMIN` — **Recommended.** Platform administrators can act as ADMIN when needed.
- `SECURITYADMIN` — If you want security team oversight of data product access.
- Custom role name (e.g., `FINANCE_ADMIN`) — If you have a domain-level role to contain all data products for a domain.

**Why does this matter?**
Role hierarchy determines who can assume data product administration. Granting to SYSADMIN ensures platform administrators can always help troubleshoot.

**Recommendation:** Enter `SYSADMIN` unless you have a specific requirement for a different parent role.

**More Information:**
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Role hierarchy
