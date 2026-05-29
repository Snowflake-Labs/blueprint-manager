<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll transfer object ownership from ad-hoc or personal roles to standard hierarchy roles. In Snowflake, OWNERSHIP is always a **role-level** privilege — the active role at creation time owns new objects, not the user. When a role that owns objects is dropped, Snowflake silently reassigns that ownership to the executing role without preserving existing grants, which can break shares and dependent grant chains.

**Account Context:** Execute from the target account with SECURITYADMIN role. This step **must run before** Step 2.4 (Enforce Managed Access Schemas) — see the Managed Access Ordering Rule below.

## Why is this important?

The common concern framed as "a user owns a table" is technically imprecise in Snowflake. What actually happens is that an **ad-hoc or personal role** (created for a one-off migration, project, or sandbox) owns the objects. This creates two compounding risks:

- **Silent ownership reassignment on DROP ROLE**: Snowflake reassigns ownership to the role executing `DROP ROLE` with no `COPY CURRENT GRANTS`. Existing downstream grants (shares, database roles, dependent views) may silently break.
- **Outside the audited hierarchy**: Roles that own objects but have no parent in the standard hierarchy are invisible to role-based access reviews. Step 1.1 (audit-role-hierarchy) surfaces these in Sections 5 and 6 — but no prior step generates the remediation SQL.

## Prerequisites

- Task 1 (RBAC Assessment) completed — Step 1.1 (audit-role-hierarchy) Sections 5 and 6 surface the ownership gaps this step remediates
- Step 2.3 (Revoke Direct User Privileges) completed

## Managed Access Ordering Rule

This step **must run before** Step 2.4 (Enforce Managed Access Schemas). Once a schema is converted to managed access, `GRANT OWNERSHIP` is restricted to roles that are **subordinate to the schema owner**. Running ownership transfer first maximizes flexibility — you can transfer to any role regardless of hierarchy position. If the schema is already in managed access mode, the sanity-check query (Step 2 of the generated SQL) will flag any target roles that are not subordinate to the schema owner; those transfers will fail and must be resolved before proceeding.

## Key Concepts

**GRANT OWNERSHIP ON ALL vs. GRANT OWNERSHIP ON FUTURE**

| Form | COPY CURRENT GRANTS | Effect |
|------|---------------------|--------|
| `GRANT OWNERSHIP ON ALL <type> IN SCHEMA` | ✅ Supported | Transfers existing objects, preserves downstream grants |
| `GRANT OWNERSHIP ON FUTURE <type> IN SCHEMA` | ❌ Not valid | Sets default owner for new objects only |

Always use `COPY CURRENT GRANTS` on the bulk form to avoid silently dropping existing privileges.

**Standard Hierarchy Roles**

The discovery query excludes `ACCOUNTADMIN`, `SECURITYADMIN`, `SYSADMIN`, `USERADMIN`, and `PUBLIC` — these are expected owners. Any other role that appears in the discovery output is a candidate for ownership transfer.

## Best Practices

- Use `SYSADMIN` or a domain-level ADMIN role as the target owner for production objects
- Run the discovery query first and review all findings before executing any transfers
- Always use `COPY CURRENT GRANTS` on the bulk transfer form
- After transferring ownership, drop or archive the vacated personal/ad-hoc roles to prevent future drift
- Re-run Step 1.1 (audit-role-hierarchy) after this step to confirm Section 6 findings are resolved

## How to Test

1. Run the discovery query (Step 1 of the SQL) to baseline ownership counts by role
2. Review the sanity-check output (Step 2) — resolve any WARNING rows before proceeding
3. Execute the ownership transfer statements (Step 3)
4. Re-run the discovery query (Step 4) — expected result: zero rows for in-scope schemas

## More Information

