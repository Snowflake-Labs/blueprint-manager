In this step, you will create an XSMALL warehouse for the Jira connector to use when writing data to Snowflake via the SnowflakeConnectionService controller.

**Account Context:** Execute from your Snowflake account using ACCOUNTADMIN or SYSADMIN.

## Why is this important?

The Openflow Jira connector uses a SnowflakeConnectionService to write data. This controller requires a warehouse. Using a dedicated XSMALL warehouse with auto-suspend keeps costs low while ensuring the connector always has compute available.

## Key Concepts

**Auto Suspend**
Set to 60 seconds so the warehouse suspends quickly after each merge batch, minimizing credit consumption.

**Auto Resume**
Must be TRUE so the connector can wake the warehouse without manual intervention.

**More Information:**
* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse)

### Configuration Questions

#### What name should be used for the Jira warehouse? (`warehouse_name`: text)
The name of the warehouse that the Jira connector will use.

**Recommendation:** `JIRA_WH` — clearly identifies it as Jira-specific.

**Alternative:** Use a shared integration warehouse if one exists (e.g., `OPENFLOW_WH`).
