This step identifies databases and objects not protected by replication, as well as items that cannot be automatically replicated by Snowflake.

## Why is this important?

- Unprotected databases are invisible to DR — if they exist, a failover event would result in complete data loss for those systems
- Replication exceptions (external tables, event tables, hybrid tables) require manual recreation scripts that must be ready before an outage
- Identifying pipeline objects (Snowpipe, external stages) that need pre-configuration prevents discovery of these gaps during an actual DR event
- Non-Snowflake dependencies (ETL tools, BI platforms) must be inventoried now so their repointing procedures can be included in the runbook

## Prerequisites

- ACCOUNTADMIN role access
- DR Assessment steps 1.1–1.3 completed (edition confirmed, existing groups audited)

## Key Concepts

- **Coverage Gap**: A critical database or object that is not included in any replication or failover group.
- **Replication Exceptions**: Objects that Snowflake cannot replicate automatically (external tables, event tables, hybrid tables, imported databases from shares).
- **Non-Snowflake Dependencies**: ETL tools, BI platforms, and applications with hardcoded connection strings that must be manually repointed during failover.

## What Gets Identified

| Category | Examples |
|----------|----------|
| Unprotected databases | Databases not in any failover group |
| Non-replicable objects | External tables, event tables, hybrid tables |
| Imported databases | Databases from inbound shares (provider must re-share to target) |
| External dependencies | ETL tools, BI tools, apps with direct account connections |

## Pipeline Object DR Requirements

Data pipeline objects require additional pre-failover preparation beyond standard failover group configuration:

**Snowpipe (auto-ingest pipes):**
- Pipe objects and load history metadata replicate with the database.
- However, event notification bindings (SQS queue subscriptions to SNS topics or S3 event notifications) are cloud-account-specific and do **not** replicate automatically.
- Before failover: configure notifications for the secondary pipe's SQS queue in the target account to subscribe to the same SNS topic as the source. See [Configure notifications for secondary auto-ingest pipes](https://docs.snowflake.com/en/user-guide/account-replication-stages-pipes-load-history).

**External stages with storage integrations:**
- External stages replicate when the database is in the failover group.
- The storage integration object itself replicates only if `STORAGE INTEGRATIONS` is in `ALLOWED_INTEGRATION_TYPES` (see step 2.2).
- The cloud IAM trust policy on the storage integration does **not** update automatically — the target account has a different Snowflake IAM identity.
- Before failover: run `DESC INTEGRATION <storage_integration>` on the target to get its IAM principal, then update the cloud-provider trust policy (S3 bucket policy, Azure SAS, GCS service account) to grant access.

**External stages without storage integrations (credential-based):**
- Stages with embedded credentials or access tokens replicate, but credentials may be account-scoped.
- Verify post-failover that stages can reach cloud storage before routing traffic.

**File formats:**
- Replicate automatically as part of database objects when the database is in the failover group. No additional action required.

## Considerations

> **Note**: Objects that cannot be replicated require manual remediation scripts. These should be documented in your DR runbook (Task 4) and tested during DR drills (Task 3).

**More Information:**
* [Replication Considerations](https://docs.snowflake.com/en/user-guide/account-replication-considerations) — Supported objects and exceptions
* [Stage, Pipe, and Load History Replication](https://docs.snowflake.com/en/user-guide/account-replication-stages-pipes-load-history) — Pipeline object DR guide


### Configuration Questions

#### Which databases should be included in the failover group? (`dr_databases`: list)
**What is this asking?**
List the databases to include in the failover group. Only standard databases
can be replicated — imported databases (from shares), system databases, and
application packages are excluded automatically.

**Format:**
Enter each database name on a separate line.

**Examples:**
```
ANALYTICS_DB
SALES_DB
CUSTOMER_DB
WAREHOUSE_DB
```

**Note:** If you want ALL standard databases, leave this list empty and the
blueprint will include all eligible databases.

