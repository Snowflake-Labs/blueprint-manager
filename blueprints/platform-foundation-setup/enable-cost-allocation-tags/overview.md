In this step, you'll decide whether to extend the tagging framework established in previous steps with the additional **cost allocation tags** recommended below. Tags are essential key-value pairs that help you organize, track, and analyze spending across your Snowflake resources. Potential cost allocation tags could include:

* COST_CENTER \- Accounting cost center code  
* OWNER \- Team or individual responsible  
* PROJECT \- Specific project or initiative  
* APPLICATION \- Application or system name

## Why is this important?

Cost allocation tags enable robust Financial Opertations (FinOps) practices:

* **Chargeback**: Bill business units for their actual usage  
* **Showback**: Show teams their spending without billing  
* **Optimization**: Identify high-cost areas for optimization  
* **Accountability**: Track who's responsible for resources

## Account Context 
This step should be executed in your Organization Account (if created) or your primary account.

## Prerequisites

*  Determine financial ownership and responsibility structure for your Snowflake resources

## Key Concepts

**What is a tag in Snowflake?**

A [tag](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) is a schema-level object that can be assigned to another Snowflake object. Tags are stored as key-value pairs, where the tag name is the key and you associate a string value when assigning the tag to an object.

**How do tags enable cost tracking in Snowflake?**

[Tags](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) created for cost allocation purposes can be applied to warehouses, databases, and other objects can be joined with Snowflake's [ACCOUNT\_USAGE views](https://docs.snowflake.com/en/sql-reference/account-usage) (e.g., WAREHOUSE\_METERING\_HISTORY, TAG\_REFERENCES) to calculate credit consumption by tag value. This enables you to build cost allocation reports that aggregate spending by cost center, team, or project. See [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) for detailed examples.

## Best Practices 

**Decide if you want to implement cost allocation tags early!** 

It is significantly easier to implement tags when you first set up your environment. While you can add tags to existing objects at any time, historical consumption data in Snowflake's usage views is recorded without tag context—you cannot retroactively associate past credit usage with newly applied tags. This means any cost allocation reports will only reflect tagged usage from the point tags were applied forward.

## More Information

* [Introduction to Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) — Overview of Snowflake's tagging framework  
* [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) — Using tags for cost allocation and reporting

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

#### Do you want to add additional cost allocation tags? (`enable_cost_tags`: multi-select)
**What is this asking?** Decide whether you want to configure additional cost allocation tags beyond the core platform tags.  

  **Why does this matter?** Additional cost tags enable more granular cost tracking and can integrate with your organization's accounting systems.  

  **Tags you already have for platform management:**  
  * domain \- Business unit or department  
  * environment \- SDLC stage (dev, test, prod)  
  * dataproduct \- Data product identifier  
  * workload \- Workload type  
  * zone \- Data zone  
  * data\_classification \- Data sensitivity level  

* **Additional tags below would be configured in next step:**  
  * cost\_center \- Accounting cost center code  
  * owner \- Team or individual responsible  
  * project \- Specific project or initiative  
  * application \- Application or system name  

* **Options explained:**  
  **Yes (Recommended):**  
  * Proceed to the next step to create additional FinOps and cost allocation tags
* **No:**  
  * Use only the core platform tags (Domain, Environment, etc.) from previous steps for FinOps  
  * Can add more tags later if needed  

* **Recommendation:** Select Yes to proceed to the next step where you can add at least cost\_center and owner tags for better financial accountability.  

**More Information:**  
  * [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing)
**Options:**
- Yes
- No
