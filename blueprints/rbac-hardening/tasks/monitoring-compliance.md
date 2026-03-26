# Monitoring & Compliance

## Summary
Establish ongoing RBAC monitoring by creating governance views for access
review, configuring Snowflake alerts on suspicious privilege changes, and
generating documentation for periodic compliance reviews.

## External Requirements
- Platform Infrastructure Database and Governance schema exist (from Platform Foundation Setup)
- SNOWFLAKE database IMPORTED PRIVILEGES granted
- Notification integration configured (for alerts)
- Warehouse available for alert execution

## Personas
- Security Administrator
- Compliance Team
- Platform Administrator

## Role Requirements
- SYSADMIN
- ACCOUNTADMIN

## Details
## **What You Will Accomplish**

By completing this task, you will have continuous RBAC monitoring in place —
governance views for on-demand review, automated alerts on privilege changes,
and compliance documentation for periodic access reviews.

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 4.1 | Create RBAC Monitoring Views | Governance views for role grants, user-role matrix, privilege summary | No |
| 4.2 | Configure Privilege Change Alerts | Alerts on suspicious GRANT/REVOKE activity | Conditional on `rbac_enable_alerts` |
| 4.3 | Generate Access Review Report | Compliance review documentation template | No |

## **Key Decisions**

| Decision | Impact |
|----------|--------|
| Alert notification integration | Where alerts are sent (email, Slack, etc.) |
| Review frequency (Weekly/Monthly/Quarterly) | How often compliance reports are generated |
| Monitoring warehouse | Cost of running scheduled alert checks |

## **Deliverables**

- ✅ RBAC monitoring views in governance schema
- ✅ Privilege change alert configuration
- ✅ Access review report SQL and documentation

## **More Information**

* [Snowflake Alerts](https://docs.snowflake.com/en/user-guide/alerts) — Automated monitoring
* [ACCESS_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/access_history) — Who accessed what
* [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles) — Role grant history