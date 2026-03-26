<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll generate diagnostic queries that reveal the complete role hierarchy in your Snowflake account. These queries help you visualize how roles are connected, discover orphaned roles with no parent, and identify hierarchies that are excessively deep.

**Account Context:** Execute these queries from the target account with ACCOUNTADMIN role (for Account Usage access).

## Why is this important?

A healthy role hierarchy is the foundation of Snowflake RBAC. Common issues include:
- **Orphaned roles** — Roles granted to no parent, making them unreachable from system roles
- **Excessive depth** — Hierarchies deeper than 5 levels are hard to audit and maintain
- **Missing connections** — Data product roles not wired up to SYSADMIN
- **Circular grants** — Roles that form loops (rare but possible)

Without visibility into the full hierarchy, you cannot confirm that your RBAC design is implemented correctly.

## Prerequisites

- Account accessible with ACCOUNTADMIN or SECURITYADMIN role
- SNOWFLAKE database IMPORTED PRIVILEGES granted (for Account Usage views)
- Data Product Setup completed (if auditing data product roles)

## Key Concepts

**Role Hierarchy**
Snowflake roles form a directed acyclic graph (DAG). Each role can be granted to one or more parent roles, and a role inherits all privileges of its child roles.

**System Roles**
| Role | Purpose |
|------|---------|
| ACCOUNTADMIN | Top-level role — should be break-glass only |
| SECURITYADMIN | Manages grants and role assignments |
| SYSADMIN | Creates and owns databases, schemas, warehouses |
| USERADMIN | Creates and manages users and roles |
| PUBLIC | Automatically granted to every user |

**Orphaned Roles**
A role that is not granted to any parent role (except PUBLIC) is effectively unreachable from the standard hierarchy. This usually indicates incomplete setup or a role that was created manually outside of the blueprint process.

## Best Practices

- Every custom role should eventually roll up to SYSADMIN (for object access) or SECURITYADMIN (for security management)
- Keep hierarchy depth to 5 levels or fewer for auditability
- Use the Data Product Setup pattern: READ → WRITE → CREATE → ADMIN → SYSADMIN
- Review orphaned roles quarterly and either wire them into the hierarchy or drop them

## How to Test

1. Run the role hierarchy query and verify all data product roles connect to SYSADMIN
2. Check the orphaned roles query — any results need investigation
3. Confirm hierarchy depth is within acceptable limits

## More Information

* [Role Hierarchy](https://docs.snowflake.com/en/user-guide/security-access-control-overview#role-hierarchy-and-privilege-inheritance) — How role inheritance works
* [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles) — Account Usage view for role grants
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles) — Built-in role descriptions

### Configuration Questions

#### What scope should the RBAC audit cover? (`rbac_audit_scope`: multi-select)
Choose whether to audit the full account or limit to specific data product role hierarchies. A full account audit is recommended for first-time hardening.

**Options:**
- Full Account
- Specific Data Products

#### Which data product prefixes should the RBAC audit cover? (`rbac_target_prefixes`: list)
If scoping to specific data products, provide the role name prefixes. Run `SHOW ROLES LIKE '%_ADMIN';` to find them.


### Configuration Questions

#### What scope should the RBAC audit cover? (`rbac_audit_scope`: multi-select)
**What is this asking?**
Choose whether to audit role-based access controls across the entire Snowflake
account or limit the audit to specific data product role hierarchies.

**Why does this matter?**
A full account audit examines every role, grant, and user assignment in the
account. This is thorough but may produce a large volume of findings. Scoping
to specific data products focuses the audit on the role hierarchies created by
Data Product Setup (ADMIN, CREATE, WRITE, RBAC, READ and their database roles).

**Options explained:**
- **Full Account**: Audit all roles, grants, and user assignments. Recommended
  for initial hardening or compliance reviews.
- **Specific Data Products**: Audit only the role hierarchies matching the
  provided data product prefixes. Useful for targeted reviews after changes.

**Recommendation:** Use "Full Account" for your first RBAC hardening pass,
then switch to "Specific Data Products" for periodic maintenance reviews.

**More Information:**
* [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview)

**Options:**
- Full Account
- Specific Data Products

#### Which data product prefixes should the RBAC audit cover? (`rbac_target_prefixes`: list)
**What is this asking?**
Provide the role name prefixes for the data products you want to audit. These
are the prefixes used when creating data product roles (e.g., SALES_ANALYTICS_PROD,
FINANCE_REPORTING_DEV).

**Why does this matter?**
When the audit scope is set to "Specific Data Products", these prefixes filter
the audit queries to only examine roles matching these patterns. This keeps
findings focused and actionable.

**How to find your prefixes:**
Run `SHOW ROLES LIKE '%_ADMIN';` and look for your data product ADMIN roles.
The prefix is everything before `_ADMIN`.

**Examples:**
- `SALES_ANALYTICS_PROD` (Single Account: domain_name_env)
- `FINANCE_REPORTING` (Multi-Account Environment-based: domain_name)
- `CLAIMS_DEV` (Multi-Account Domain-based: name_env)
- `INVENTORY` (Multi-Account Domain+Env: name)

**Recommendation:** Include all data products that were set up using the
Data Product Setup blueprint.

