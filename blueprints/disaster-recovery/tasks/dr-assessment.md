# DR Assessment

## Summary
Audit current replication infrastructure, client redirect, replication health, and identify coverage gaps.

## External Requirements
- Snowflake account exists in an organization with at least one other account

## Personas
- Platform Administrator
- Security Team

## Role Requirements
- ACCOUNTADMIN

## Details
## **Deliverables**

By completing this task, you will have:
✅ Verified Snowflake edition and organization membership supports DR features
✅ Inventoried existing replication and failover groups
✅ Assessed client redirect configuration and identified gaps
✅ Measured replication lag and effective RPO
✅ Identified all databases and objects not covered by replication

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 1.1 | Check Account Edition and Info | Verify DR feature availability | — |
| 1.2 | Audit Replication and Failover Groups | Discover existing DR infrastructure | — |
| 1.3 | Audit Client Redirect Connections | Check transparent failover setup | — |
| 1.4 | Check Replication Health and Lag | Measure current RPO | — |
| 1.5 | Identify Coverage Gaps | Find unprotected databases and non-replicated objects | — |

## **More Information**

* [Replication and Failover Overview](https://docs.snowflake.com/en/user-guide/account-replication-intro) — Snowflake DR documentation
* [Client Redirect](https://docs.snowflake.com/en/user-guide/client-redirect) — Transparent connection failover