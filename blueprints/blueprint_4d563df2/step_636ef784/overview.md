In this step, you'll record your Snowflake **organization name**, which is a critical component of all connection URLs and account identifiers. For example, in the URL https://ACME-prod.snowflakecomputing.com, the organization name is "ACME". 

This value is used throughout subsequent steps to construct connection URLs, SCIM endpoints, SAML configurations, and documentation. Every account you create will include this organization name in its URL, so it's essential to record the correct value now.

**Note:** This step captures your *existing* organization name—it does not create or change it. If you have a system-generated name (like XY12345) and want a custom name before proceeding with this and subsequent steps, you'll need to contact Snowflake Support separately first.

## **Why is this important?**

An organization is a Snowflake object that links the accounts owned by your business entity. Once your organization name is established, and account(s) are established with users and systems securely connecting to Snowflake using your Account Identifiers and URLs, it is difficult to change the organization name in all the places that would require the change. **For this reason, we strongly encourage customers to plan ahead and ensure that their Organization Name meets their future connectivity needs.** 

## **Prerequisites**

* Locate your **current Organization Name** \- before confirming your organization name in this step, you should determine if you want to change the current organization name first. To find this, look at your current Snowflake URL. The organization name is the portion before the dash. For example:  
  * https://ACME-prod.snowflakecomputing.com → the Organization name is ACME  
  * https://XY12345-prod.snowflakecomputing.com → the Organization name is XY12345

## **Key Concepts**

[**Account identifiers**](https://docs.snowflake.com/en/user-guide/admin-account-identifier) identify a Snowflake account within your organization. They are required in Snowflake wherever you need to specify the account you are using, including but not limited to:

* URLs for accessing any of the Snowflake web interfaces.  
* Snowflake CLI, SnowSQL, and other clients (connectors, drivers, etc.) for connecting to Snowflake.  
* Third-party applications and services that comprise the Snowflake ecosystem.

How Account Identifiers are used/structured when connecting to Snowflake:

* URL for signing into the Snowflake UI: \<orgname\>-\<account\_name\>.snowflakecomputing.com  
* Configuring a client, driver, or library to connect to Snowflake: \<orgname\>-\<account\_name\>

As seen in the examples above, Account Identifiers consist of two key components:

1. \<orgname\> is the name of your Snowflake organization. An organization is a Snowflake object that links the accounts owned by your business entity.  
2. \<account\_name\> is the unique name of your account within your organization. You specify an account name when you create a new account, but it can be [changed](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts-rename).

There are two ways an Organization \<orgname\> can be named:

1. **Custom Named:** If you worked directly with your Snowflake account team on initial setup activities, Snowflake can assign a custom name for the organization. You can also reach out to Snowflake Support to customize/change a system-generated name.  
2. **System-Generated:** if your initial Snowflake account was created using the self-service option, a globally unique organization name is system-generated for you (e.g., XY12345, AB98765)

In this step, you'll decide which type of Organization Name (System-Generated or Custom) you want to use. As mentioned above, once your organization name is established and users and systems are connecting securely to Snowflake with your Account Identifiers and URLs, it is difficult to change the organization name in all the places that would require the change. For this reason, it's important to consider this decision up front\!

**NOTE**: this step focuses on the Organization Name only; how to establish and manage Account and other object naming conventions will be covered in subsequent steps\!

## **Option Details** 

### Customize your Organization name

For customers who work directly with their Snowflake account team on initial setup activities, Snowflake may have already assigned a custom name for the organization. If you have a system generated name but want to change to a custom, human-readable name, [contact Snowflake Support](https://docs.snowflake.com/en/user-guide/admin-account-identifier#organization-and-account-names) or your account team to request a custom organization name and they’ll work with you to find a suitable, available name.

**Example**  
URL: https://acme-prod.snowflakecomputing.com

* Organization name \= ACME (custom)  
* Account name \= prod \- with custom org names, account names can be kept simple since the org name already provides context in the URL

**Guidance for custom Organization names:**

* This custom name must be unique across all other organizations in Snowflake.  
* The name must start with a letter and can only contain letters and numbers.  
* The name cannot contain underscores or other delimiters.  
* The name should be succinct (3-8 characters)

✅ **Choose this strategy:**

* Better brands your snowflake account w/ your customers; e.g., ACME vs XY12345  
* Makes URLs more succinct & readable

❌ **Avoid this approach:**

* Transparency of your organization in URLs is unnecessary or undesirable

### Use the system-generated organization name 

You can keep the system-generated organization name (e.g., XY12345) for privacy or simplicity. The account names themselves can still be descriptive.

**Example**  
URL: https://xy12345-prod.snowflakecomputing.com

* Organization Name \= XY12345 (system-generated)  
* Account Name \= prod \- Account names can be descriptive even with system-generated org names

✅ **Choose this approach if:**

* Transparency of your organization name in the URL is unnecessary or undesirable  
* You prefer to keep the default system-generated name

❌ **Consider a custom name instead if:**

* You want your organization name visible in URLs for branding  
* You want more readable, professional-looking URLs

## **More Information**

* [Account Identifiers](https://docs.snowflake.com/en/user-guide/admin-account-identifier) — Understanding organization and account names in URLs  
* [Organizations](https://docs.snowflake.com/en/user-guide/organizations) — Overview of Snowflake organizations  
* [Renaming an Account](https://docs.snowflake.com/en/user-guide/organizations-manage-accounts-rename) — How to change account names

### Configuration Questions

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
