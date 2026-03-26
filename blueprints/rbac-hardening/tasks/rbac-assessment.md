# RBAC Assessment

## Summary
Discover the current state of role-based access controls in your Snowflake
account by auditing the role hierarchy, privilege grants, and stale access
patterns. All queries are read-only diagnostics.

## External Requirements
- Account accessible with SECURITYADMIN or ACCOUNTADMIN role
- SNOWFLAKE database IMPORTED PRIVILEGES granted (for Account Usage views)
- Data Product Setup completed (if auditing data product roles)

## Personas
- Security Administrator
- Compliance Team
- Platform Administrator

## Role Requirements
- SECURITYADMIN
- ACCOUNTADMIN

## Details
## **What You Will Accomplish**

By completing this task, you will have a comprehensive picture of your
account's RBAC health — role hierarchy structure, privilege grant risks,
and stale access patterns — enabling informed decisions in subsequent
hardening tasks.

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 1.1 | Audit Role Hierarchy | Visualize the complete role tree, find orphaned roles, detect excessive depth | No |
| 1.2 | Audit Privilege Grants | Discover direct user grants, PUBLIC exposure, ACCOUNTADMIN overuse | No |
| 1.3 | Audit Stale Access | Find unused roles, dormant users with active privileges | No |

## **Key Decisions**

| Decision | Impact |
|----------|--------|
| Audit scope (full account vs. specific data products) | Determines breadth of audit queries |
| Stale access threshold (days) | Controls sensitivity of dormant user detection |

## **Deliverables**

- ✅ Complete role hierarchy visualization query
- ✅ Privilege risk assessment queries
- ✅ Stale access detection queries
- ✅ Prioritized findings for Task 2 (Privilege Hardening)

## **More Information**

* [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview) — Snowflake RBAC fundamentals
* [Account Usage Views](https://docs.snowflake.com/en/sql-reference/account-usage) — Login history, grants, query history