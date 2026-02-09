In this step, you'll confirm or select the multi-account strategy for your organization. This setting was typically established during the Platform Foundation workflow, but if you're running Account Creation directly, you'll need to specify it here.

**Account Context:** This step should be executed from your Organization Account.

## **Why is this important?**

The account strategy determines:
- How accounts are organized (by domain, environment, or both)
- What information is captured for each account
- How cost allocation tags are applied
- The overall structure of your Snowflake organization

## **Prerequisites**

- Access to Organization Account with ORGADMIN role
- Understanding of your organization's multi-account strategy

## **Key Concepts**

**Organization-Level Setting**
This is an organization-level answer that persists across all runs of the Account Creation workflow. Once set, you won't need to answer this question again for future accounts.

**Multi-Account Strategies**
Snowflake supports several approaches to organizing multiple accounts:

| Strategy | Account Represents | Best For |
|----------|-------------------|----------|
| Domain-based | Business unit (Sales, Finance, HR) | Strong domain isolation, environments within each domain |
| Environment-based | SDLC stage (Dev, Test, Prod) | Strong environment isolation, domains within each environment |
| Domain + Environment | Specific combination (Sales-Prod) | Maximum isolation, most accounts |

**Already Completed Platform Foundation?**
If you completed the Platform Foundation workflow, your account strategy was already captured. Simply confirm the same selection here to ensure consistency.

**More Information:**
* [Managing Accounts in an Organization](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts) — Account management overview

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
