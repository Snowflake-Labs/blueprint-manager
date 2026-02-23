# Core Roles & Database Setup

## Summary
Create the foundational infrastructure for your data product including five
core account-level roles, databases for each zone with database-level access
roles, schemas with schema-level access roles, and complete role hierarchy.

## External Requirements
- Task 1 (Data Product Planning) completed
- Target account accessible
- data_product_name, data_product_domain, data_product_environment from Task 1
- scim_prefix, data_zones, schema_configuration from Task 1

## Personas
- Platform Administrator
- Data Architect
- Security Administrator

## Role Requirements
- USERADMIN role
- SYSADMIN role
- SECURITYADMIN role

## Details
## **Understanding Snowflake Roles**

Snowflake uses **Role-Based Access Control (RBAC)**. Permissions aren't granted directly to users — instead:

1. **Privileges** are granted to **roles**
2. **Roles** are granted to **users** (or other roles)
3. **Users** inherit privileges from all their roles

## **Account Roles vs. Database Roles**

| Type | Scope | Created By | Use Case |
|------|-------|------------|----------|
| **Account Role** | Entire account | USERADMIN/SECURITYADMIN | User assignment, cross-database access |
| **Database Role** | Single database | Database owner | Delegated administration within a database |

## **Understanding Tags**

**Tags** are metadata labels you attach to Snowflake objects for FinOps, governance, and discovery:

| Tag | Applied To | Purpose |
|-----|------------|---------|
| `DOMAIN` | Roles, Databases, Warehouses | Cost allocation by business domain |
| `ENVIRONMENT` | Databases, Warehouses | Distinguish dev/test/prod |
| `DATAPRODUCT` | Databases, Warehouses | Identify owning data product |
| `ZONE` | Databases | Data processing stage (RAW, CURATED, etc.) |
| `WORKLOAD` | Warehouses | Compute purpose (INGEST, TRANSFORM, BI) |

## **Steps in This Task**

| Step | Title | Purpose |
|------|-------|---------|
| 2.1 | Create Data Product Core Roles | Create ADMIN, CREATE, WRITE, RBAC, READ account roles |
| 2.2 | Create Databases | Create zone databases with DB_R/DB_W/DB_C database roles |
| 2.3 | Create Schemas | Create schemas with SC_R/SC_W/SC_C database roles |

## **Role Architecture**

```
SYSADMIN
└── <dataproduct>_ADMIN (owns infrastructure)
    ├── <dataproduct>_CREATE (creates objects, has account access roles)
    └── <dataproduct>_RBAC (owns access roles)

Database Roles:  DB_C           DB_W            DB_R
                   ↑               ↑               ↑
Schema Roles:   SC_C_<schema> ← SC_W_<schema> ← SC_R_<schema>
```

## **Tag-Based Cost Allocation**

## **Deliverables**

Upon completing this task, you will have:
- ✅ Five core account roles created and hierarchically linked
- ✅ Account access roles granted to CREATE role
- ✅ Databases created for each zone with database roles
- ✅ Schemas created with managed access and schema roles
- ✅ Complete role hierarchy from schema → database → account level

## **More Information**

* [Access Control Overview](https://docs.snowflake.com/en/user-guide/security-access-control-overview)
* [Database Roles](https://docs.snowflake.com/en/user-guide/security-access-control-overview#database-roles)
* [Object Tagging](https://docs.snowflake.com/en/user-guide/object-tagging)