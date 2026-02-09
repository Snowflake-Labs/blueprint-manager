In this step, you'll configure the account-level budget with spending limits and notification preferences. The Budget object monitors all credit consumption for your account, using time-series forecasting to send daily, proactive alerts when your spending is projected to exceed the limit.

**Account Context:** This step should be executed in your Organization Account (if created) or your primary account.

## Why is this important?

Configuring your budget correctly ensures you receive meaningful alerts:
- **Realistic limits** prevent alert fatigue from too-low thresholds
- **Appropriate notifications** ensure the right people are alerted
- **Proper refresh intervals** balance monitoring frequency with cost

## External Prerequisites

- Monthly credit limit approved by your finance team
- Email addresses or distribution lists for alert recipients

## Key Concepts

**Credit Limit**
The maximum number of credits allocated to the budget for the period. Set in credits, not dollars.

**Credit to Dollar Conversion**
To convert from a dollar amount, use your negotiated credit rate. For example, if your rate is $3/credit and your limit is $3,600, your credit limit is 1,200 credits.

**Notification Threshold**
The percentage of the limit (e.g., 75%) that triggers an alert when projected spending exceeds it.

**Email Notifications**
This step configures email-based notifications, which is the simplest approach. Distribution lists are recommended for team visibility.

**Alternative Notification Methods**
Snowflake also supports webhooks (Slack/Teams) and cloud service queues (SNS/Event Grid). These require additional configuration via notification integrations. See the "Upgrading to Webhook Notifications" section in the generated documentation.

**Budget Refresh Interval**
How often the budget checks consumption data for forecasting. Default is 6.5 hours; optional 1-hour refresh increases compute cost by ~12x.

**Reset Frequency**
Budgets automatically reset on the first of every month at 12:00 AM UTC.

**Alert vs Hard Limit**
Budgets are for alerting only - they do NOT suspend services. Use Resource Monitors for hard limits.

**Best Practice: Set Realistic Limits**
Set an achievable budget limit to ensure alerts are meaningful. A limit set too high won't provide timely warnings; too low creates alert fatigue.

**Best Practice: Multiple Alert Levels**
For multiple thresholds (e.g., 50%, 75%, 90%), use Resource Monitors (Configure Resource Monitors step) which support multiple trigger points with different actions.

## More Information

* [Monitor credit usage with budgets](https://docs.snowflake.com/en/user-guide/budgets) — Overview of Snowflake's native budget feature
* [Notifications for budgets](https://docs.snowflake.com/en/user-guide/budgets/notifications) — Configuring alerts and notification methods
* [SET_SPENDING_LIMIT Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_spending_limit) — Setting credit limits on budgets
* [SET_NOTIFICATION_THRESHOLD Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_notification_threshold) — Configuring alert thresholds
* [SET_REFRESH_TIER Class Method](https://docs.snowflake.com/en/sql-reference/classes/budget/methods/set_refresh_tier) — Setting forecast update frequency

### Configuration Questions

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

#### At what percentage of your budget should alerts be triggered? (`budget_notification_threshold`: multi-select)
**What is this asking?**
Select the percentage of your budget limit at which Snowflake will send notifications when *projected* spending exceeds this threshold.

**Why does this matter?**
The threshold determines how early you receive warnings. Lower thresholds give more lead time but may create noise; higher thresholds give less warning.

**How it works:**
- Snowflake uses time-series forecasting to predict end-of-month spending
- When projected spending exceeds (budget × threshold%), an alert is sent
- Example: 5,000 credit budget with 75% threshold → alert when projected spending > 3,750 credits

**Options explained:**

| Threshold | Use Case |
|-----------|----------|
| **50%** | Early warning for large budgets - maximum lead time |
| **75%** | Balanced early warning (recommended) |
| **90%** | Warning close to limit - less noise |
| **100%** | Alert only when projected to hit exactly 100% |
| **110%** | Alert after projected overage (Snowflake default) |

**For multiple thresholds:** Snowflake's native budget supports one threshold. For multiple alert levels, use Resource Monitors (Configure Resource Monitors step) or custom budget actions.

**Recommendation:** Select `75` for balanced early warning that gives you time to take action.
**Options:**
- 50
- 75
- 90
- 100
- 110

#### How frequently should the budget check for updated spending? (`budget_refresh_interval`: multi-select)
**What is this asking?**
Choose how often the budget updates its spending data and performs forecasting.

**Why does this matter?**
More frequent refreshes provide faster alerts but cost more compute.

**Options explained:**

**6.5 hours (Default):**
- Standard refresh interval
- Balances cost and monitoring frequency
- Suitable for most organizations

**1 hour (Frequent):**
- More frequent spending updates
- Better for tight budget control
- Increases compute cost by ~12x

**Recommendation:**
Start with 6.5 hours (default). Switch to 1 hour only during critical cost monitoring periods.
**Options:**
- 6.5 hours (default)
- 1 hour (frequent monitoring)

#### What email address(es) should receive budget alerts? (`budget_alert_emails`: list)
**What is this asking?**
Provide the email addresses that should receive budget alert notifications.

**Why does this matter?**
Budget alerts need to reach people who can investigate and take action on spending issues.

**Best practices:**
- Use distribution lists for team visibility (e.g., `finops-team@company.com`)
- Include both technical and financial stakeholders
- Ensure 24/7 monitoring for critical budgets

**Examples:**
- `finops-team@company.com`
- `data-platform-leads@company.com`

**Alternative notification methods:**
This step configures email notifications, which is the simplest approach. If you need webhook notifications (Slack/Teams) or cloud service queues (SNS/Event Grid), see the "Upgrading to Webhook Notifications" section in the generated documentation.

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
