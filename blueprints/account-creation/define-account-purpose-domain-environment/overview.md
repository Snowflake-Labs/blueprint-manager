In this step, you'll define the purpose of the new Snowflake account by selecting both the business domain and environment it represents. In a domain + environment multi-account strategy, each account corresponds to a specific domain-environment combination (e.g., Sales-Dev, Finance-Prod).

**Account Context:** This step should be executed from your Organization Account.

## Why is this important?

In a domain + environment strategy:
- Each account represents a specific domain-environment combination
- This provides the strongest isolation (both between domains AND environments)
- Production data is completely separated from development
- Cost allocation at the account level is by both domain and environment

## External Prerequisites

- Platform Foundation workflow completed with Domain + Environment Multi-Account strategy
- Knowledge of which domain and environment combination this account will serve

## Key Concepts

**Domain + Environment Account Strategy**
Each Snowflake account represents a specific combination of business domain and SDLC environment. This is the most granular multi-account approach, providing maximum isolation.

**Domain**
The business unit or functional area (e.g., Sales, Finance, HR).

**Environment**
The SDLC stage (e.g., Dev, Test, Prod).

**Account Granularity**
With this strategy, you'll have accounts like:
- Sales-Dev, Sales-Test, Sales-Prod
- Finance-Dev, Finance-Test, Finance-Prod
- etc.

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

#### Which environment will this account represent? (`account_environment`: multi-select)
**What is this asking?**
Select the SDLC environment this account will represent. This account will serve all domains (Sales, Finance, HR, etc.) for this environment.

**Why does this matter?**
- The environment becomes part of the account name
- Cost allocation at the account level will be attributed to this environment
- All resources in this account are associated with this environment

**Environment Considerations:**
- **DEV/DEVELOPMENT**: Lower security, experimentation allowed
- **TEST/QA**: Moderate security, controlled changes
- **PROD/PRODUCTION**: Highest security, strict change control

**Note on Domains:**
Since you're using an environment-based strategy, domains will be organized **within** this account at the database level. You'll configure domains when creating data products.

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
