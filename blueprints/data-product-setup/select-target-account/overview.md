In this step, you'll identify which Snowflake account will host your data product. For multi-account strategies, this determines where all databases, schemas, warehouses, and roles will be created.

**Account Context:** This step is for planning only. You'll need to connect to the selected account before executing SQL in subsequent steps.

## Why is this important?

The target account determines:
- **Resource Location**: Where databases, warehouses, and roles are created
- **Cost Attribution**: Which account incurs compute and storage costs
- **Access Boundaries**: Users need access to this account to use the data product
- **Naming Implications**: For domain-based and environment-based strategies, the account name may imply certain naming components

## Prerequisites

- Platform Foundation completed with multi-account strategy selected
- Target account already exists (created via Account Creation workflow)
- Network connectivity to the target account

## Key Concepts

**Account Selection by Strategy**

| Strategy | Account Name Pattern | Example |
|----------|---------------------|---------|
| Multi-Account (Environment-based) | `<environment>` | `PROD`, `DEV`, `TEST` |
| Multi-Account (Domain-based) | `<domain>` | `FIN`, `MKT`, `OPS` |
| Multi-Account (Domain + Environment) | `<domain>_<environment>` | `FIN_PROD`, `MKT_DEV` |

**Implied Naming Components**

When you select an account, certain naming components become implicit:
- **Environment-based**: Environment is implied by account, excluded from object names
- **Domain-based**: Domain is implied by account, excluded from object names
- **Domain + Environment**: Both are implied, minimal object naming

**More Information:**
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding account names
* [Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Multi-account management


### Configuration Questions

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
