# Data Product Cost Management

## Summary
Establish cost controls for your data product through Snowflake resource monitors
that track credit consumption and can trigger alerts or suspend warehouses when
thresholds are reached.

## External Requirements
- Warehouses created (Task 3)
- Understanding of expected credit consumption

## Personas
- FinOps Team
- Platform Administrator

## Role Requirements
- ACCOUNTADMIN role access (required for resource monitors)

## Details
## **Understanding Snowflake Credits**

Snowflake uses **consumption-based pricing**. You pay for:

| Resource | How It's Measured | Typical Cost |
|----------|-------------------|--------------|
| **Compute** | Credits per hour of warehouse runtime | Varies by contract |
| **Storage** | $ per TB per month | ~$20-40/TB/month |

**Credits** are the billing unit for compute. Credit consumption depends on warehouse size:

| Warehouse Size | Credits per Hour |
|----------------|------------------|
| X-Small | 1 |
| Small | 2 |
| Medium | 4 |
| Large | 8 |
| X-Large | 16 |

## **Why Cost Management?**

Data products can consume significant compute resources, especially during:
- Initial data loads and transformations
- Ad-hoc analytics queries
- Runaway queries or inefficient code
- Unexpected usage spikes

Resource monitors provide:
- **Visibility**: Track credit consumption per warehouse
- **Alerts**: Notify stakeholders before budgets are exceeded
- **Controls**: Automatically suspend warehouses at defined thresholds
- **Accountability**: Enable chargeback and cost allocation

## **Steps in This Task**

| Step | Title | Purpose |
|------|-------|---------|
| 5.1 | Create Resource Monitors | Define monitors with credit quotas |
| 5.2 | Assign Monitors to Warehouses | Attach monitors to data product warehouses |
| 5.3 | Configure Alert Notifications | Set up notification integrations for alerts |

## **Key Concepts**

**Resource Monitor Components**

| Component | Description |
|-----------|-------------|
| Credit Quota | Credit allowance for the period |
| Frequency | Reset interval (MONTHLY, WEEKLY, DAILY, NEVER) |
| Start Timestamp | When monitoring begins |
| Triggers | Actions at percentage thresholds |

**Trigger Actions**

| Action | Behavior | When to Use |
|--------|----------|-------------|
| NOTIFY | Send alert only | Early warning (50%, 75%) |
| SUSPEND | Stop warehouse, finish running queries | Soft limit (90%) |
| SUSPEND_IMMEDIATE | Stop warehouse, cancel all queries | Hard limit (100%) |

## **Estimating Credit Needs**

| Warehouse Size | Light Usage | Moderate Usage | Heavy Usage |
|----------------|-------------|----------------|-------------|
| X-Small | 10-30 credits/month | 30-100 | 100-300 |
| Small | 20-60 | 60-200 | 200-600 |
| Medium | 40-120 | 120-400 | 400-1200 |

Start conservative and adjust based on actual usage.

## **What You'll Create**

| Object Type | Naming Pattern | Owner | Purpose |
|-------------|----------------|-------|---------|
| Resource Monitors | `<prefix>_MONITOR` | `ACCOUNTADMIN` | Credit tracking |
| Notification Integration | `<prefix>_ALERTS` | `ACCOUNTADMIN` | Alert delivery |

**Note:** Resource monitors require ACCOUNTADMIN privileges.

## **More Information**

* [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors)
* [CREATE RESOURCE MONITOR](https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor)
* [Notification Integrations](https://docs.snowflake.com/en/user-guide/notification-integrations)