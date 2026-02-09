In this step, you'll configure the **Account-Level Resource Monitor**. This acts as your global safety net by automatically suspending all warehouses if the account's total credit limit is reached.

**Important:** You are not limited to just one monitor. While this step establishes the "Global Brake," you will later create warehouse-specific monitors in the Data Product workflow.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## **Why is this important?**

The account-level resource monitor provides:

* **Global protection** for all warehouses in the account  
* **Tiered alerts** at 75%, 90%, and 100% of the limit  
* **Configurable actions** from notification to immediate suspension  
* **Automatic reset** aligned with billing cycles

## **External Prerequisites**

* Maximum credit limit approved by your finance team  
* Decision on suspension behavior (immediate vs. after current queries)  
* Understanding of reset frequency alignment with billing

## **Key Concepts**

**Credit Quota** The maximum number of credits allowed before action is taken.

**Tiered Thresholds** This configuration uses a **tiered threshold approach** with multiple warning points:

* **75%**: First notification (early warning)  
* **90%**: Second notification (final warning)  
* **100%**: Your configured action (Suspend or Notify)

**Note:** Snowflake allows only ONE suspend trigger per resource monitor, so the 100% threshold is your single enforcement point. This tiered approach gives you multiple opportunities to investigate and respond before hitting the hard limit.

**Global vs Local Monitors** An account-level monitor is "omnipresent"—if it triggers a Suspend action, it shuts down every warehouse in the account. Warehouse-specific monitors (configured later) only affect the assigned warehouses.

**Quota Alignment** If you plan warehouse-specific monitors (e.g., three departments with 500-credit budgets each), your account-level monitor should be at least 1,500+ credits to accommodate the sum of all local monitors.

**Notification Recipients** Account-level alerts go to all users with the ACCOUNTADMIN role. Ensure these users are monitoring their email for budget alerts.

**Trigger Actions**

* NOTIFY: Sends email to ACCOUNTADMIN users (no impact on queries)  
* SUSPEND: Blocks new queries, lets running queries finish, then suspends warehouses  
* SUSPEND\_IMMEDIATE: Terminates all queries immediately and suspends warehouses

**Reset Frequency** How often the credit counter resets (Monthly, Weekly, Daily, or Never). Align with billing cycles for easier reconciliation.

**Working with Budgets** Resource monitors complement budgets: Budgets provide predictive alerts based on forecasting, while resource monitors provide real-time enforcement. Use both together for comprehensive cost management.

## **More Information**

* [Working with Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) — Overview of resource monitor capabilities  
* [CREATE RESOURCE MONITOR](https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor) — SQL command reference

### Configuration Questions

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
