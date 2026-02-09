# Data Product Setup

Configure a complete data product with databases, roles, warehouses, and cost controls

This repeatable workflow guides you through configuring a complete data product in Snowflake. A Data Product is a self-contained, governed unit of data with clear ownership, dedicated resources, and well-defined access controls.

**What You Will Create:**
- **Core Roles**: ADMIN, CREATE, WRITE, RBAC, READ roles with proper hierarchy
- **Databases**: Zone-based databases (RAW, TRANSFORM, CURATED)
- **Schemas**: Organized by source system or subject area within each zone
- **Database Roles**: Granular access control (DB_R, DB_W, DB_C, SC_R, SC_W, SC_C)
- **Warehouses**: Workload-specific compute (INGEST, TRANSFORM, QUERY, BI)
- **Resource Monitors**: Credit quotas and alerts for cost management

**Key Features:**
- Supports both SCIM and non-SCIM deployments
- Flexible zone structure (medallion architecture)
- Tag-based governance and cost allocation
- Delegated administration through RBAC role

Run this workflow once for each data product you need to deploy.

