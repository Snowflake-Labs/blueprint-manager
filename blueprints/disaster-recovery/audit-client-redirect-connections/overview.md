This step checks whether client redirect connections are configured for transparent failover. Client redirect allows Snowflake clients to automatically connect to the promoted account without application-level connection string changes.

## Why is this important?

- Without client redirect, every application connection string must be manually updated during a DR event, adding minutes to RTO
- Transparent failover is only possible if connection objects are pre-configured on both accounts before an outage
- Auditing existing connections reveals whether prior DR configuration was partial or complete
- Client redirect is Business Critical Edition only — confirming its presence (or absence) guides the implementation plan

## Prerequisites

- ACCOUNTADMIN role access
- DR Assessment step 1.1 (Check Account Edition) completed — confirms Business Critical Edition

## Key Concepts

- **Connection Object**: A named object that provides a stable connection URL. During failover, the URL transparently redirects to the new primary.
- **Primary Connection**: The active connection object (on the current primary account)
- **Secondary Connection**: The replica connection on the target account, ready to be promoted

## What Gets Checked

| Item | Purpose |
|------|---------|
| Connection objects | Whether any client redirect connections exist |
| Primary/secondary status | Which account currently owns each connection |
| Connection URL | The stable URL that clients should use |

## Considerations

> **Note**: Client redirect is the preferred approach for transparent failover. Without it, all application connection strings must be manually updated during a DR event. Client redirect requires Business Critical Edition.

**More Information:**
* [Client Redirect](https://docs.snowflake.com/en/user-guide/client-redirect) — Overview and configuration guide
* [CREATE CONNECTION](https://docs.snowflake.com/en/sql-reference/sql/create-connection) — SQL reference
