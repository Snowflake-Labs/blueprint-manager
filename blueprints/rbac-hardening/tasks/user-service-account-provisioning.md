# User & Service Account Provisioning

## Summary
Bridge the gap between role creation and actual usage by assigning end users
to data product functional roles and provisioning dedicated service account
users with least-privilege roles, key-pair authentication, and warehouse
restrictions.

## External Requirements
- Data Product Setup completed (functional roles exist)
- User roster with required access levels documented
- Service account requirements documented (name, purpose, access level)
- SCIM prefix configured (if using SCIM for role assignment)

## Personas
- Security Administrator
- Identity Team
- Data Product Owner

## Role Requirements
- USERADMIN
- SECURITYADMIN

## Details
## **What You Will Accomplish**

By completing this task, you will have connected real users and service
accounts to the role hierarchy created by Data Product Setup. Users will
be assigned to READ, WRITE, CREATE, or ADMIN roles based on their job
function, and service accounts will be provisioned with key-pair auth
and minimal privileges.

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 3.1 | Assign Functional Roles to Users | Grant data product roles to end users | No |
| 3.2 | Provision Service Accounts | Create service account users with minimal privileges | No |

## **Key Decisions**

| Decision | Impact |
|----------|--------|
| Access level per user (READ/WRITE/CREATE/ADMIN) | Determines what each user can do |
| Service account auth method (key-pair vs password) | Security posture for automation |
| Warehouse assignments per service account | Cost control for automated workloads |

## **Deliverables**

- ✅ User-to-role assignment SQL
- ✅ Service account creation SQL with key-pair auth
- ✅ Warehouse access grants for service accounts

## **More Information**

* [GRANT ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-role) — Assigning roles to users
* [Key Pair Authentication](https://docs.snowflake.com/en/user-guide/key-pair-auth) — Service account best practice
* [CREATE USER](https://docs.snowflake.com/en/sql-reference/sql/create-user) — User creation options