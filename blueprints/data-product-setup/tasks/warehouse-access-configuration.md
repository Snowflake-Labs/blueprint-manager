# Warehouse & Access Configuration

## Summary
Create warehouses for each workload type, create warehouse access roles for
controlled compute access, transfer ownership to admin roles, and wire the
complete role hierarchy connecting account roles to warehouse access.

## External Requirements
- Task 2 (Core Roles & Database Setup) completed
- warehouse_definitions from Task 1
- Core roles created (ADMIN, CREATE, WRITE, RBAC, READ)
- Databases and schemas with database roles

## Personas
- Platform Administrator
- Data Team

## Role Requirements
- SYSADMIN role
- USERADMIN role
- SECURITYADMIN role

## Details
## **Understanding Snowflake Warehouses**

In Snowflake, a **warehouse** is a cluster of compute resources — **not storage**. This is different from traditional databases where "warehouse" typically means a data warehouse (storage).

**Key implications:**
- **Scale independently**: Add more compute without moving data
- **Workload isolation**: Heavy ETL doesn't slow down BI dashboards
- **Pay per use**: Warehouses auto-suspend when idle
- **Multiple simultaneous**: Different teams use different warehouses on the same data

## **Warehouse Sizing**

| Size | Credits/Hour | Use Case |
|------|--------------|----------|
| X-Small | 1 | Light queries, development |
| Small | 2 | Ad-hoc analysis, small loads |
| Medium | 4 | Standard workloads |
| Large | 8 | Heavy transformations |
| X-Large | 16 | Large data processing |

## **Steps in This Task**

| Step | Title | Purpose |
|------|-------|---------|
| 3.1 | Create Warehouses | Create workload-specific warehouses with appropriate sizing |
| 3.2 | Create Warehouse Access Roles | Create `_WH_U_*` roles for warehouse usage |
| 3.3 | Transfer Ownership & Wire Hierarchy | Transfer ownership and complete role wiring |

**From Task 1:**
- `warehouse_definitions` — Warehouse specs (workload, size, timeout)

**From Task 2:**
- Core roles created (ADMIN, CREATE, WRITE, RBAC, READ)
- Databases and schemas with database roles

## **Warehouse Architecture**

```
Warehouse: <prefix>_<WORKLOAD>
├── Owner: <dataproduct>_ADMIN
├── Access Role: _WH_U_<prefix>_<WORKLOAD>
│   ├── Grants: USAGE, MONITOR
│   └── Owner: <dataproduct>_RBAC
└── Properties:
    ├── Size: (configured per workload)
    ├── Auto Suspend: 60 seconds
    └── Auto Resume: TRUE
```

## **Deliverables**

Upon completing this task, you will have:
- ✅ Warehouses created for each workload type
- ✅ Warehouse access roles created and configured
- ✅ Ownership transferred to ADMIN/RBAC roles
- ✅ Complete role hierarchy from account → database → schema → warehouse

## **More Information**

* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse)
* [Warehouse Considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations)
* [Role Hierarchy](https://docs.snowflake.com/en/user-guide/security-access-control-overview#role-hierarchy-and-privilege-inheritance)