<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll assign users to functional roles in the Data Product role hierarchy. Instead of granting privileges directly to users, each user is assigned a role level (READ, WRITE, CREATE, or ADMIN) for each data product they need to access.

**Account Context:** Execute from the target account with SECURITYADMIN role.

## Why is this important?

Functional roles are the foundation of scalable RBAC:
- **Consistent access** — All users at the same level have identical privileges
- **Easy onboarding** — New users get one role grant instead of dozens of object grants
- **SCIM compatible** — Identity providers manage group-to-role mappings
- **Auditable** — Role membership shows exactly who can do what

## Prerequisites

- Data Product roles exist (created via Data Product Setup blueprint)
- Task 2 completed (privileges hardened, direct grants revoked)
- User-to-role mappings approved by data owners

## Key Concepts

**Data Product Role Hierarchy**
| Level | Role Pattern | Capabilities |
|-------|-------------|-------------|
| READ | `<PREFIX>_READ` | SELECT on all tables/views |
| WRITE | `<PREFIX>_WRITE` | INSERT, UPDATE, DELETE + READ |
| CREATE | `<PREFIX>_CREATE` | CREATE TABLE, CREATE VIEW + WRITE |
| ADMIN | `<PREFIX>_ADMIN` | OWNERSHIP, manage grants + CREATE |
| RBAC | `<PREFIX>_RBAC` | Role management (separate branch) |

**Role Assignment Pattern**
```sql
GRANT ROLE <PREFIX>_READ TO USER <username>;
```

Each higher role inherits from the lower roles, so granting WRITE also provides READ access.

## Best Practices

- Assign the **minimum role level** needed for each user's job function
- Use RBAC roles only for team leads or data stewards who manage access
- Document the business justification for each ADMIN role assignment
- Review role assignments quarterly
- For SCIM-managed environments, map identity provider groups to functional roles

## How to Test

1. As the assigned user, verify you can perform operations at your role level
2. Verify you cannot perform operations above your role level
3. For WRITE users: confirm SELECT + INSERT works, but CREATE TABLE fails
4. For READ users: confirm SELECT works, but INSERT fails

## More Information

* [Role-Based Access Control](https://docs.snowflake.com/en/user-guide/security-access-control-overview) — RBAC overview
* [GRANT ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-role) — Granting roles to users


### Configuration Questions

#### Which users should be assigned to data product functional roles? (`rbac_user_role_assignments`: object-list)
**What is this asking?**
Define which end users should be granted which data product functional roles.
For each assignment, specify the user's login name, the data product role prefix,
and the access level (READ, WRITE, CREATE, or ADMIN).

**Why does this matter?**
Data Product Setup creates the role hierarchy (ADMIN, CREATE, WRITE, READ) but
does not assign any end users. Without this step, the roles exist but nobody
can use them. This is the bridge between infrastructure and actual access.

**Fields:**
- **user_name**: The Snowflake login name of the user
- **role_level**: One of READ, WRITE, CREATE, or ADMIN
- **data_product_prefix**: The role prefix (e.g., SALES_ANALYTICS_PROD)

**Access Level Guide:**
| Level | Can Do | Typical Users |
|-------|--------|---------------|
| READ | Query all data in the data product | Analysts, BI tools, data consumers |
| WRITE | READ + insert/update/delete data | Data engineers, ETL processes |
| CREATE | WRITE + create objects, apply policies | Senior engineers, data architects |
| ADMIN | CREATE + own infrastructure, manage RBAC | Data product owners, platform team |

**Examples:**
```yaml
- user_name: JSMITH
  role_level: READ
  data_product_prefix: SALES_ANALYTICS_PROD
- user_name: JDOE
  role_level: WRITE
  data_product_prefix: SALES_ANALYTICS_PROD
```

**Recommendation:** Follow the principle of least privilege — assign the
minimum access level each user needs. Most users should be READ; ADMIN should
be limited to 1-2 data product owners.

**More Information:**
* [GRANT ROLE](https://docs.snowflake.com/en/sql-reference/sql/grant-role)

