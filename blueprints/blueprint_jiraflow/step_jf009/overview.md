In this step, you will configure the Jira connector's parameter context with your Jira credentials and Snowflake destination settings using a Python script that calls the NiFi REST API directly.

## Why is this important?

nipyapi has known issues updating sensitive parameters (like API tokens) through its standard interface. The Python configure script uses direct HTTP calls to the NiFi parameter-context API, which correctly handles both sensitive and non-sensitive parameters in a single request.

## Key Concepts

**Jira API Token**
The API token is passed at script execution time via `--jira-token` and is never stored in the answers YAML file or committed to version control. Generate one at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens).

**Project Names — Simple Query**
The connector defaults to `SIMPLE` search type, which uses the `Project Names - Simple Query` parameter (not `Project Names`). Multiple projects can be comma-separated.

**SNOWFLAKE_MANAGED Auth**
Set `Authentication Strategy` to `SNOWFLAKE_MANAGED` for SPCS runtimes. This uses the runtime's Snowflake identity — no private key configuration required. The `Snowflake Role` must be set to the runtime's role (from step 6).

### Configuration Questions

#### What is the Jira instance URL? (`jira_url`: text)
Your Jira Cloud URL. Example: `https://yourorg.atlassian.net/`

#### What email is associated with the Jira API token? (`jira_email`: text)
The email address of the Atlassian account that owns the API token.

#### What Jira project key(s) should be synced? (`jira_project_keys`: text)
One or more Jira project keys to ingest. Comma-separate multiple projects.

**Example:** `PLAT` or `PLAT,SEC,OPS`
