# Data Product Planning

## Summary
Select the target Snowflake account for deployment, define the data product's name,
domain, environment, and SCIM configuration, plan zone structure and schemas,
and define warehouse requirements for different workloads.

## External Requirements
- Platform Foundation Setup completed
- Target account exists and is accessible

## Personas
- Data Team
- Platform Team
- Data Architecture Team

## Role Requirements
- SYSADMIN role access in the target account

## Details
This is a **repeatable workflow** — run it once for each data product you need to configure.

## **What is a Data Product?**

A **Data Product** is a self-contained, governed unit of data with clear ownership, dedicated resources, and well-defined access controls. Instead of a monolithic data warehouse with unclear ownership, data products organize data by business domain with:

- **Own databases** organized by processing stage (raw → transformed → curated)
- **Own compute** (warehouses) sized for specific workloads
- **Own access controls** with delegated administration
- **Clear team ownership** and cost accountability

## **Steps in This Task**

| Step | Title | Purpose | Conditional |
|------|-------|---------|-------------|
| 1.1 | Select Target Account | Identify which account to deploy to | Multi-account strategies only |
| 1.2 | Define Data Product Identity | Name, domain, environment, SCIM prefix | Always shown |
| 1.3 | Configure Zone Structure | Define data zones (raw, curated, pub) | Always shown |
| 1.4 | Plan Schema Organization | Define schemas within each zone | Always shown |
| 1.5 | Plan Warehouse Requirements | Define compute resources and workload types | Always shown |

**From Platform Foundation (inherited):**
- `account_strategy` — Single or multi-account approach
- `domain_list` — Available business domains
- `environment_list` — Available SDLC environments
- `platform_database_name` — Infrastructure database name
- `governance_name` — Governance schema name

## **Key Decisions**

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Target Account | Platform Team | Where resources are created |
| Data Product Name | Data Team/Platform Team | Permanent identifier in all object names |
| Domain Assignment | Business/Platform Team | Cost allocation and governance |
| Environment | Platform Team | Determines isolation level |
| SCIM Prefix | Platform/Security Team | Role ownership and user assignment method |
| Zone Structure | Data Architecture Team | Data flow and organization |
| Warehouse Sizing | Platform/Data Team | Performance and cost |

## **Deliverables**

Upon completing this task, you will have:
- ✅ Target account identified and documented
- ✅ Data product identity defined (name, domain, environment)
- ✅ SCIM configuration determined (prefix or NONE)
- ✅ Zone structure planned
- ✅ Schemas organized by zone and purpose
- ✅ Warehouse requirements defined by workload type

## **More Information**

* [Snowflake Object Hierarchy](https://docs.snowflake.com/en/user-guide/databases) — Database and schema concepts
* [Database Design Best Practices](https://docs.snowflake.com/en/user-guide/databases-best-practices) — Database organization
* [Warehouse Considerations](https://docs.snowflake.com/en/user-guide/warehouses-considerations) — Sizing and configuration
* [SCIM Provisioning](https://docs.snowflake.com/en/user-guide/scim) — Identity provider integration