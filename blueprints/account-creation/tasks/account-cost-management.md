# Account Cost Management

## Summary
Configure an account-level budget with spending limits and alerts, set up a
resource monitor for active cost control, and apply domain and environment
tags for cost allocation and FinOps reporting.

## External Requirements
- Security & Identity Configuration complete (Task 2)
- Infrastructure share consumed (access to governance objects)
- Knowledge of expected credit consumption for this account
- List of stakeholders to receive budget alerts

## Personas
- FinOps Team
- Platform Administrator
- Finance Team

## Role Requirements
- ACCOUNTADMIN role access

## Details
## Steps in This Task

| Step | Title | Purpose |
|------|-------|---------|
| 3.1 | Configure Account Budget | Set spending limits and email alerts |
| 3.2 | Configure Account Resource Monitor | Active cost control with suspend/notify actions |
| 3.3 | Apply Cost Allocation Tags | Tag account resources for FinOps reporting |

**From Platform Foundation (inherited):**
- Tag framework (DOMAIN, ENVIRONMENT tags with allowed values)
- FinOps strategy decisions

## Account Execution Context

All steps in this task should be executed from the **newly created account**.

| Steps | Execute From |
|-------|--------------|
| 3.1 - 3.3 | **New Account** (the account you created) |

## Time Estimate

- **Budget configuration:** 5-10 minutes
- **Resource monitor setup:** 5-10 minutes
- **Tag application:** 5-10 minutes
- **Total:** 15-30 minutes

## Key Decisions

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Monthly credit limit | Finance/Platform Team | Budget ceiling for this account |
| Alert thresholds | Platform Team | When stakeholders are notified |
| Resource monitor action | Platform Team | Whether to suspend or just notify at limit |
| Tag values | Business/Platform Team | Cost attribution in reports |

## Relationship to Platform Foundation

The Platform Foundation workflow established:
- **Tag framework**: DOMAIN, ENVIRONMENT, and other tags with allowed values
- **Account-level budget**: For the Organization Account
- **Account-level resource monitor**: For the Organization Account

This task configures the same elements for THIS account:
- Apply tags to this account's resources
- Set budget specific to this account's expected usage
- Configure resource monitor for this account's credit limit

## Deliverables

Upon completing this task, you will have:
- ✅ Account budget configured with monthly limit and email alerts
- ✅ Account resource monitor with threshold-based actions
- ✅ Domain and environment tags applied for cost reporting
- ✅ Account ready for use with full cost visibility

## More Information

* [Budgets Overview](https://docs.snowflake.com/en/user-guide/budgets) — Credit monitoring and alerts
* [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) — Active cost control
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging) — Tag-based governance
* [Attributing Costs with Tags](https://docs.snowflake.com/en/user-guide/cost-attributing) — FinOps reporting