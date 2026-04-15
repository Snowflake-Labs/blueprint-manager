In this step, you will create a Snowflake Network Rule that allows the Openflow Jira connector to reach the Jira Cloud API endpoints. This rule is required before creating the External Access Integration.

**Account Context:** Execute from your Snowflake account using ACCOUNTADMIN.

## Why is this important?

Openflow SPCS runtimes run inside Snowflake's infrastructure and cannot make outbound network calls without an External Access Integration backed by a Network Rule. The Jira connector needs to reach two Atlassian hosts — both must be included or the connector will fail validation.

## Key Concepts

**Both Atlassian hosts are required**
The connector uses the Jira instance URL (`yourorg.atlassian.net`) to look up the Jira Cloud ID, then routes all actual API calls through `api.atlassian.com`. If either host is missing from the network rule, the `Jira Connection` controller service will fail.

**Network Rule Scope**
The rule is created in a specific database and schema. Choose a schema used for security/governance objects. The rule is then referenced by the External Access Integration.

**More Information:**
* [CREATE NETWORK RULE](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule)
* [External Access Overview](https://docs.snowflake.com/en/developer-guide/external-network-access/external-network-access-overview)

### Configuration Questions

#### What database should contain the network rule? (`rule_db`: text)
The database where the `JIRA_NETWORK_RULE` network rule object will be created.

**Recommendation:** Use an existing security or governance database (e.g., `SECURITY`, `GOVERNANCE`, `PLATFORM`).

#### What schema should contain the network rule? (`rule_schema`: text)
The schema within `rule_db` where the `JIRA_NETWORK_RULE` will be created.

**Recommendation:** Use `PUBLIC` or a dedicated policies/security schema.
