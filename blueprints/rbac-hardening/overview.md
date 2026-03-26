# RBAC Hardening

Audit, harden, and monitor role-based access controls across your Snowflake account

This repeatable workflow guides you through auditing, hardening, and monitoring role-based access controls (RBAC) in your Snowflake account. It complements the initial role hierarchy created by Data Product Setup by filling operational gaps: assigning users to functional roles, restricting over-privileged system roles, revoking stale access, and establishing ongoing monitoring.

**What You Will Do:**
- **Audit**: Visualize your role hierarchy, discover PUBLIC exposure, find over-privileged users, and detect stale access
- **Harden**: Revoke unnecessary PUBLIC grants, restrict ACCOUNTADMIN to break-glass only, eliminate direct user privileges, and enforce managed access schemas
- **Provision**: Assign end users to functional roles and configure least-privilege service accounts
- **Monitor**: Create governance views, privilege-change alerts, and compliance review documentation

**Key Features:**
- Works with existing Data Product Setup role hierarchies
- Generates review-before-execute SQL (safe dry-run pattern)
- Supports both full-account and per-data-product scope
- SCIM-aware for environments using identity provider integration

Run this workflow periodically to maintain RBAC hygiene as your account evolves.

