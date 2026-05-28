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

#### Which domain will this account represent? (`account_domain`: single-select)
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

#### What prefix (if any) should be added to all account names? (`account_name_prefix`: text)
An account name prefix is an optional string added to the beginning of every account name for consistency and organization identification.  

**When to use a prefix:**  
* If your organization name is system-generated (e.g., `XY12345`) and you want your company name visible in account names  
* If you want to enforce consistent naming across all accounts  
* If you have multiple organizations or business units sharing Snowflake and need differentiation  

**Example with prefix:**  
* Prefix: `acme`  
* Account names become: `acme_prod`, `acme_dev`, `acme_finance`  
* URL: `https://XY12345-acme_prod.snowflakecomputing.com`  

**Example without prefix:**  
* Account names: `prod`, `dev`, `finance`  
* URL: `https://ACME-prod.snowflakecomputing.com`  

**Recommendations:**  
* If you have a **custom organization name** (like `ACME`), a prefix is typically unnecessary since your identity is already in the URL  
* If you have a **system-generated name**, consider using an abbreviated company name as a prefix  
* Keep prefixes short (3-8 characters) with no underscores  

**Enter `NONE` if you do not want to use an account name prefix.**  

**More Information:**  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)

#### What is your Snowflake organization name? (`snowflake_org_name`: text)
Your Snowflake organization name is the first part of your account URL and connection identifiers. This is a required component of all Account Identifiers.  
  **How to find your organization name:**  
  Look at your current Snowflake URL. The organization name is the portion before the dash:  
  * https://\*\*ACME\*\*-prod.snowflakecomputing.com → Organization name is ACME  
  * https://\*\*XY12345\*\*-prod.snowflakecomputing.com → Organization name is XY12345  
* **Types of Organization Names:**  
  * **Custom Name:** A human-readable name like ACME or INITECH that was requested from Snowflake. These provide better branding and more readable URLs.  
  * **System-Generated:** An auto-assigned alphanumeric code like XY12345 or AB98765, created automatically during self-service sign up. Companies typically keep this name if transparency of your organization name in the URL is unnecessary or undesirable.   
* **To request a custom name:** If you have a system-generated name and want to change it, [contact Snowflake Support](https://community.snowflake.com/s/article/How-To-Submit-a-Support-Case-in-Snowflake-Lodge) or your account team. Custom names must be globally unique, start with a letter, and contain only letters and numbers.  
  **More Information:**  
  * [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) 

#### What account strategy do you wish to implement? (`account_strategy`: single-select)
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
