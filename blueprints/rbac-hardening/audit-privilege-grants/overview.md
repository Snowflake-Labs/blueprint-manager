<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll generate diagnostic queries that discover privilege grant issues across your account. These queries find direct user-level grants (which should be on roles instead), PUBLIC role exposure, users with ACCOUNTADMIN, and roles with powerful account-level privileges.

**Account Context:** Execute these queries from the target account with ACCOUNTADMIN role.

## Why is this important?

Privilege grants are the mechanism by which roles gain access to objects. Common misconfigurations include:
- **Direct user grants** — Privileges granted directly to users bypass the role hierarchy and are invisible to role-based audits
- **PUBLIC role exposure** — Grants to PUBLIC give every user access, often unintentionally
- **ACCOUNTADMIN overuse** — Too many users with ACCOUNTADMIN defeats separation of duties
- **Excessive privileges** — Roles with MANAGE GRANTS or OWNERSHIP on account-level objects can escalate their own access

## Prerequisites

- Account accessible with ACCOUNTADMIN role
- SNOWFLAKE database IMPORTED PRIVILEGES granted

## Key Concepts

**Direct User Grants**
In Snowflake, privileges can be granted to either roles or users. Granting directly to users is an anti-pattern because it bypasses the role hierarchy. Access should always flow through roles.

**PUBLIC Role Grants**
Every user in the account automatically inherits all privileges granted to PUBLIC. Common issues include warehouse USAGE (compute costs), database/schema USAGE (metadata visibility), and table SELECT (data exposure).

**Account-Level Privileges**
High-risk privileges include:
| Privilege | Risk |
|-----------|------|
| MANAGE GRANTS | Can grant any privilege to any role |
| CREATE ROLE | Can create new roles |
| CREATE USER | Can create new users |
| EXECUTE TASK | Can run scheduled operations |
| MONITOR USAGE | Can view all account activity |

## Best Practices

- All access should flow through roles, never directly to users
- PUBLIC role should have minimal or no grants
- ACCOUNTADMIN should be limited to 2-3 break-glass users
- MANAGE GRANTS should only be on SECURITYADMIN
- Audit privilege grants quarterly at minimum

## How to Test

1. Run the direct user grants query — any results need immediate remediation
2. Review PUBLIC grants — each should have a documented business justification
3. Verify ACCOUNTADMIN count matches your break-glass policy

## More Information

* [Privilege Overview](https://docs.snowflake.com/en/user-guide/security-access-control-privileges) — Available privileges
* [GRANTS_TO_USERS](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users) — User grant history
* [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles) — Role grant history


### Configuration Questions

#### What scope should the RBAC audit cover? (`rbac_audit_scope`: single-select)
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

