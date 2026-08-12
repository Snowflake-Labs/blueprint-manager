# DR Implementation

## Summary
Create failover groups with replication schedules and configure client redirect for transparent failover.

## External Requirements
- DR Assessment completed (Task 1)
- Target account exists in same organization, different region
- Business Critical Edition on both accounts

## Personas
- Platform Administrator

## Role Requirements
- ACCOUNTADMIN

## Details
## **Deliverables**

By completing this task, you will have:
✅ A failover group on the source account with selected object types and databases
✅ A secondary failover group on the target account actively replicating
✅ Replication schedule set and initial sync triggered
✅ Client redirect configured (if enabled) with connection URL ready for applications

## **Key Decisions**

| Decision | Impact | Guidance |
|----------|--------|----------|
| Object types to replicate | Non-trivial to change post-setup; adding types later triggers re-sync | Include `Network Policies` at minimum; add `Users`, `Roles`, `Warehouses` for full DR coverage |
| Database scope | Determines DR coverage and initial replication cost | Include all production databases; exclude dev/test to reduce cost |
| Replication frequency | Directly sets your RPO; lower frequency = lower cost but higher data loss risk | Match or exceed your `dr_rpo_target` answer |
| Client redirect | Affects application architecture; all app connection strings must change | Recommended for production; significantly reduces RTO |

## **Account Execution Context**

This task requires switching between your source and target Snowflake accounts.
Connect to the correct account before running each step's SQL.

| Step | Title | Account |
|------|-------|---------|
| 2.1 | Define DR Requirements | Source account |
| 2.2 | Create Failover Group on Source | Source account |
| 2.3 | Create Secondary Failover Group on Target | **Target account** |
| 2.4 | Set Up Client Redirect | Source account (Part 1); **Target account** (Part 2) |

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 2.1 | Define DR Requirements | Specify target, databases, RPO, object types | — |
| 2.2 | Create Failover Group on Source | Create primary failover group with replication schedule | — |
| 2.3 | Create Secondary Failover Group on Target | Create replica group and start initial sync | — |
| 2.4 | Set Up Client Redirect | Create connection objects for transparent failover | When client redirect enabled |

## **More Information**

* [CREATE FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/create-failover-group) — SQL reference
* [Client Redirect](https://docs.snowflake.com/en/user-guide/client-redirect) — Connection URL setup