In this step, you will create the External Access Integration (EAI) that authorizes the Openflow runtime to use the Jira network rule. The EAI must exist before it can be attached to the runtime.

**Account Context:** Execute from your Snowflake account using ACCOUNTADMIN.

## Why is this important?

Snowflake SPCS runtimes are isolated by default. An External Access Integration explicitly grants a runtime permission to make outbound network calls to the hosts defined in the associated network rule. Without the EAI, the Jira connector cannot reach Atlassian's APIs regardless of what the network rule allows.

## Key Concepts

**EAI Attachment**
Creating the EAI in SQL is only the first half. After this step, you must attach the EAI to your specific Openflow runtime via the Control Plane UI (covered in step 7). The SQL creation and the UI attachment are separate operations.

**More Information:**
* [CREATE EXTERNAL ACCESS INTEGRATION](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration)

### Configuration Questions

This step has no additional configuration questions. It uses the `rule_db` and `rule_schema` values from the previous step to reference `JIRA_NETWORK_RULE`.
