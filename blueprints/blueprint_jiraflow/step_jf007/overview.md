In this step, you will attach the `JIRA_EAI` External Access Integration to your Openflow SPCS runtime via the Control Plane UI. This is a required UI operation — there is no SQL or CLI command for this.

## Why is this important?

Creating the EAI in SQL makes it available in your Snowflake account, but the Openflow runtime does not use it until it is explicitly associated with that specific runtime in the Control Plane. Without this attachment, the Jira connector cannot make outbound API calls to Atlassian.

## Key Concepts

**Runtime Restart**
Attaching an EAI causes the runtime to restart. This is expected — the restart applies the new network configuration. Wait for the runtime to return to a running state before deploying the connector.

### Configuration Questions

This step has no configuration questions. It requires only clicking through the Openflow Control Plane UI to associate `JIRA_EAI` with your runtime.
