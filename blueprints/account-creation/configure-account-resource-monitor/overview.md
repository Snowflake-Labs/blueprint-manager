In this step, you'll configure an account-level resource monitor that provides active cost control. Unlike budgets (which only alert), resource monitors can take action—suspending warehouses when credit limits are reached.

**Account Context:** This step should be executed from the newly created account.

## **Why is this important?**

Resource monitors provide a safety net for cost control:
- **Prevent runaway costs**: Automatically stop spending when limits are hit
- **Multiple thresholds**: Get early warnings before reaching the limit
- **Active intervention**: Can suspend warehouses, not just alert
- **Tiered response**: Different actions at different thresholds

## **Prerequisites**

- Account budget configured (recommended)
- Understanding of acceptable downtime if warehouses are suspended
- Knowledge of critical vs. non-critical workloads

## **Key Concepts**

**Resource Monitor**
A Snowflake object that tracks credit consumption and can take action (notify or suspend) when thresholds are reached.

**Threshold Actions**
- **NOTIFY**: Send a notification, but allow usage to continue
- **SUSPEND**: Stop warehouses after current queries complete
- **SUSPEND_IMMEDIATE**: Stop warehouses immediately, killing running queries

**Reset Frequency**
How often the credit counter resets:
- **MONTHLY**: Most common, aligns with billing cycles
- **WEEKLY**: For tighter control
- **DAILY**: For very strict limits
- **NEVER**: Cumulative across all time

**Account-Level Monitor**
Applied to the entire account, tracking all credit consumption from all warehouses.

**Tiered Thresholds**
Best practice is to configure multiple thresholds:
- 75%: Notify (early warning)
- 90%: Notify (urgent warning)
- 100%: Suspend or notify (limit reached)

**Note:** Snowflake allows only ONE suspend trigger per resource monitor, so the 100% threshold is your enforcement point.

**More Information:**
* [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) — Complete guide
* [CREATE RESOURCE MONITOR](https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor) — SQL reference

### Configuration Questions

#### What name should be used for this account? (`new_account_name`: text)
**What is this asking?**
Confirm or customize the account name. Based on your Platform Foundation naming conventions, a suggested name was generated in the previous step.

**Naming Requirements:**
- Must be unique within your organization
- Can contain letters, numbers, and underscores
- Cannot start with a number
- Maximum 255 characters
- Will be converted to uppercase internally

**Recommended Format:**
Based on your Platform Foundation settings, follow this pattern:
- If prefix is used: `{prefix}_{domain}_{environment}` or `{prefix}_{environment}_{domain}`
- If no prefix: `{domain}_{environment}` or `{environment}_{domain}`

**Examples:**
- `ACME_SALES_PROD`
- `ACME_DEV_FINANCE`
- `ANALYTICS_TEST`

**Best Practice:**
Use the suggested name from the previous step unless you have a specific reason to customize it. Consistent naming makes governance and cost allocation easier.

#### What is the monthly credit limit for the resource monitor? (`account_resource_monitor_limit`: text)
**What is this asking?**
Set the maximum number of credits the account can consume before the configured action (at 100%) is taken.

**Why does this matter?**
This is your hard limit. The resource monitor will automatically set up tiered alerts:
- At 75% of this limit: First notification
- At 90% of this limit: Second notification
- At 100% of this limit: Your selected action (Suspend/Notify)
- At 110%: Same action as 100% (catches overruns)

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

#### How often should the resource monitor reset? (`account_resource_monitor_reset_frequency`: multi-select)
**What is this asking?**
Choose when the credit counter resets to zero.

**Why does this matter?**
The reset frequency should align with your billing and budgeting cycles.

**Options explained:**

**Monthly (Recommended):**
- Resets on the 1st of each month
- Aligns with Snowflake billing cycles

**Weekly:**
- Resets every Monday
- For tighter weekly cost control

**Daily:**
- Resets daily at midnight
- For very tight cost control

**Never:**
- Manual reset only
- For one-time credit allocations

**Recommendation:**
Use Monthly reset aligned with your billing cycle.
**Options:**
- Monthly
- Weekly
- Daily
- Never (manual reset)

#### What action should be taken when the credit limit is reached? (`account_resource_monitor_action`: multi-select)
**What is this asking?**
Choose what happens when the credit limit is reached.

**Why does this matter?**
Different actions balance cost protection against user disruption.

**Options explained:**

**Suspend Immediately:**
- Terminates all running queries immediately
- Suspends all warehouses
- Most aggressive protection
- May cause user disruption

**Suspend After Current Queries (Recommended):**
- Allows running queries to complete
- Blocks new queries from starting
- Suspends warehouses after current work finishes
- Balances protection with user experience

**Notify Only:**
- Sends alert but doesn't suspend
- Requires manual intervention
- Costs can exceed limit

**Recommendation:**
Use "Suspend After Current Queries" for production.
**Options:**
- Suspend Immediately
- Suspend After Current Queries
- Notify Only
