In this step, you'll decide whether to activate Snowflake's native **Budget** functionality. A Snowflake Budget allows you to set a defined spending limit (in credits) for a specific time period (e.g., monthly) and automatically monitors consumption. It uses time-series forecasting to predict spending overruns, generating alerts when thresholds are approached or exceeded.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

Spending budgets provide proactive cost awareness by sending alerts when spending is projected to exceed your defined limits. This helps:
- **Prevent unexpected costs** with early warning alerts
- **Enable better financial planning** with time-series forecasting
- **Coordinate with finance teams** through automated notifications
- **Establish cost governance** as a foundation for FinOps practices

## External Prerequisites

- Estimated monthly credit budget from your finance team
- Email addresses or notification endpoints for budget alerts

## Key Concepts

**Budget**
A Snowflake object that monitors credit consumption against a specified spending limit for a specified time period.

**Budget Scope**
Budgets are typically applied at the account level, controlling all compute and cloud services costs. Custom budgets can monitor specific objects or tag-based groups.

**Credit**
The unit of consumption for all paid usage on Snowflake (Compute, Cloud Services, and Storage).

**Time-Series Forecasting**
Snowflake continuously analyzes your spending patterns to predict end-of-period consumption. Alerts are triggered when projected spending exceeds your notification threshold.

**How Forecasting and Thresholds Work Together**
- **Budget Limit**: The total credits allocated for the period (e.g., 5,000 credits/month)
- **Notification Threshold**: The percentage of the limit that triggers alerts (default: 110%)
- **Alert Trigger**: When projected spending exceeds (limit × threshold)

*Example*: You set a monthly budget of 5,000 credits with a 90% notification threshold (4,500 credits). Halfway through the month, Snowflake forecasts that based on current usage, you'll consume 5,000 credits by month's end. Since 5,000 exceeds the 4,500 threshold, an alert is sent immediately—giving you two weeks to adjust.

**Notification Options**
Budget alerts are configured via email in the next step. This is the simplest approach and works for most organizations. If you later want webhook notifications (Slack/Teams) or cloud service queues (SNS/Event Grid), see the upgrade instructions in the Configure Spending Budgets documentation.

**Spend in Currency**
Viewing spending in currency (vs credits) requires `ORGADMIN` or `GLOBALORGADMIN` role access to the `ORGANIZATION_USAGE` schema.

**Budgets vs Resource Monitors**
- **Budgets**: Alerting and awareness - sends notifications but doesn't stop services
- **Resource Monitors**: Active cost control - can automatically suspend warehouses

**Best Practice: Use Native Budgets**
Snowflake's native budget feature is the most efficient way to monitor credit consumption, requiring no external tools or infrastructure setup.

## More Information

* [Monitor credit usage with budgets](https://docs.snowflake.com/en/user-guide/budgets) — Overview of Snowflake's native budget feature
* [Notifications for budgets](https://docs.snowflake.com/en/user-guide/budgets/notifications) — Configuring alerts and notification methods
* [SET_SPENDING_LIMIT Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_spending_limit) — Setting credit limits on budgets
* [SET_NOTIFICATION_THRESHOLD Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_notification_threshold) — Configuring alert thresholds
* [SET_REFRESH_TIER Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_refresh_tier) — Setting forecast update frequency

### Configuration Questions

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
