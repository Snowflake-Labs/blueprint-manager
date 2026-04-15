In this step, you will enable all controller services for the Jira connector process group, verify the configuration, and start the flow.

## Why is this important?

NiFi controller services must be enabled before processors can use them. The Jira connector includes a `SnowflakeConnectionService`, a `JiraConnectionService`, and two Private Key Services. With `SNOWFLAKE_MANAGED` auth, the two Private Key Services are not used and will always fail validation — this is expected and should be ignored.

## Key Concepts

**Expected Verification Result**
`ci verify_config` should report **29/31 passed**. The 2 failures are always the `Forge Private Key Service` and `Snowflake Private Key Service` controllers, which require private key configuration that is not needed for `SNOWFLAKE_MANAGED` auth.

**Ingestion Schedule**
The connector fetches on a 5-minute timer by default. Data appears in Snowflake within approximately 10 minutes of starting (one fetch cycle + one merge buffer flush).

**Merge Strategy**
The connector uses a full re-fetch + MERGE approach: all issues in the specified project(s) are re-fetched each cycle, and the MERGE operation inserts new issues and updates changed ones. There are no duplicates.

### Configuration Questions

This step uses `nipyapi_profile`, `dest_db`, `dest_schema`, and `dest_table` from previous steps. No additional questions.
