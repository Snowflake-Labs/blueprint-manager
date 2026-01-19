In this step, you'll assign initial owners to the data product. This step produces:

1. **Owner Assignments** — SQL to grant the owner role to the specified users

This step focuses on establishing initial ownership only. Reader, writer, and admin access should be managed separately through your organization's access management process (SCIM, ServiceNow, access request workflows, etc.).

**Why only owners?**
- Owners are required from day one to manage the data product
- Reader/writer access typically grows over time as the data product matures
- Large-scale user management is better handled through SCIM or identity provider integration
- Access request workflows provide better audit trails than embedding users in setup scripts

**Account Context:** Execute this SQL from the target account with SECURITYADMIN or the data product owner role.

## **Why is this important?**

Every data product needs at least one owner who can:
- Manage access grants within the data product
- Troubleshoot permission issues
- Coordinate with the platform team
- Own accountability for the data product

Think of owners as the "keys to the building" — someone needs them from day one, but you don't need to issue everyone's badge during construction.

## **Prerequisites**

- Roles created and privileges granted in previous steps (Create Data Product Roles, Transfer Ownership, Grant Role Privileges)
- Owner users provisioned in the account (via SCIM or manual creation)

## **Key Concepts**

**Owner Role Responsibilities**
- Full administrative control over all data product resources
- Can grant access to other users (via the role hierarchy)
- Accountable for data product governance
- Typically 1-2 people: data steward, lead engineer, or product owner

**Ongoing Access Management**
After initial setup, manage reader/writer access through:
- **SCIM Integration**: Sync IdP groups to Snowflake roles
- **Access Request Workflows**: ServiceNow, Jira, or custom processes
- **Parent Role Assignment**: Grant the data product role to a team role

**More Information:**
* [GRANT ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-role) — SQL reference
* [SCIM Integration](https://docs.snowflake.com/en/user-guide/scim) — Automated user provisioning

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

#### Who should own this data product? (`owner_users`: list)
Enter the usernames of users who should own this data product. At least one owner is required.

**What is a username?**
The Snowflake login name, not the display name. You can find usernames by running:
```sql
SHOW USERS;
```

**Who should be an owner?**
- Data steward or product owner
- Lead data engineer
- Service account for automation (if applicable)

**Recommendation:** Assign 1-2 owners maximum. Too many owners dilutes accountability.

**Examples:**
```
john.smith
jane.doe
```

**More Information:**
* [SHOW USERS](https://docs.snowflake.com/en/sql-reference/sql/show-users) — List users in account

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
