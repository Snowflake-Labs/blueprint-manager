In this step, you'll configure additional cost allocation tags beyond the core tags from the Platform Foundation task. You'll define which dimensions to add and set up cost reporting views to analyze spending by tag.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

Extending your tag framework enables:
- **Cost center mapping** for chargeback to accounting
- **Ownership tracking** for accountability
- **Project-level visibility** for initiative-based cost tracking
- **Cost reporting views** for analyzing spending patterns

## External Prerequisites

- Cost center codes from your accounting system
- Ownership/responsibility assignments for resources

## Key Concepts

**Tag Dimensions**
The categories of tags you'll use for cost allocation (e.g., cost_center, owner).

**Tag Enforcement**
Whether tags are required when creating new resources. Tag policies require Enterprise Edition or higher.

**Cost Reporting Views**
Pre-built views that join tag data with consumption data for analysis.

**Start Simple**
Begin with Essential or Minimal dimensions and expand as your FinOps maturity grows. You can always add more tags later.

**Automate Tag Application**
Use SQL scripts or IaC tools to automate tag application and reduce manual errors.

**Enforce Production at Minimum**
At a minimum, consider requiring tags on production resources to ensure cost visibility where it matters most.

## More Information

* [Introduction to Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging/introduction) — Overview of Snowflake's tagging framework
* [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) — Using tags for cost allocation and reporting

### Configuration Questions

#### What credit limit should the account resource monitor enforce? (`account_resource_monitor_limit`: text)
**What is this asking?**
Set the maximum number of credits the account can consume before the configured action (at 100%) is taken.

**Why does this matter?**
This is your hard limit. The resource monitor will automatically set up tiered alerts:
- At 75% of this limit: First notification
- At 90% of this limit: Second notification
- At 100% of this limit: Your selected action (Suspend/Notify)
- At 110%: Post-limit notification

**How to determine your limit:**
- Align with or slightly exceed your monthly budget
- Consider setting 10-20% higher than expected usage as a safety buffer
- Account for all warehouses that will be created

**Example:**
If your monthly budget is 1,000 credits:
- Set limit to 1,000 credits
- First alert at 750 credits (75%)
- Second alert at 900 credits (90%)
- Action triggered at 1,000 credits (100%)

**Relationship to Budgets:**
If you set a budget of 1,000 credits with a 75% threshold, you'll receive budget forecasting alerts *before* the resource monitor's 75% actual usage alert—giving you even earlier warning.

**Warning:** When the limit is reached and suspension is configured, ALL warehouses will be affected.

#### Do you want to set up spending budgets? (`enable_budgets`: multi-select)
**What is this asking?**
Decide whether to use Snowflake's native budget feature for automated spending monitoring and alerts.

**Why does this matter?**
Budgets provide proactive cost awareness by sending alerts when spending is projected to exceed your defined limits. This helps prevent unexpected costs and enables better financial planning.

**Options explained:**

**Yes (Recommended):**
- Use Snowflake's native budget feature
- Set monthly spending limits (in credits)
- Receive automated email alerts when thresholds are exceeded
- Time-series forecasting predicts budget overruns
- No additional infrastructure required

**No:**
- Monitor spending without automated alerts
- Suitable if you have other cost control mechanisms
- Can still use Resource Monitors for hard limits

**Recommendation:**
Use Snowflake's native budgets for automated monitoring and alerts. They're easy to set up and provide valuable early warning of cost overruns.

