<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll generate diagnostic queries that detect stale access — unused roles, dormant users with active privileges, users who have never logged in but hold role grants, and active human users who have not enrolled in any MFA method. Stale access is a security risk because it provides attack surface without business value.

**Account Context:** Execute these queries from the target account with ACCOUNTADMIN role.

## Why is this important?

Stale access accumulates over time as employees change roles, leave the organization, or projects are decommissioned. Risks include:
- **Orphaned credentials** — Dormant users may have credentials that are compromised without detection
- **Unused roles** — Roles with no active users consuming them indicate RBAC drift
- **Compliance violations** — Most frameworks (SOC 2, HIPAA) require periodic access review and removal of stale grants

## Prerequisites

- Account accessible with ACCOUNTADMIN role
- SNOWFLAKE database IMPORTED PRIVILEGES granted
- LOGIN_HISTORY data available (up to 365 days)

## Key Concepts

**Dormant Users**
Users who have not logged in for 90+ days but still have active role grants. These accounts should be reviewed for deactivation or privilege removal.

**Unused Roles**
Roles that exist in the hierarchy but are not granted to any user, or are only granted to users who haven't logged in recently.

**Last Login Analysis**
Snowflake's LOGIN_HISTORY view provides login records for up to 365 days. Users are bucketed into:
- **Active** (<30 days since last login)
- **Stale** (30-90 days)
- **Dormant** (>90 days)
- **Never** (no login record)

## Best Practices

- Disable dormant users (`ALTER USER SET DISABLED = TRUE`) rather than dropping them immediately
- Revoke role grants from dormant users before disabling
- Keep disabled users for 30-90 day retention period, then drop
- Run stale access detection monthly

## How to Test

1. Run the dormant users query — verify results against your HR/identity records
2. Cross-reference unused roles with the role hierarchy audit
3. Confirm "never logged in" users are not pending onboarding

## MFA Enrollment Gaps (Step 6)

Step 6 identifies active human users (`TYPE NOT IN ('SERVICE', 'LEGACY_SERVICE')`) who have not enrolled in any MFA method.

**Why `HAS_MFA` and not `EXT_AUTHN_DUO`?**
`HAS_MFA` is the correct column to use. It reflects enrollment across all supported MFA methods — TOTP authenticator apps, passkeys, and Duo. `EXT_AUTHN_DUO` is a legacy Duo-specific field and will miss users enrolled via other methods.

**Snowflake BCR 2025_06 — Phased MFA Enforcement**
Snowflake is rolling out mandatory MFA enforcement in phases:
- **Phase 1** (Sep 2025 – Jan 2026, currently active): MFA enforced for Snowsight password logins only.
- **Phase 3** (Aug – Oct 2026): MFA extended to all password-based interfaces, including JDBC/ODBC drivers and BI tools.

Until Phase 3 completes, non-Snowsight authentication pathways remain a gap even on accounts that appear policy-compliant.

**`BYPASS_MFA_UNTIL` exemptions**
Even when `MFA_ENROLLMENT = 'REQUIRED'` is set in an auth policy, users who have not logged in since the policy was applied will not yet have enrolled. The `BYPASS_MFA_UNTIL` column surfaces temporary exemptions that may have been granted and should be reviewed.

## More Information

* [LOGIN_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/login_history) — User login records
* [ALTER USER](https://docs.snowflake.com/en/sql-reference/sql/alter-user) — Disabling users
* [QUERY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) — Query activity
* [USERS view](https://docs.snowflake.com/en/sql-reference/account-usage/users) — HAS_MFA, BYPASS_MFA_UNTIL columns
* [BCR 2025_06](https://docs.snowflake.com/en/release-notes/bcr-bundles/2025_06/bcr-1680) — Mandatory MFA enforcement phased rollout


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

