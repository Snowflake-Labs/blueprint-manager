In this step, you will query the destination table to confirm that Jira issues are flowing into Snowflake successfully.

**Account Context:** Execute from your Snowflake account using any role with SELECT access on the destination schema.

## Why is this important?

The connector starts asynchronously. This validation step confirms the end-to-end pipeline is working: the Jira API is reachable, the connector is fetching issues, and the SnowflakeConnectionService is merging data into the destination table.

## Expected Results

- `{{ dest_db }}.{{ dest_schema }}.{{ dest_table }}` exists and has rows
- Issues have populated `ISSUE_KEY`, `PROJECT_KEY`, and a nested `ISSUE` VARIANT column
- `updated_at` timestamps match recent Jira activity

## Timing

Allow up to **10 minutes** after starting the flow before the first data appears. The connector fetches on a 5-minute timer, and the merge buffer flushes at 1,000 records or after 5 minutes, whichever comes first.

## Key Concepts

**ISSUE Column**
The raw Jira issue is stored as a VARIANT column named `ISSUE`. All Jira fields are accessible via dot notation or the `::TYPE` cast syntax (e.g., `ISSUE:fields:summary::STRING`).

### Configuration Questions

This step uses `dest_db`, `dest_schema`, `dest_table`, and `nipyapi_profile` from previous steps. No additional questions.
