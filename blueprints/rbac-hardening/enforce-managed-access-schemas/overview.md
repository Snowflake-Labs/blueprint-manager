<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll convert existing schemas to use Snowflake's Managed Access feature, which centralizes privilege management by restricting GRANT authority to the schema owner (or SECURITYADMIN), instead of allowing any role with ownership to manage grants.

**Account Context:** Execute from the target account with SECURITYADMIN role.

## Why is this important?

Without Managed Access, any role that owns an object within a schema can grant access to that object. This leads to:
- **Shadow access patterns** — Object owners can bypass RBAC by granting directly
- **Privilege sprawl** — Grants proliferate without centralized control
- **Audit gaps** — Security teams cannot guarantee that only approved roles have access

With `MANAGED ACCESS`, only the schema owner and SECURITYADMIN (or higher) can manage grants on objects within the schema, regardless of who owns those objects.

## Prerequisites

- Task 1 (RBAC Assessment) completed
- Steps 2.1–2.3 completed (PUBLIC restricted, admin separated, direct grants revoked)
- Understanding of which schemas should be converted (all data-product schemas recommended)

## Key Concepts

**Managed Access vs. Standard Schemas**
| Feature | Standard Schema | Managed Access Schema |
|---------|----------------|----------------------|
| Object owner can GRANT | Yes | **No** |
| Schema owner can GRANT | Yes | Yes |
| SECURITYADMIN can GRANT | Yes | Yes |
| Privilege sprawl risk | High | **Low** |
| Central control | No | **Yes** |

**Applying Managed Access**
- New schemas: `CREATE SCHEMA <name> WITH MANAGED ACCESS;`
- Existing schemas: `ALTER SCHEMA <name> ENABLE MANAGED ACCESS;`
- Reverting (not recommended): `ALTER SCHEMA <name> DISABLE MANAGED ACCESS;`

## Best Practices

- Enable Managed Access on **all production schemas**
- Apply at schema creation time via Data Product Setup templates
- Do not disable Managed Access once enabled unless absolutely necessary
- Monitor for schemas created without Managed Access using the monitoring views in Task 4

## How to Test

1. In a Managed Access schema, attempt to GRANT from an object-owner role (should fail)
2. Verify SECURITYADMIN can still GRANT on objects in the schema
3. Verify schema owner can still GRANT on objects in the schema

## More Information

* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas) — Feature documentation
* [ALTER SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/alter-schema) — Enabling managed access


### Configuration Questions

#### Do you want to convert existing schemas to managed access? (`rbac_enforce_managed_access`: single-select)
**What is this asking?**
Choose whether to generate ALTER SCHEMA statements that enable WITH MANAGED ACCESS
on existing schemas.

**Why does this matter?**
In a standard schema, the object owner can grant privileges on their objects to
any role. This creates "shadow security" where access is granted outside of
centralized control. Managed access schemas restrict grant authority to the
schema owner and SECURITYADMIN, ensuring all access goes through the approved
RBAC hierarchy.

**Options explained:**
- **Yes**: Generate ALTER SCHEMA ... ENABLE MANAGED ACCESS for all schemas
  (excluding INFORMATION_SCHEMA and system schemas).
- **No**: Skip managed access enforcement. Choose this if your schemas already
  use managed access or if object owners intentionally manage their own grants.

**Recommendation:** Yes. Managed access is a Snowflake best practice for
production environments. It ensures the RBAC hierarchy defined in Data Product
Setup is the only path to data access.

**More Information:**
* [Managed Access Schemas](https://docs.snowflake.com/en/user-guide/security-access-control-overview#managed-access-schemas)
* [ALTER SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/alter-schema)

**Options:**
- Yes
- No

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

