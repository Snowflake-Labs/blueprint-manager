In this step, you'll define the purpose of the new Snowflake account by selecting the business domain it represents. In a domain-based multi-account strategy, each account corresponds to a business domain (e.g., Sales, Finance, HR).

**Account Context:** This step should be executed from your Organization Account.

## Why is this important?

In a domain-based strategy:
- Each account represents a distinct business domain
- Environments (Dev, Test, Prod) are organized **within** the account at the database level
- This provides strong isolation between business units
- Cost allocation at the account level is by domain

## External Prerequisites

- Platform Foundation workflow completed with Domain-based Multi-Account strategy
- Knowledge of which business domain this account will serve

## Key Concepts

**Domain-based Account Strategy**
Each Snowflake account represents a business domain. Within each domain account, you'll create separate databases or schemas for different environments (handled in the Data Product workflow).

**Domain**
The business unit or functional area this account serves. Domains were defined in the Platform Foundation task (e.g., Sales, Finance, HR, Engineering).

**Environment at Database Level**
In this strategy, environments (Dev, Test, Prod) are NOT at the account level. They will be created as separate databases or schemas within this account when you run the Data Product workflow.

**More Information:**
* [Managing Accounts in an Organization](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account management overview

### Configuration Questions

#### Which domain will this account represent? (`account_domain`: multi-select)
**What is this asking?**
Select the business domain this account will represent. This account will serve all environments (Dev, Test, Prod) for this domain.

**Why does this matter?**
- The domain becomes part of the account name
- Cost allocation at the account level will be attributed to this domain
- All resources in this account are associated with this domain

**Note on Environments:**
Since you're using a domain-based strategy, environments (Dev, Test, Prod) will be organized **within** this account at the database level. You'll configure environments when creating data products.

**More Information:**
* [Managing Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account management overview

#### Provide a brief description of this account's purpose. (`account_description`: text)
**What is this asking?**
Write a short description that explains what this account is for.

**Why does this matter?**
A clear description helps team members understand the account's purpose at a glance. It appears in account listings and documentation, making governance and auditing easier.

**Examples:**
- "Sales domain account - contains all environments for Sales analytics"
- "Finance domain account for financial reporting and analytics"
- "HR domain account for people analytics and workforce planning"

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
