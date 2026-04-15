In this step, you will grant the Openflow runtime role all privileges needed to operate the Jira connector: access to the destination database and schema, the ability to create and modify tables, usage on the warehouse, and usage on the External Access Integration.

**Account Context:** Execute from your Snowflake account using ACCOUNTADMIN.

## Why is this important?

The Openflow runtime operates under its own Snowflake role. Without the correct grants, the connector will fail when attempting to create the destination table, insert data, or use the warehouse.

## Key Concepts

**Runtime Role**
Find the runtime role by running `SHOW ROLES LIKE '%OPENFLOW%';` in Snowflake. It typically follows the pattern `OPENFLOW_RUNTIME_ROLE_SPCS_<runtime_name>` or similar.

**FUTURE TABLES Grant**
The connector auto-creates the destination table on first run. The `GRANT ... ON FUTURE TABLES` ensures the runtime role can write to that table immediately after creation without requiring a manual re-grant.

**EAI Grant**
The runtime role must have `USAGE` on `JIRA_EAI` to route outbound network traffic through the External Access Integration.

**More Information:**
* [GRANT Privilege](https://docs.snowflake.com/en/sql-reference/sql/grant-privilege)

### Configuration Questions

#### What is the Openflow runtime role name? (`runtime_role`: text)
The Snowflake role under which the Openflow SPCS runtime operates.

**How to find it:**
```sql
SHOW ROLES LIKE '%OPENFLOW%';
```

Look for a role named `OPENFLOW_RUNTIME_ROLE_SPCS_<runtime_name>` or similar.
