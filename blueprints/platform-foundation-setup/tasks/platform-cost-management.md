# Platform Cost Management

## Summary
Set up Snowflake's native budget feature for automated spending alerts,
configure account-level resource monitors with hard limits, extend the tagging
framework with cost center and ownership tracking, and create cost reporting views.

## External Requirements
- Task 1 (Platform Foundation) completed
- Task 2 (Security & Identity Configuration) completed
- Estimated monthly credit budget from finance team
- List of cost centers for chargeback (if applicable)

## Personas
- FinOps Team
- Finance Team
- Platform Administrator

## Role Requirements
- ACCOUNTADMIN role access

## Details
This task builds on the infrastructure created in Task 1 (Account Strategy & Nomenclature) and should be executed after Task 2 (Security & Identity Configuration).

**Account Context:** All steps in this task should be executed in your Organization Account (if created in the Create Organization Account step) or your primary account.

## Steps in This Task

| Step | Title | Purpose |
|------|-------|---------|
| 3.1 | Enable Spending Budgets | Decide whether to use Snowflake's native budget feature |
| 3.2 | Configure Spending Budgets | Set monthly limits and notification preferences |
| 3.3 | Enable Resource Monitors | Decide whether to implement account-level resource monitors |
| 3.4 | Configure Resource Monitors | Set credit limits and suspension actions |
| 3.5 | Enable Cost Allocation Tags | Decide whether to add cost-focused tags |
| 3.6 | Configure Cost Allocation Tags | Create additional tags and cost reporting views |

**Note on conditional steps:**
- Configure Spending Budgets is shown only if you enable budgets in Enable Spending Budgets
- Configure Resource Monitors is shown only if you enable resource monitors in Enable Resource Monitors
- Configure Cost Allocation Tags is shown only if you enable additional cost tags in Enable Cost Allocation Tags

## Time Estimate

- **Quick Path** (budgets only): 15-20 minutes
- **Standard Path** (budgets + resource monitors): 25-35 minutes
- **Full Path** (all features): 35-45 minutes

## Key Decisions

### 1. Spending Budgets
**Decision:** Whether to enable Snowflake's native budget feature
**Stakeholders:** FinOps team, Finance, Platform team
**Recommendation:** Enable budgets for all environments. They provide valuable early warning of spending trends with no risk of disruption.

### 2. Resource Monitors
**Decision:** Whether to implement hard credit limits that suspend warehouses
**Stakeholders:** Platform team, Finance, Business stakeholders
**Recommendation:** Enable for production environments to prevent unexpected cost overruns. Consider the impact on users if warehouses are suspended.

### 3. Cost Allocation Tags
**Decision:** Which additional tags to implement beyond the core tags from Task 1
**Stakeholders:** FinOps team, Finance, Department leads
**Recommendation:** At minimum, add `cost_center` and `owner` tags for chargeback and accountability.

## Budgets vs Resource Monitors

Understanding the difference is critical:

| Feature | Budgets | Resource Monitors |
|---------|---------|-------------------|
| **Purpose** | Alerting & awareness | Active cost control |
| **Action** | Send notifications | Can suspend warehouses |
| **Limit Type** | Soft (can exceed) | Hard (enforced) |
| **Forecasting** | Time-series prediction | Simple threshold |
| **User Impact** | None | May interrupt work |
| **Best For** | Planning & monitoring | Cost protection |

**Recommendation:** Use both! Budgets for early warning, resource monitors as a safety net.

## Cost Allocation Strategy

This task extends the tagging framework established in Task 1:

**Core Tags (from Task 1):**
- `domain` - Business unit (e.g., Finance, Marketing)
- `environment` - SDLC stage (e.g., Dev, Prod)
- `dataproduct` - Data product identifier
- `workload` - Workload type (Ingest, Transform, BI, etc.)
- `zone` - Data zone (Raw, Curated, Consumption, etc.)

**Additional Tags (this task):**
- `cost_center` - Accounting cost center code
- `owner` - Team or individual responsible
- `project` - Specific project or initiative
- `application` - Application or system name

## Deliverables

Upon completing this task, you will have:

1. **If budgets enabled:**
   - Account-level spending budget configured
   - Notification recipients set up
   - Budget refresh interval configured

2. **If resource monitors enabled:**
   - Account-level resource monitor protecting all warehouses
   - Credit limit with notification thresholds
   - Suspension action configured

3. **If cost tags enabled:**
   - Additional tags in governance schema
   - Cost reporting views created
   - Infrastructure database tagged

4. **Documentation:**
   - Configuration summary in dynamic content
   - SQL code for all configurations
   - Cost reporting queries

## What's Next

After completing Cost Management, you've finished the **Platform Foundation Setup** workflow. Your Snowflake environment now has:

- ✅ Account strategy and nomenclature defined
- ✅ Security and identity configured
- ✅ Cost management in place

**Next Workflow:** Proceed to **Data Product Configuration** to set up individual data products with:
- Databases and schemas
- Warehouses sized for workloads
- Warehouse-level resource monitors
- Functional and access roles
- Tag application to resources

## More Information

* [Monitor credit usage with budgets](https://docs.snowflake.com/en/user-guide/budgets)
* [Working with Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
* [Attributing Costs using Tags](https://docs.snowflake.com/en/user-guide/cost-attributing)
* [Cost Management Best Practices](https://docs.snowflake.com/en/user-guide/cost-understanding)