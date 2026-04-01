<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll generate a comprehensive access review report that covers all aspects of your RBAC posture. This report should be run on a regular cadence and reviewed by your security team to maintain compliance and detect configuration drift.

**Account Context:** Execute from the target account with SECURITYADMIN role.

## Why is this important?

Access reviews are a core requirement for security compliance frameworks:
- **SOC 2** — Requires periodic access reviews for logical access controls
- **HIPAA** — Requires regular review of access to PHI
- **PCI-DSS** — Requires quarterly access reviews for cardholder data environments
- **SOX** — Requires evidence of access control effectiveness

Beyond compliance, regular reviews catch:
- Privilege creep from role accumulation
- Dormant accounts that increase attack surface
- Shadow access from direct user grants
- Overprivileged service accounts

## Prerequisites

- Step 4.1 (RBAC Monitoring Views) completed — report queries these views
- Step 4.2 (Alerts) recommended but not required
- Monitoring warehouse provisioned
- SECURITYADMIN role access

## Key Concepts

**Report Sections**
| # | Section | What It Checks |
|---|---------|---------------|
| 1 | Executive Summary | Overall user counts and health metrics |
| 2 | ACCOUNTADMIN Holders | Verify against authorized break-glass list |
| 3 | RBAC Bypasses | Direct user grants (should be zero) |
| 4 | Role Hierarchy Health | Excessive role chain depth |
| 5 | Dormant Users | Inactive users with active roles |
| 6 | Recent Changes | Privilege modifications since last review |
| 7 | PUBLIC Role Grants | Grants to PUBLIC (should be minimal) |
| 8 | MFA Status | Users without MFA on privileged roles |

**Review Frequency**
| Cadence | Lookback Period | Best For |
|---------|----------------|----------|
| Weekly | 7 days | High-security environments, SOX |
| Monthly | 30 days | Standard compliance requirements |
| Quarterly | 90 days | Lower-risk environments |

## Best Practices

- Assign a specific owner for each report section
- Track remediation actions (disable dormant users, revoke bypasses)
- Archive reports for audit evidence
- Escalate critical findings (unauthorized ACCOUNTADMIN, RBAC bypasses)
- Trend metrics over time to identify improvement or degradation

## How to Test

1. Run the full report query set
2. Verify each section returns data (or the expected empty set)
3. Cross-reference Section 2 with your authorized ACCOUNTADMIN list
4. Confirm Section 3 returns zero rows (no RBAC bypasses)

## More Information

* [Access Control](https://docs.snowflake.com/en/user-guide/security-access-control) — Security overview
* [Account Usage](https://docs.snowflake.com/en/sql-reference/account-usage) — Audit data sources


### Configuration Questions

#### How often should access reviews be conducted? (`rbac_review_frequency`: single-select)
**What is this asking?**
Select how frequently your organization should review RBAC configurations
and user access assignments.

**Why does this matter?**
Regular access reviews are a core requirement of most compliance frameworks
(SOC 2, HIPAA, PCI-DSS, SOX). The review frequency determines:
- How quickly stale access is detected
- How often compliance documentation is generated
- The cadence for the access review report

**Options explained:**
- **Weekly**: High-security environments or accounts with frequent user changes.
  Generates a focused diff report each week.
- **Monthly**: Standard recommendation for most organizations. Balances
  security with operational overhead.
- **Quarterly**: Minimum recommended frequency. Suitable for stable environments
  with few access changes.

**Recommendation:** Monthly for production accounts. Weekly during initial
hardening or after organizational changes. Quarterly only for non-production
accounts with low change rates.

**More Information:**
* [SOC 2 Access Reviews](https://docs.snowflake.com/en/user-guide/security-access-control-overview)

**Options:**
- Weekly
- Monthly
- Quarterly

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

