# Consumer Access

## Summary
Enable external consumers to access your data product by creating purpose-specific
consumer access roles that provide granular, SCIM-manageable access for end users
who need only specific data zones.

## External Requirements
- Task 3 completed (all infrastructure in place)
- Knowledge of consumer groups and their data needs
- SCIM prefix configured (if using SCIM)

## Personas
- Data Product Owner
- Security Administrator
- Identity Team

## Role Requirements
- USERADMIN role (or SCIM provisioner role if using SCIM)

## Details
## **Why Consumer Access Roles?**

The core `<prefix>_READ` role provides read access across the entire data product - all zones, all schemas. This is typically too broad for end users who:
- Only need access to curated/published data (not raw or transformed)
- Should not see intermediate processing tables
- Need SCIM-managed role assignments for identity governance
- Require audit-friendly access patterns

Consumer access roles solve this by creating purpose-specific roles that:
- Grant access only to specific schemas (typically CURATED or PUBLISHED zones)
- Can be managed via SCIM for user assignment
- Support compliance requirements with clear purpose documentation
- Enable self-service access requests through identity governance workflows

## **Steps in This Task**

| Step | Title | Purpose |
|------|-------|---------|
| 4.1 | Create Custom Read Roles | SCIM-manageable roles for specific consumer groups |
| 4.2 | Grant Database Access to Roles | Wire consumer roles to specific database roles |

## **Consumer Role Pattern**

```
<prefix>_<stem>_<purpose>
```

| Component | Description | Example |
|-----------|-------------|---------|
| prefix | Data product prefix | `SALES_ANALYTICS_PRD` |
| stem | Subject area or consumer group | `REVENUE`, `MARKETING` |
| purpose | Access type | `RO` (Read-Only), `PI` (PII Access) |

## **Consumer Role Hierarchy**

```
Consumer Role (SCIM-managed)
└── Granted specific database roles
    └── DB_R or specific SC_R_* roles
        └── Read access to specific schemas only
```

## **SCIM Integration**

When SCIM is enabled:
- Consumer roles are owned by `<scim_prefix>_PROVISIONER`
- Users are assigned to consumer roles via SCIM (identity provider)
- No manual user grants required
- Access reviews happen in the identity provider

## **What You'll Create**

| Object Type | Naming Pattern | Owner | Purpose |
|-------------|----------------|-------|---------|
| Consumer Roles | `<prefix>_<stem>_<purpose>` | `<scim_prefix>_PROVISIONER` or `USERADMIN` | End-user access |
| Role Grants | Database role → Consumer role | N/A | Wire access |

## **More Information**

* [Database Roles](https://docs.snowflake.com/en/user-guide/security-access-control-database-roles)
* [SCIM Provisioning](https://docs.snowflake.com/en/user-guide/admin-security-fed-auth-overview)