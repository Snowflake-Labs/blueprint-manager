<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll create a set of monitoring views in a dedicated RBAC_MONITORING database. These views provide ongoing visibility into role membership, privilege changes, direct user grants (RBAC bypasses), role hierarchy depth, and user activity status.

**Account Context:** Execute from the target account with SYSADMIN (view creation) and SECURITYADMIN (grants).

## Why is this important?

RBAC hardening is not a one-time activity. Without continuous monitoring:
- **Configuration drift** — New direct grants or PUBLIC grants accumulate over time
- **Privilege creep** — Users accumulate roles beyond what they need
- **Dormant accounts** — Inactive users retain access, increasing attack surface
- **Compliance gaps** — Auditors expect evidence of ongoing access review

These monitoring views provide the foundation for alerts (Step 4.2) and access review reports (Step 4.3).

## Prerequisites

- Tasks 1-3 completed (assessment, hardening, provisioning)
- A designated warehouse for running monitoring queries
- SYSADMIN role for creating the monitoring database and views

## Key Concepts

**Monitoring Views**
| View | Purpose | Data Source |
|------|---------|-------------|
| V_ROLE_MEMBERSHIP | Current role assignments | GRANTS_TO_USERS |
| V_PRIVILEGE_CHANGES | Grant/revoke history | GRANTS_TO_ROLES |
| V_DIRECT_USER_GRANTS | RBAC bypass detection | GRANTS_TO_USERS |
| V_ROLE_HIERARCHY_DEPTH | Role chain analysis | GRANTS_TO_ROLES (recursive) |
| V_USER_ACTIVITY | Login/dormancy tracking | USERS |

**Health Indicators**
- `V_DIRECT_USER_GRANTS` should return **zero rows** (no bypasses)
- `V_ROLE_HIERARCHY_DEPTH` should show all roles as **HEALTHY** (depth ≤ 4)
- `V_USER_ACTIVITY` should have no **DORMANT** users with active roles

## Best Practices

- Schedule monitoring queries to run on a regular cadence (daily or weekly)
- Use a dedicated, auto-suspend warehouse for monitoring to control costs
- Grant SELECT on monitoring views to your security operations role
- Integrate monitoring view outputs with your SIEM or alerting platform

## How to Test

1. Query each view and verify it returns expected results
2. Confirm V_DIRECT_USER_GRANTS returns zero rows (if Step 2.3 was completed)
3. Check V_ROLE_HIERARCHY_DEPTH for any CRITICAL or WARNING roles
4. Review V_USER_ACTIVITY for dormant or never-logged-in users

## More Information

* [Account Usage Views](https://docs.snowflake.com/en/sql-reference/account-usage) — Data sources
* [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles) — Privilege tracking
* [GRANTS_TO_USERS](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_users) — User access tracking


### Configuration Questions

#### Which warehouse should be used for RBAC monitoring tasks and alerts? (`rbac_monitoring_warehouse`: text)
**What is this asking?**
Specify the warehouse that will execute RBAC monitoring queries and alert
checks. This warehouse runs the scheduled monitoring views and alert
conditions.

**Why does this matter?**
RBAC monitoring queries run against Account Usage views and can be
resource-intensive on large accounts. Using a dedicated or shared platform
warehouse keeps monitoring costs separate from data product workloads.

**Examples:**
- `PLAT_INFRA_WH_ADMIN` — Platform administration warehouse
- `MONITORING_WH` — Dedicated monitoring warehouse
- `COMPUTE_WH` — General-purpose warehouse (for smaller accounts)

**Recommendation:** Use your platform administration warehouse if one exists.
For cost efficiency, an X-Small warehouse with AUTO_SUSPEND = 60 is sufficient
for monitoring workloads.

**More Information:**
* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse)


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

