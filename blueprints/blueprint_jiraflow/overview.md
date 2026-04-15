# Openflow Jira Cloud Connector Setup

Deploy and configure the Snowflake Openflow Jira Cloud connector on an SPCS runtime to sync Jira issues into Snowflake.

This workflow guides you through setting up the Jira Cloud connector on a Snowflake Openflow SPCS runtime. The connector uses `SNOWFLAKE_MANAGED` authentication — no key pair or private key configuration required.

By the end of this workflow, Jira issues will be flowing into your Snowflake table automatically, merged on a 5-minute schedule.

**Prerequisites**:
- Snowflake Openflow deployed on an SPCS runtime
- nipyapi CLI installed: `uv tool install "nipyapi[cli]>=1.2.0"`
- Snow CLI configured with a working connection
- A Jira Cloud instance with API token access
