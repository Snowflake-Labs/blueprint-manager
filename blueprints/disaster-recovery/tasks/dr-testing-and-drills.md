# DR Testing and Drills

## Summary
Execute a planned failover/failback drill to validate DR readiness and measure actual RTO/RPO.

## External Requirements
- DR Implementation completed (Task 2)
- Failover group(s) actively replicating
- Coordination with stakeholders (failover temporarily redirects workloads)

## Personas
- Platform Administrator
- Data Engineer

## Role Requirements
- ACCOUNTADMIN

## Details
## **Deliverables**

By completing this task, you will have:
✅ Confirmed replication is healthy before testing
✅ Executed a planned failover (promoted secondary to primary)
✅ Validated data and functionality on the new primary
✅ Executed failback to restore the original primary
✅ Measured and recorded actual RTO and RPO achieved

## **Account Execution Context**

This task requires switching between your source and target Snowflake accounts.
Connect to the correct account before running each step's SQL.

| Step | Title | Account |
|------|-------|---------|
| 3.1 | Pre-Drill Validation | Source account |
| 3.2 | Execute Failover | **Target account** |
| 3.3 | Validate on New Primary | **Target account** (now primary) |
| 3.4 | Execute Failback | Original source account (now secondary) |

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 3.1 | Pre-Drill Validation | Verify replication health before failover | — |
| 3.2 | Execute Failover | Promote secondary to primary | — |
| 3.3 | Validate on New Primary | Confirm data accessibility and writes | — |
| 3.4 | Execute Failback | Restore original primary and resume replication | — |

## **More Information**

* [Failover Groups](https://docs.snowflake.com/en/user-guide/account-replication-failover-groups) — Managing failover
* [ALTER FAILOVER GROUP ... PRIMARY](https://docs.snowflake.com/en/sql-reference/sql/alter-failover-group) — Failover promotion