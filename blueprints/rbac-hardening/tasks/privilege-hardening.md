# Privilege Hardening

## Summary
Tighten access controls based on RBAC Assessment findings by revoking
unnecessary PUBLIC grants, restricting ACCOUNTADMIN to break-glass users,
eliminating direct user-level privileges, and enforcing managed access schemas.

## External Requirements
- Task 1 (RBAC Assessment) completed and findings reviewed
- Agreement on which PUBLIC grants to revoke (exceptions documented)
- Agreement on authorized ACCOUNTADMIN users (break-glass list)
- Understanding of which users have direct privileges that need migration

## Personas
- Security Administrator
- Platform Administrator

## Role Requirements
- SECURITYADMIN
- ACCOUNTADMIN

## Details
## **What You Will Accomplish**

By completing this task, you will have hardened your account's privilege
posture — PUBLIC role locked down, ACCOUNTADMIN restricted to break-glass
users, direct user grants migrated to roles, and schemas converted to
managed access for centralized control.

## **Important**

> Each step generates SQL that should be reviewed carefully before execution,
> as these are destructive operations (REVOKE statements).

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 2.1 | Restrict PUBLIC Role Grants | Revoke unnecessary grants from PUBLIC role | Conditional on `rbac_restrict_public` |
| 2.2 | Enforce Admin Separation of Duties | Restrict ACCOUNTADMIN to break-glass users only | No |
| 2.3 | Revoke Direct User Privileges | Move direct user-level grants into roles | No |
| 2.4 | Enforce Managed Access Schemas | Convert schemas to WITH MANAGED ACCESS | Conditional on `rbac_enforce_managed_access` |

## **Key Decisions**

| Decision | Impact |
|----------|--------|
| PUBLIC grant exceptions | Which objects remain accessible to all users |
| ACCOUNTADMIN authorized list | Who can use the most powerful role |
| Managed access scope | Which schemas get centralized grant control |

## **Deliverables**

- ✅ PUBLIC role revocation SQL (with exceptions)
- ✅ ACCOUNTADMIN restriction SQL
- ✅ Direct privilege migration SQL
- ✅ Managed access conversion SQL

## **More Information**

* [PUBLIC Role](https://docs.snowflake.com/en/user-guide/security-access-control-overview#public-role) — Understanding the PUBLIC role
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas) — Centralized grant control
* [Separation of Duties](https://docs.snowflake.com/en/user-guide/security-access-control-overview#label-access-control-overview-roles-system) — System role best practices