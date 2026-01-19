In this step, you'll identify which Snowflake account this data product will be deployed to. This step captures:

1. **Target Account Name** (`target_account_name`) — The specific account where all data product objects will be created
2. **Access Confirmation** (`target_account_access_confirmed`) — Verification that you have appropriate access

This information is used throughout the remainder of the workflow:
- **SQL Comments**: All generated SQL includes the target account name for documentation
- **Connection Context**: Ensures you're logged into the correct account before executing commands
- **Naming Logic**: For multi-account strategies, the account name may influence object naming (e.g., domain or environment is already in the account name)

**Note:** This step is only shown for multi-account strategies. For single-account deployments, the target is implicitly your only account.

**Account Context:** This step captures context for subsequent SQL generation.

## **Why is this important?**

In a multi-account Snowflake environment, it's critical to know which account you're deploying to:
- **Prevents errors**: SQL executed in the wrong account creates objects in the wrong place
- **Documentation**: Generated SQL includes account context in comments
- **Cost allocation**: Resources are attributed to the correct account
- **Governance**: Access controls are applied in the correct context

Think of this as selecting which "building" you're setting up a new office in — you need to know where you are before you start arranging furniture.

## **Prerequisites**

- Multi-account strategy selected in Platform Foundation
- Target account exists (run Account Creation workflow if needed)
- Access to the target account with appropriate roles

## **Key Concepts**

**Multi-Account Strategies**
Depending on your account strategy, accounts may be organized by:
- **Domain-based**: Each account represents a business domain (Sales, Finance, etc.)
- **Environment-based**: Each account represents an SDLC environment (Dev, Prod, etc.)
- **Domain + Environment**: Each account represents a specific combination (Sales-Dev, Finance-Prod, etc.)

**Target Account**
The Snowflake account where this data product's resources will be created. All databases, schemas, warehouses, and roles will exist in this account.

**More Information:**
* [Managing Accounts in an Organization](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Multi-account management
* [Snowflake Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Organization overview

### Configuration Questions

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
