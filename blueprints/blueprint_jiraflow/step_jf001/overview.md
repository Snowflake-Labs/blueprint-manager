In this step, you will confirm the prerequisites needed to run the Jira Cloud connector blueprint: a working nipyapi CLI, a configured nipyapi profile pointing to your Openflow SPCS runtime, and a Snow CLI connection.

**Account Context:** All SQL steps in this workflow should be executed from your Snowflake account using a role with sufficient privileges (ACCOUNTADMIN or equivalent).

## Why is this important?

The nipyapi CLI is used to deploy the Jira connector, configure its parameter context, enable controller services, and start the flow. Without a valid nipyapi profile pointing to your runtime, subsequent steps cannot be executed.

## Prerequisites

- nipyapi CLI installed: `uv tool install "nipyapi[cli]>=1.2.0"`
- A Personal Access Token (PAT) generated from Snowflake UI (Openflow SPCS rejects JWT session tokens)
- Snow CLI configured with a working connection

## Key Concepts

**nipyapi Profile**
A named entry in `~/.nipyapi/profiles.yml` that stores the NiFi API URL and PAT for a specific runtime. All nipyapi commands use `--profile <name>` to target the correct runtime.

**SPCS vs BYOC**
This blueprint is designed for SPCS (Snowpark Container Services) deployments. SPCS runtimes use `SNOWFLAKE_MANAGED` authentication and require External Access Integrations for outbound network access. BYOC deployments use key-pair auth and have direct network access.

**Personal Access Token (PAT)**
Generate from Snowflake UI under your user profile → Security → Personal Access Tokens. Do not use session tokens — SPCS runtimes reject them with a 401 error.

### Configuration Questions

#### What is your nipyapi profile name? (`nipyapi_profile`: text)
The name of the nipyapi profile in `~/.nipyapi/profiles.yml` that points to your Openflow SPCS runtime.

**How to find it:**
```bash
grep -E "^[a-zA-Z].*:$" ~/.nipyapi/profiles.yml | tr -d ':'
```

**How to create one** (if it doesn't exist yet):
```yaml
# ~/.nipyapi/profiles.yml
<profile_name>:
  nifi_url: https://of--<account>.snowflakecomputing.app/<runtime_name>/nifi-api
  nifi_bearer_token: <personal_access_token>
```