* [GRANT OWNERSHIP](https://docs.snowflake.com/en/sql-reference/sql/grant-ownership) — Syntax, COPY CURRENT GRANTS behavior, managed-access restrictions
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas) — Ownership transfer constraints
* [GRANTS_TO_ROLES](https://docs.snowflake.com/en/sql-reference/account-usage/grants_to_roles) — Account Usage view for ownership auditing


### Configuration Questions

#### Do you want to transfer object ownership from non-hierarchy roles to a standard role? (`rbac_reassign_ownership`: single-select)
**What is this asking?**
Choose whether to generate SQL that transfers OWNERSHIP of objects (tables, views,
stages, functions, procedures, dynamic tables) from ad-hoc or personal roles to
roles within the standard hierarchy.

**Why does this matter?**
In Snowflake, OWNERSHIP is a role-level privilege — the active role at creation
time owns new objects, not the user. When an ad-hoc or personal role that owns
objects is dropped, Snowflake silently reassigns ownership to the executing role
with no COPY CURRENT GRANTS. Existing downstream grants (shares, dependent views)
may silently break.

Step 1.1 (audit-role-hierarchy) Sections 5 and 6 surface these gaps. This step
generates the remediation SQL.

**Options explained:**
- **Yes**: Generate discovery and bulk GRANT OWNERSHIP ... COPY CURRENT GRANTS
  statements for all configured schemas.
- **No**: Skip ownership transfer. Choose this if ownership is already consolidated
  into hierarchy roles or if you prefer to handle transfers manually.

**Important:** This step must run BEFORE Step 2.4 (Enforce Managed Access Schemas).
After a schema is converted to managed access, ownership transfers are restricted
to roles subordinate to the schema owner.

**Recommendation:** Yes. Even if no immediate action is needed, running the
discovery query surfaces any ownership outside the hierarchy.

**More Information:**
* [GRANT OWNERSHIP](https://docs.snowflake.com/en/sql-reference/sql/grant-ownership)

**Options:**
- Yes
- No

#### Which role should receive ownership when no per-schema target is specified? (`rbac_target_owner_role`: text)
**What is this asking?**
Provide the fallback role name used as the ownership transfer target when
`rbac_ownership_scope` is not configured or for schemas not listed in scope.

**Why does this matter?**
When no per-schema scope is provided, the generated SQL comment uses this role
as the placeholder for manual execution. When scope is configured but a schema
entry omits a target, this role is used as the default.

**Examples:**
- `SYSADMIN` — Snowflake best-practice default; owns infrastructure objects
- `FINAJ_PROD_ADMIN` — Domain ADMIN role for a specific data product
- `DATA_PLATFORM_ADMIN` — Centralized platform team ownership role

**Recommendation:** Use `SYSADMIN` for production accounts unless your organization
uses a dedicated platform-admin role. Avoid ACCOUNTADMIN — it is a break-glass
role and should not own data objects.

**More Information:**
* [System-Defined Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#system-defined-roles)


#### Which schemas should have ownership transferred, and to which role? (`rbac_ownership_scope`: object-list)
**What is this asking?**
Define the list of schemas whose objects should have ownership transferred,
and specify the target role for each schema. This is optional: if left empty,
the generated SQL provides commented-out templates using `rbac_target_owner_role`
as the default.

**Why does this matter?**
Different schemas may be owned by different domain-level ADMIN roles. Specifying
per-schema targets lets the generated SQL be executed directly without manual
substitution.

**Fields:**
- **database**: The Snowflake database name (e.g., SALES_ANALYTICS_PROD_DB)
- **schema**: The schema name within that database (e.g., RAW, CURATED, PUBLISHED)
- **target_role**: The role that should receive ownership (e.g., SALES_ANALYTICS_PROD_ADMIN)

**Managed Access Constraint:**
If a schema is already in managed access mode, `target_role` must be a role
subordinate to the schema owner. The sanity-check query in the generated SQL
will flag incompatible combinations before any transfers are executed.

**Examples:**
```yaml
- database: SALES_ANALYTICS_PROD_DB
  schema: RAW
  target_role: SALES_ANALYTICS_PROD_ADMIN
- database: SALES_ANALYTICS_PROD_DB
  schema: CURATED
  target_role: SALES_ANALYTICS_PROD_ADMIN
- database: FINANCE_REPORTING_DB
  schema: PUBLISHED
  target_role: SYSADMIN
```

**Recommendation:** Populate this list using the discovery query output from
Step 1.1 (audit-role-hierarchy) Section 6. Match each schema to the ADMIN
role of the owning data product.

**More Information:**
* [GRANT OWNERSHIP](https://docs.snowflake.com/en/sql-reference/sql/grant-ownership)
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)

