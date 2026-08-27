# Disaster Recovery

Configure cross-region failover groups, client redirect, replication schedules, and validate DR readiness for Snowflake.

This blueprint guides you through implementing a complete Disaster Recovery (DR) strategy
for your Snowflake environment using failover groups, replication, and client redirect.

**What You Will Create:**
- Failover groups with automated replication schedules
- Client redirect connections for transparent failover
- DR drill scripts for planned failover/failback testing
- Operational runbook with RACI matrix and communication plans
- Cost estimation for replication, data transfer, and storage

**Prerequisites:**
- Business Critical Edition or higher (for failover groups and client redirect)
- At least one additional Snowflake account in a different region
- ACCOUNTADMIN role on both source and target accounts
- Source and target accounts in the same Snowflake organization

Run this blueprint once per DR target topology (e.g., once per target account/region pair).

