In this step, you'll configure an account-level budget to monitor credit consumption and receive alerts when spending approaches or exceeds defined thresholds.

**Account Context:** This step should be executed from the newly created account.

## **Why is this important?**

Budgets provide visibility and early warning for cost management:
- **Predictable spending**: Set expected monthly credit consumption
- **Proactive alerts**: Get notified before overspending occurs
- **Stakeholder awareness**: Keep finance and management informed
- **No surprise bills**: Avoid unexpected charges at month end

## **Prerequisites**

- Account created and accessible
- **Wait 5-10 minutes** after account creation before running this step (the Snowflake system database needs time to bootstrap)
- Knowledge of expected monthly credit consumption for this account
- Email addresses of stakeholders to receive alerts

## **Key Concepts**

**Account Budget**
A native Snowflake feature that tracks credit consumption against a defined limit. Budgets use time-series forecasting to predict end-of-month spend and alert proactively.

**Credit Limit**
The monthly spending target for this account. This is a monitoring threshold, not a hard limit—the budget alerts but doesn't stop usage.

**Notification Thresholds**
Percentage points at which alerts are sent. For example, 75% means you're alerted when spending reaches 75% of the monthly limit.

**Email Notifications**
Budget alerts are sent to specified email addresses. Use distribution lists to ensure the right stakeholders receive alerts.

**Budgets vs Resource Monitors**
- **Budgets**: Alert only, use forecasting, good for visibility
- **Resource Monitors**: Can take action (suspend), based on actual usage

**Bootstrap Timing**
Budget creation requires the Snowflake system database to be fully initialized. In newly created accounts, this may take 5-10 minutes. If you receive a "Snowflake Database is still bootstrapping" error, wait a few minutes and retry.

**More Information:**
* [Budgets Overview](https://docs.snowflake.com/en/user-guide/budgets) — Credit monitoring and alerts
* [Budget Notifications](https://docs.snowflake.com/en/user-guide/budgets/notifications) — Alert configuration

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

#### What is the monthly credit limit for this account? (`account_budget_limit`: text)
**What is this asking?**
Set the expected monthly credit consumption for this account.

**Why does this matter?**
A well-set budget provides meaningful alerts without being too restrictive. Setting it too low causes alert fatigue; too high means late warnings. This is your primary visibility into spending patterns for this account.

**How to estimate:**
- Consider the workloads planned for this account
- Review historical usage from similar environments
- Factor in development vs production usage patterns
- Account for growth and seasonality

**Examples by account type:**
| Account Type | Typical Range |
|--------------|---------------|
| Development | 500 - 2,000 credits |
| Test/QA | 1,000 - 5,000 credits |
| Production | 5,000 - 50,000+ credits |

**Format:** Enter a number (e.g., `5000` for 5,000 credits)

**Note:** This is a monitoring threshold. You can adjust it as you learn actual consumption patterns.

**More Information:**
* [Budgets Overview](https://docs.snowflake.com/en/user-guide/budgets) — Credit monitoring and alerts

#### At what percentage should budget alerts be sent? (`account_budget_threshold`: multi-select)
**What is this asking?**
Choose when to receive the first budget alert (as a percentage of the monthly limit).

**Why does this matter?**
The threshold determines how early you receive warnings. Lower thresholds give more lead time to take action; higher thresholds give less warning but reduce noise.

**Options explained:**
- **50%**: Early warning, good for tight budget control
- **75%**: Balanced approach, recommended for most accounts
- **90%**: Late warning, for accounts with predictable spend
- **100%**: Alert only when limit is reached

**How forecasting works:**
Snowflake predicts end-of-month spend based on current trajectory. If your 75% threshold would be exceeded by month end, you're alerted early.

**Example:**
With a 5,000 credit limit and 75% threshold:
- Alert when projected spend exceeds 3,750 credits
- If halfway through the month Snowflake forecasts 4,000 credits, you're alerted immediately

**Recommendation:** Use 75% for most accounts to balance early warning with alert fatigue.
**Options:**
- 50
- 75
- 90
- 100

#### Who should receive budget alerts? (`account_budget_emails`: list)
**What is this asking?**
Provide email addresses that should receive budget alert notifications.

**Why does this matter?**
Budget alerts are only useful if the right people see them. The recipients should have the authority and ability to take action when spending exceeds expectations.

**Recommendations:**
- Include platform/cloud team for technical response
- Include finance for budget oversight
- Use distribution lists for team coverage
- Keep the list focused to avoid alert fatigue

**Examples:**
- `cloud-platform@company.com`
- `finance-alerts@company.com`
- `jane.doe@company.com`

**Format:** Enter each email address on a separate line.