**More Information:**
* [Monitor credit usage with budgets](https://docs.snowflake.com/en/user-guide/budgets)
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

#### Do you want to configure resource monitors? (`enable_resource_monitors`: multi-select)
**What is this asking?**
Decide whether to implement an account-level resource monitor for active cost control.

**Why does this matter?**
Resource monitors provide hard credit limits that can automatically suspend warehouses when reached. This prevents runaway costs from misconfigured warehouses or inefficient queries.

**Options explained:**

**Yes (Recommended for Production):**
- Automatically suspend ALL warehouses at credit limits
- Prevent runaway costs across entire account
- Real-time protection for total spending
- Required for cost-sensitive environments

**No:**
- Rely on budgets and manual monitoring
- More flexible but higher risk of cost overruns
- Not recommended for production environments

**Note:** This creates an account-level monitor only. Warehouse-specific monitors will be configured in the Data Product workflow.

**Recommendation:**
Always use an account resource monitor in production environments to prevent unexpected costs.

**More Information:**
* [Working with Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
**Options:**
- Yes
- No

#### Which additional tag dimensions will you use? (`additional_tag_dimensions`: multi-select)
**What is this asking?**
Select which additional tags to create beyond the core tags from the Platform Foundation task.

**Why does this matter?**
Different organizations need different levels of cost tracking granularity.

**Options explained:**

**All (Cost Center, Owner, Project, Application):**
- `cost_center` - Accounting cost center code
- `owner` - Team or individual responsible
- `project` - Specific project or initiative
- `application` - Application or system name
- Best for: Large organizations with complex cost allocation

**Essential (Cost Center, Owner):**
- `cost_center` - For chargeback to accounting
- `owner` - For accountability
- Best for: Most organizations with standard chargeback requirements

**Minimal (Owner only):**
- `owner` - Track who's responsible for resources
- Best for: Small organizations or those just getting started

**Recommendation:**
Start with Essential (Cost Center, Owner). Add more as your FinOps practices mature.
**Options:**
- All (Cost Center, Owner, Project, Application)
- Essential (Cost Center, Owner)
- Minimal (Owner only)

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

#### Should these tags be required on new resources? (`require_cost_tags`: multi-select)
**What is this asking?**
Decide whether tagging should be a governance requirement when new resources are created.

**Why does this matter?**
Required tags ensure complete cost visibility but add governance overhead.

**How enforcement works:**
Snowflake doesn't automatically prevent creating resources without tags. Enforcement is achieved through:
- **Monitoring**: This step creates an `untagged_warehouses` view to identify resources missing required tags
- **Governance processes**: Document tagging requirements in your provisioning procedures
- **Role-based access**: Limit who can create warehouses/databases and train those teams on tagging requirements
- **Regular audits**: Periodically review the `untagged_warehouses` view and remediate

**Options explained:**

**Yes (all resources):**
- Governance policy: all new warehouses and databases must be tagged
- Ensures complete cost visibility
- Use `untagged_warehouses` view for compliance monitoring

**Yes (production only):**
- Governance policy: production resources must be tagged
- Development/test resources have optional tagging
- Balances visibility with flexibility

**No (optional):**
- Tags are optional on all resources
- Maximum flexibility
- Risk of incomplete cost tracking

**Recommendation:**
Use "Yes (production only)" to ensure production cost visibility while allowing development flexibility. Regardless of choice, regularly review the `untagged_warehouses` view to maintain cost visibility.
**Options:**
- Yes (all resources)
- Yes (production only)
- No (optional)

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

#### What action should be taken when the limit is reached? (`resource_monitor_action`: multi-select)
Choose the action when credit limit is hit:

**Suspend Immediately**:
- Stops all running queries
- Suspends all warehouses
- Prevents any additional costs
- Most aggressive protection

**Suspend After Current Queries**:
- Allows running queries to complete
- Suspends warehouses after completion
- Prevents new queries
- Balances protection with user experience

**Notify Only**:
- Sends alert but doesn't suspend
- Requires manual intervention
- Least disruptive but less protective

Best Practice: Use "Suspend After Current Queries" for production to protect costs while minimizing disruption.
**Options:**
- Suspend Immediately
- Suspend After Current Queries
- Notify Only

#### What is your monthly account budget (in credits)? (`account_monthly_budget`: text)
**What is this asking?**
Set the total monthly credit budget for your Snowflake account. This is the spending limit used to calculate when alerts are triggered.

**Why does this matter?**
A well-set budget provides meaningful alerts without being too restrictive. Setting it too low causes alert fatigue; too high means late warnings.

**How to determine your budget:**
- Base it on your Snowflake contract or expected usage
- Include a buffer for growth (recommend 20-30% above expected usage)
- Consider seasonal variations in workload

**Example:**
If you expect to use 1,000 credits/month, set budget to 1,200-1,300 credits.

**Note:** 1 credit ≈ $2-4 depending on your Snowflake edition and region.

**Important:** This is for alerting purposes only. Snowflake will not automatically stop services when the budget is exceeded. Use Resource Monitors (Configure Resource Monitors step) for hard limits.
