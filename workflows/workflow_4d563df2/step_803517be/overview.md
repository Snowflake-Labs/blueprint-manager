In this step, you'll decide whether to extend the tagging framework established in the Platform Foundation task with additional **cost allocation tags**. Tags are essential key-value pairs that help you organize, track, and analyze spending across your Snowflake resources.

**Note:** In the Platform Foundation task (Create Infrastructure Database and Define Object Naming Conventions steps), you already created core FinOps tags: `domain`, `environment`, `dataproduct`, `workload`, and `zone`. This step adds optional cost-focused tags like `cost_center` and `owner` for enhanced financial tracking.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

Cost allocation tags enable robust FinOps practices:
- **Chargeback**: Bill business units for their actual usage
- **Showback**: Show teams their spending without billing
- **Optimization**: Identify high-cost areas for optimization
- **Accountability**: Track who's responsible for resources

**How it works:** Tags applied to warehouses, databases, and other objects can be joined with Snowflake's [ACCOUNT_USAGE views](https://docs.snowflake.com/en/sql-reference/account-usage) (e.g., `WAREHOUSE_METERING_HISTORY`, `TAG_REFERENCES`) to calculate credit consumption by tag value. This enables you to build cost allocation reports that aggregate spending by cost center, team, or project. See [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) for detailed examples.

## External Prerequisites

- Cost center codes from your accounting system (if applicable)
- Ownership/responsibility structure for resources

## Key Concepts

**Existing Tags (from Platform Foundation task)**
- `domain` - Business unit (equivalent to Business Unit)
- `environment` - SDLC stage (Dev, Test, Prod)
- `dataproduct` - Data product identifier
- `workload` - Workload type (Ingest, Transform, BI, etc.)
- `zone` - Data zone (Raw, Curated, Consumption, etc.)

**Additional Cost Tags (this step)**
- `cost_center` - Accounting cost center code
- `owner` - Team or individual responsible
- `project` - Specific project or initiative
- `application` - Application or system name

**Tag Inheritance**
Snowflake uses tag inheritance for data governance (e.g., [Masking Policies](https://docs.snowflake.com/en/user-guide/tag-based-masking-policies)), but this does **not** apply to cost allocation. Cost allocation tags must be applied directly to the resource (Warehouse, Database) you want to track.

**Tag Limits**
Plan your strategy efficiently—Snowflake has [limits on the number of tags](https://docs.snowflake.com/en/user-guide/object-tagging#tag-quotas) you can create and apply per object. Start with essential tags and expand as needed.

**Implementation Timing**
It's significantly easier to implement tags when you first set up your environment. While you can add tags to existing objects at any time, historical consumption data in Snowflake's usage views is recorded without tag context—you cannot retroactively associate past credit usage with newly applied tags. This means any cost allocation reports will only reflect tagged usage from the point tags were applied forward.

## More Information

* [Introduction to Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) — Overview of Snowflake's tagging framework
* [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) — Using tags for cost allocation and reporting

### Configuration Questions

#### What do you want to name the governance schema? (`governance_name`: text)
**What is the Governance Schema?**  
The Governance schema is created within the Infrastructure Database and contains objects related to security, compliance, and platform governance. This includes FinOps tags, network rules, audit views, and administrative procedures.  

**Recommended Name:** `GOVERNANCE`  

This is a straightforward, self-descriptive name that clearly communicates the schema's purpose. Alternative options include:  
* `ADMIN` — Administration  
* `SECURITY` — Security-focused objects  
* `PLATFORM` — Platform-level objects  

**Schema Configuration:**  
This schema will be created with **Managed Access** enabled, which means:  
* Only the schema owner (typically SYSADMIN) can grant privileges on objects  
* Prevents "shadow" security configurations where object creators grant their own access  
* Provides centralized control over who can access governance objects  

**Best Practice:** Use a simple, single-word name that represents the functional purpose.  

**More Information:**  
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)  
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)  

#### Do you want to add additional cost allocation tags? (`enable_cost_tags`: multi-select)
**What is this asking?**
Decide whether to create additional tags beyond the core FinOps tags already configured in the Platform Foundation task.

**Why does this matter?**
Additional cost tags enable more granular cost tracking and can integrate with your organization's accounting systems.

**Tags you already have (from Platform Foundation task):**
- `domain` - Business unit or department
- `environment` - SDLC stage (dev, test, prod)
- `dataproduct` - Data product identifier
- `workload` - Workload type
- `zone` - Data zone

**Additional tags this step can add:**
- `cost_center` - Accounting cost center code
- `owner` - Team or individual responsible
- `project` - Specific project or initiative
- `application` - Application or system name

**Options explained:**

**Yes (Recommended):**
- Add cost center mapping for chargeback
- Track ownership for accountability
- Enable project-level cost tracking

**No:**
- Use only the core tags from the Platform Foundation task
- Simpler setup, less granular tracking
- Can add more tags later if needed

**Recommendation:**
Add at least `cost_center` and `owner` tags for better financial accountability.

**More Information:**
* [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing)
**Options:**
- Yes
- No

#### What do you want to name the platform database? (`platform_database_name`: text)
**What is the Platform/Infrastructure Database?**  
The Infrastructure Database is a centralized "hub" database that houses platform-wide objects including FinOps tags, network rules, governance policies, and shared procedures. It is owned by the central platform team and shared across all accounts in multi-account deployments.  

**Recommended Naming Approach:**  
Use a name that clearly identifies this as a platform-owned, infrastructure-focused database. The format should be: `<domain>_<dataproduct>`  

* **Domain:** Use `plat` (short for "platform") or your platform team's acronym (e.g., `cdp`, `snow`, `data`)  
* **Data Product:** Use `infra` or another term indicating infrastructure purpose  

**Example:** `PLAT_INFRA` — clearly indicates Platform team ownership and Infrastructure purpose  

**Alternative Examples:**  
* `CDP_INFRA` — Cloud Data Platform Infrastructure  
* `SNOW_ADMIN` — Snowflake Administration  
* `DATA_PLATFORM` — Data Platform database  

**Important:** Choose carefully! This name will be referenced by hundreds of objects, policies, and procedures. Changing it later is extremely complex and risky.  

**More Information:**  
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)  
* [Object Identifiers](https://docs.snowflake.com/en/sql-reference/identifiers)  
