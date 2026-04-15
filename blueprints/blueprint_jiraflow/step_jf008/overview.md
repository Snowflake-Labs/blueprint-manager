In this step, you will deploy the Jira Cloud connector from the Snowflake Openflow Connector Registry to your runtime using the nipyapi CLI.

## Why is this important?

The Snowflake Openflow Connector Registry contains pre-built, versioned connector flows. Deploying via `nipyapi ci deploy_flow` provisions the Jira connector as a new process group in your runtime, ready for parameter configuration.

## Key Concepts

**Process Group ID**
After deployment, nipyapi returns a process group ID. Save this — you need it to configure parameters, enable controllers, and start the flow in subsequent steps.

**Snowflake Connector Registry**
The registry (`Snowflake Openflow Connector Registry`) is read-only and pre-provisioned. No registry client setup is required.

### Configuration Questions

This step uses the `nipyapi_profile` value from step 1. No additional questions.
