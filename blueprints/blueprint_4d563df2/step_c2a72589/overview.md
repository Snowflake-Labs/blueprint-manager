In this step, you'll create the foundational objects that will be used throughout the rest of this workflow and in future workflows:

1. **Infrastructure Database** — A centralized database that serves as the "home" for all platform-wide governance and administrative objects  
2. **Governance Schema** — A schema within the database (with Managed Access enabled) where tags, network rules, and policies will be stored

Objects created in subsequent steps, such as Tags to standardize database object names and enable cost allocation, and Network Rules and Policies, will be stored in this database and schema. 

## Why is this important?

Regardless of whether you're implementing a single or multi-account strategy, by housing these objects in a single dedicated infrastructure database, you ensure that governance is consistent across your entire organization. In multi-account environments, this database can be shared from your Organization Account to child accounts, ensuring that every business unit uses the same standardized metadata and security boundaries.

## Account Context

This step should be executed in your [Organization Account](https://docs.snowflake.com/en/user-guide/organization-accounts) (if created) or your primary account.

## Key Concepts

In this step you'll create an Infrastructure Database and Governance Schema. Below is a reminder of where these objects fit in the Snowflake Object Hierarchy.

![Snowflake Object Hierarchy](../../images/account_strategy_images/snowflake_object_hierarchy.png)

* **Organization** \- An organization is a first-class Snowflake object that links the accounts owned by your business entity.
* **Snowflake Accounts** \- customers can create one or more accounts.
* **Accounts contain databases** \- each database belongs to a single Snowflake account; databases cannot span multiple accounts but they can be replicated or shared to other accounts.  
* **Databases contain schemas** \- each schema belongs to a single Snowflake database.  
* **Schemas contain objects** \- objects include tables, tags, rules, views, file formats, sequences, UDFs, procedures, etc.

Objects that you'll create and store in this infrastructure database and schema in subsequent steps such as Tags, Network Rules, and Network Policies, will be covered in more detail in subsequent steps.   

## Best Practices

* **Standardize infrastructure naming conventions early:** A central Snowflake platform team will typically own certain account-level objects, therefore, we strongly recommend that your Snowflake platform team selects a designated acronym (e.g., plat, snow, cdp) to identify the central platform team and distinguish their objects from those of other business domains. This name is difficult to change once dozens to hundreds of objects and policies are referencing it, so we recommend selecting and implementing this identifier early on.  

* **Use a [Managed Access Schema](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas):** Managed Access Schema is a security model where the schema owner controls all object privileges, rather than individual object creators. We recommend using Managed Access for schemas to ensure that only the Platform Team (via the SECURITYADMIN or SYSADMIN roles) can grant privileges, preventing "shadow" security configurations.

## How to Test

Once you've executed this step, you can check to ensure it worked with the following commands:

* Verify database existence: SHOW DATABASES LIKE '{{ platform\_database\_name }}';  
* Confirm Managed Access status: SHOW SCHEMAS IN DATABASE {{ platform\_database\_name }}; (Verify the governance schema shows TRUE for is\_managed\_access).

## More Information

* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database) — SQL command reference  
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema) — SQL command reference  
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas) — Centralized privilege management  
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Using tags for governance  
* [Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) — Sharing objects across accounts

### Configuration Questions

#### What do you want to name the platform database? (`platform_database_name`: text)
**What is the Platform/Infrastructure Database?**  
  The Infrastructure Database is a centralized "hub" database that houses platform-wide objects including tags, network rules, governance policies, and shared procedures. It is owned by the central platform team and shared across all accounts in multi-account deployments.  
  **Recommended Naming Approach:**  
  Use a name that clearly identifies this as a platform-owned, infrastructure-focused database. The format should be: \<domain\>\_\<dataproduct\>  
  * **Domain:** Use plat (short for "platform") or your platform team's acronym (e.g., cdp, snow, data)  
  * **Data Product:** Use infra or another term indicating infrastructure purpose  
* **Example:** PLAT\_INFRA — clearly indicates Platform team ownership and Infrastructure purpose  
  **Alternative Examples:**  
  * CDP\_INFRA — Cloud Data Platform Infrastructure  
  * SNOW\_ADMIN — Snowflake Administration  
  * DATA\_PLATFORM — Data Platform database  
* **Important:** Choose carefully\! This name will eventually be referenced by dozens to hundreds of objects, policies, and procedures. Changing it later can be complex and risky.  
  **More Information:**  
  * [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)  
  * [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)

#### What do you want to name the governance schema? (`governance_name`: text)
**What is the Governance Schema?**  
  The Governance schema is created within the Infrastructure Database and contains objects related to security, compliance, and platform governance. This includes platform and FinOps tags, network rules, audit views, and administrative procedures.  

  **Recommended Name:** GOVERNANCE  

  This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:  
  * ADMIN — Administration  
  * SECURITY — Security-focused objects  
  * PLATFORM — Platform-level objects  

**Schema Configuration:**  
  This schema will be created with **Managed Access** enabled, which means:  
  * Only the schema owner (typically [SYSADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system) - aka System Administrator) can grant privileges on objects  
  * Prevents "shadow" security configurations where object creators grant their own access  
  * Provides centralized control over who can access governance objects  

**Best Practice:** Use a simple, single-word name that represents the functional purpose.  
  
**More Information:**  
  * [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)  
  * [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)  
  * [System Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system)
