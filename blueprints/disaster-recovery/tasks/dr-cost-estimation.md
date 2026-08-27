# DR Cost Estimation

## Summary
Calculate initial replication, ongoing data transfer, target storage, and operational costs for your DR topology.

## External Requirements
- Access to SNOWFLAKE.ACCOUNT_USAGE views
- Knowledge of target DR region and topology

## Personas
- Platform Administrator
- Data Engineer

## Role Requirements
- ACCOUNTADMIN

## Details
## **Deliverables**

By completing this task, you will have:
✅ DR topology and pricing parameters specified
✅ Current storage footprint measured and databases categorized
✅ Initial (one-time) replication cost estimated
✅ Monthly incremental replication, storage, and operational costs estimated
✅ Year 1 and Year 2+ annual cost projections generated

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 5.1 | Gather Cost Parameters | Specify topology, rates, and assumptions | — |
| 5.2 | Measure Storage Footprint | Query actual storage per database | — |
| 5.3 | Estimate Replication and Operational Costs | Calculate initial, monthly, and annual projections | — |

## **More Information**

* [Replication Cost](https://docs.snowflake.com/en/user-guide/account-replication-cost) — Cost model documentation
* [Service Consumption Table](https://www.snowflake.com/legal/snowflake-service-consumption-table/) — Current pricing