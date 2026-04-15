In this step, you will create the destination database and schema where the Jira connector will write issue data. The connector auto-creates the destination table on first run — no manual table creation is needed.

**Account Context:** Execute from your Snowflake account using ACCOUNTADMIN or SYSADMIN.

## Why is this important?

The connector's SnowflakeConnectionService writes data using a MERGE operation into a target table. The database and schema must exist before the connector starts, but the table itself is auto-provisioned by the connector.

## Key Concepts

**Auto-Created Table**
The connector creates `{{ dest_table }}` (or whatever table name you configure) automatically on its first run. The schema must exist, but the table must not be manually pre-created as the connector manages its own DDL.

**More Information:**
* [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database)
* [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema)

### Configuration Questions

#### What database should store Jira issues? (`dest_db`: text)
The Snowflake database where Jira issue data will land.

**Default:** `JIRA_DB`

#### What schema should store Jira issues? (`dest_schema`: text)
The schema within `dest_db` where the Jira connector will write data.

**Default:** `JIRA_SCHEMA`

#### What table name should the connector write to? (`dest_table`: text)
The table name that the connector will auto-create and write Jira issues into.

**Default:** `JIRA_ISSUES`
