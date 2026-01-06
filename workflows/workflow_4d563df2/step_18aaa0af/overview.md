In this step, you'll decide whether or not to enable an Organization account and what to name it. The organization account provides centralized management, unified billing, and the ability to create and manage multiple Snowflake accounts. Note: Organization accounts are only available for Snowflake edition **Enterprise** or higher (it is not available your only account is Standard edition). 

## Why is this important?

It is strongly recommended that all customers with Enterprise or higher account editions create Organization accounts. Even if you're leaning toward a single account strategy initially, if there is any potential in the future for more than one account, it will be best to setup the organization account at the onset as this allows for centralization of several key features. See the [documentation](https://docs.snowflake.com/en/user-guide/organization-accounts) for more details.

## What happens next based on your decision

Your decision here determines where all subsequent configuration steps will be executed:

**If you create an Organization Account:**
- The next step will create the Organization Account from your current (initial) account
- After that, you will **switch to the new Organization Account**
- The remainder of this workflow will be executed **in the Organization Account**
- Your initial account becomes a regular member account of your organization

**If you do NOT create an Organization Account (`NONE`):**
- All subsequent steps will be executed in your **current account**
- This is appropriate for single-account strategies with no plans for expansion

## External Prerequisites

* Select or upgrade to Snowflake Enterprise Edition or higher

## Key Concepts

It is important to note that an “Organization” is distinct from an Organization Account:

* **Organization**: An Organization is a Snowflake object that links the accounts owned by your business entity.  
  * **Organization Name** = your Snowflake organization identifier  
* **Organization Account**: a special type of account that provides centralized management capabilities to oversee and manage multiple Snowflake accounts. It has ORGADMIN privileges that manages other accounts.  
  * **Organization Account Name** = the name of your Organization Account

## More Information

* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts) — Overview and capabilities of organization accounts  
* [ORGADMIN Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#orgadmin-role) — Permissions and responsibilities  
* [Creating Accounts](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts-create) — How to create accounts within an organization

### Configuration Questions

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

#### What do you want to name your organization account? (`org_account_name`: text)
The Organization Account is a special account that provides centralized management capabilities for your Snowflake environment. Enter the name you want to use, or enter `NONE` if you do not want to create an organization account.  

**⚠️ Strong Recommendation: Create an Organization Account**  

We strongly recommend creating an Organization Account, even if you have selected a Single Account strategy. Here's why:  

* **Future-proofing:** If there's any potential for adding accounts later, having the Organization Account already set up makes expansion seamless  
* **Centralized features:** Access to organization-level views, billing, and governance features  
* **Easier migration:** Moving to a multi-account strategy later is significantly easier with an existing Organization Account  
* **No downside:** The Organization Account has minimal overhead and doesn't impact your single-account operations  

**For Multi-Account Strategies:** An Organization Account is **required**. It provides:  
* Centralized view of all accounts  
* Unified billing and cost management  
* Ability to create and manage child accounts programmatically  
* Organization-level policies and governance  

**Recommended Name:** `ORG`  

Since there can be only one Organization Account per organization, the name should clearly indicate this special purpose. We recommend simply naming it `ORG`.  

**Example URLs with name `ORG`:**  
* Custom org name: `https://ACME-ORG.snowflakecomputing.com`  
* System-generated with prefix: `https://XY12345-acme_ORG.snowflakecomputing.com`  
* System-generated without prefix: `https://XY12345-ORG.snowflakecomputing.com`  

**Requirements:**  
* Snowflake Enterprise Edition or higher  
* ORGADMIN role granted in the existing account  

**Enter `NONE` only if you are certain you will never need multi-account capabilities.**  

**More Information:**  
* [Organization Accounts](https://docs.snowflake.com/en/user-guide/organization-accounts)  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)  

#### What is your Snowflake organization name? (`snowflake_org_name`: text)
Your Snowflake organization name is the first part of your account URL and connection identifiers. This is a required component of all Account Identifiers.  

**How to find your organization name:**  
Look at your current Snowflake URL. The organization name is the portion before the dash:  
* `https://**ACME**-prod.snowflakecomputing.com` → Organization name is `ACME`  
* `https://**XY12345**-prod.snowflakecomputing.com` → Organization name is `XY12345`  

**Types of Organization Names:**  
* **Custom Name:** A human-readable name like `ACME` or `INITECH` that was requested from Snowflake. These provide better branding and more readable URLs.  
* **System-Generated:** An auto-assigned alphanumeric code like `XY12345` or `AB98765`, created automatically during self-service signup.  

**To request a custom name:** If you have a system-generated name and want to change it, contact Snowflake Support or your account team. Custom names must be globally unique, start with a letter, and contain only letters and numbers.  

**More Information:**  
* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier)  
