In this step, you'll decide whether or not to enable an [**Organization Account**](https://docs.snowflake.com/en/user-guide/organization-accounts). The Organization Account provides centralized management, unified billing, and the ability to create and manage multiple Snowflake accounts. Note: Organization accounts are only available for [Snowflake Edition](https://docs.snowflake.com/en/user-guide/intro-editions) **Enterprise** or higher (it is not available your only account is Standard edition).

## **Why is this important?**

It is strongly recommended that all customers with Enterprise or higher account editions create Organization Accounts. Even if you're leaning toward a single account strategy initially, if there is any potential in the future for more than one account, it will be best to setup the organization account at the onset as this allows for centralization of several key features. See the [documentation](https://docs.snowflake.com/en/user-guide/organization-accounts) for more details.

## **Key Concepts**

It is important to note that an "Organization" is distinct from an Organization Account:

* [**Organization**](https://docs.snowflake.com/en/user-guide/organizations): An Organization is a Snowflake object that links the accounts owned by your business entity.  
  * **Organization Name** \= the name of your business entity that appears in your [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)  
* [**Organization Account**](https://docs.snowflake.com/en/user-guide/organization-accounts): a special type of account that provides centralized management capabilities to oversee and manage multiple Snowflake accounts. It has ORGADMIN privileges that manages other accounts.  
  * **Organization Account Name** \= the name of your Organization Account

## **What happens next based on your decision**

Your decision here determines where all subsequent configuration steps will be executed:

**If you create an Organization Account:**

* The next step will be to create the Organization Account from your current (initial) account  
* After that, you will **switch to the new Organization Account**  
* The remainder of this workflow will be executed **in the Organization Account**  
* Your initial account becomes a regular member account of your organization

**If you do NOT create an Organization Account:**

* All subsequent steps will be executed in your **current account**  
* This is appropriate for single-account strategies with no plans for expansion

## **Prerequisites**

* If you want to create an Organization Account, you'll need to ensure you select or upgrade to [Snowflake Enterprise Edition](https://docs.snowflake.com/en/user-guide/intro-editions) or higher

## **More Information**

* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts) — Overview and capabilities of organization accounts  
* [ORGADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#orgadmin-role) — Permissions and responsibilities  
* [Creating Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts-create) — How to create accounts within an organization  
* [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) – Snowflake Edition options

### Configuration Questions

#### Do you want to create an Organization Account? (`enable_org_account`: multi-select)
The Organization Account is a special account that provides centralized management capabilities for your Snowflake environment.  
  
  **⚠️ Strong Recommendation: Create an Organization Account**  
  We strongly recommend creating an Organization Account, even if you have selected a Single Account strategy. Here's why:  
  * **Future-proofing:** If there's any potential for adding accounts later, having the Organization Account already set up makes expansion seamless  
  * **Centralized features:** Access to organization-level views, billing, and governance features  
  * **Easier migration:** Moving to a multi-account strategy later is significantly easier with an existing Organization Account  
  * **No downside:** The Organization Account has minimal overhead and doesn't impact your single-account operations  
* **For Multi-Account Strategies:** An Organization Account is **required**. It provides:  
  * Centralized view of all accounts  
  * Unified billing and cost management  
  * Ability to create and manage child accounts programmatically  
  * Organization-level policies and governance  
* **Requirements:**  
  * Snowflake Enterprise Edition or higher  
  * [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts) — Overview and capabilities of organization accounts  
  * [ORGADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#orgadmin-role) — Permissions and responsibilities  
  * [Snowflake Editions](https://docs.snowflake.com/en/user-guide/intro-editions) – Snowflake Edition options 
**Options:**
- Yes
- No
