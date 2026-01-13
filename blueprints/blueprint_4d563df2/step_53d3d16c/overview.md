In this step, you'll decide whether to configure resource monitors for active cost control. Unlike Budgets, which are primarily informational and predictive, Resource Monitors can take immediate action—such as automatically suspending warehouses—when defined credit limits are reached.

This step focuses on establishing an **account-level resource monitor**, which acts as a global safety net to prevent runaway costs across your entire Snowflake environment.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

Resource monitors are your "emergency brake" for cost control:
- **Prevent runaway costs** from misconfigured warehouses or inefficient queries
- **Real-time protection** with immediate action when limits are reached
- **Account-wide safety net** covering all warehouses
- **Peace of mind** knowing total costs are protected

## External Prerequisites

- Maximum credit limit approved by your finance team
- Understanding of the impact of warehouse suspension on users

## Key Concepts

**Resource Monitor**
A Snowflake object that tracks credit consumption and can take action when thresholds are reached. Think of it as a "circuit breaker" for your spending.

**Account-Level Monitor**
Monitors all credit consumption across all warehouses in the account. When triggered, **all warehouses** will be suspended—this may interrupt active queries and prevent new logins until the monitor resets or the limit is adjusted.

**Warehouse-Level Monitor**
Monitors only specific warehouses (configured later in Data Product workflow). Only affects the assigned warehouses when triggered.

**Monitor Scope**
This account-level monitor covers all warehouses, including any default `COMPUTE_WH`. Warehouse-specific monitors for individual data products will be configured in the Data Product workflow.

**Reset Intervals**
Monitors typically reset monthly, aligning with billing cycles. Options include Monthly, Weekly, Daily, or Never (manual reset).

**Trigger Actions**
Resource monitors support three types of actions when thresholds are reached:
- `NOTIFY`: Send email notifications to ACCOUNTADMIN users (no impact on queries)
- `SUSPEND`: Allows running queries to complete, blocks new queries, then suspends warehouses
- `SUSPEND_IMMEDIATE`: Terminates all running queries immediately and suspends warehouses

**Multiple Thresholds**
Unlike budgets (which support a single threshold), resource monitors support **multiple thresholds at different percentages**, each with its own action. For example:
- At 75%: `NOTIFY` (early warning)
- At 90%: `NOTIFY` (final warning)
- At 100%: `SUSPEND` (stop spending)

This allows a tiered response—early warnings give you time to investigate while hard stops prevent overspending.

**Budgets vs Resource Monitors: Complementary Tools**
These tools work best **together**, not as alternatives:
- **Budgets**: Predictive alerting using time-series forecasting. Alerts you when you're *projected* to exceed limits. Cannot take action—only sends notifications.
- **Resource Monitors**: Real-time enforcement based on actual consumption. Takes action when you *actually* hit limits. Can suspend warehouses.

| Feature | Budgets | Resource Monitors |
|---------|---------|-------------------|
| **Alerting** | Predictive (forecasting) | Actual (real-time) |
| **Action** | Notify only | Notify, Suspend, or Suspend Immediate |
| **Thresholds** | Single | Multiple (tiered) |
| **Best For** | Early warning | Hard limits |

**Best Practice: Use Both**
- **Budgets** at 75% threshold → Early warning based on forecast
- **Resource Monitor** at 75% (NOTIFY), 90% (NOTIFY), 100% (SUSPEND) → Tiered real-time protection

## More Information

* [Working with Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) — Overview of resource monitor capabilities
* [CREATE RESOURCE MONITOR](https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor) — SQL command reference

### Configuration Questions

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
