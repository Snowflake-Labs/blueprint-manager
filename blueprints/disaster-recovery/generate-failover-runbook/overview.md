This step produces a complete operational runbook document covering the full DR lifecycle: event declaration, Snowflake failover procedures, manual steps outside Snowflake, replication exceptions, validation checklists, failback, and communication templates.

## Why is this important?

- A runbook that exists only in people's heads will fail when those people are unavailable or under stress during an actual outage
- Replication exceptions (TSS, MFA, external tables, PrivateLink) require pre-planned manual steps that must be documented before an event occurs
- Communication templates prevent delayed or inconsistent notifications during a high-stress DR event
- The runbook is a living document that improves with each drill — version control it alongside your infrastructure code

## Prerequisites

- DR Implementation completed (Task 2)
- Organizational context collected (step 4.1)
- RACI matrix generated (step 4.2)

## Key Concepts

- **Runbook**: A step-by-step operational document that can be followed during an actual DR event or drill without requiring deep technical expertise.
- **Replication Exceptions**: Objects and settings that do NOT automatically transfer during failover (external tables, event tables, PrivateLink, MFA enrollment).
- **Communication Plan**: Pre-written templates for notifying stakeholders at each phase of a DR event.

## What Gets Generated

| Section | Contents |
|---------|----------|
| Event Declaration | Trigger criteria, escalation path |
| Failover Steps | SQL procedures for promotion and redirect |
| Manual Steps | ETL/BI repointing, non-Snowflake actions |
| Exceptions | Objects requiring manual recreation |
| Validation Checklist | Post-failover verification items |
| Failback Procedure | Steps to restore original primary |
| Communication Plan | Email/notification templates |

## Replication Exceptions — Security-Critical Items

The following exceptions have security or compliance implications and require proactive preparation **before** executing a failover or drill:

| Exception | Impact | Remediation |
|-----------|--------|-------------|
| **Customer-Managed Keys (CMK) / Tri-Secret Secure** | TSS configuration does NOT replicate. The target account silently reverts to Snowflake-managed encryption post-failover. Critical regression for regulated industries (HIPAA, PCI-DSS, FedRAMP). | Pre-configure TSS on the target account independently before conducting any failover drill. Verify with `SHOW PARAMETERS LIKE 'CUSTOMER_MANAGED_KEY' IN ACCOUNT;` on the target. |
| **MFA device enrollment** | User MFA device registrations do not replicate. Users authenticating on the target post-failover will not have MFA enabled unless handled proactively. | Pre-enroll users on the target account, or enforce MFA at the network policy level on the target before failover. Include MFA re-enrollment in the RTO window if pre-enrollment is not feasible. |
| **External tables** | External table definitions replicate, but the underlying cloud storage event notifications do not. | Manually reconnect event notifications (SQS/SNS/Event Grid) on the target post-failover. |
| **Event tables** | Event table data and telemetry configuration do not replicate. | Recreate telemetry configuration on target post-failover. |
| **Hybrid tables** | Hybrid tables are not supported in failover groups. | These must be managed outside the DR scope; consult Snowflake Support. |
| **Databases from inbound shares** | Imported databases from providers cannot be replicated. | Request a new share from the provider targeting the DR account before failover. |
| **PrivateLink / Private Connectivity** | Private Link endpoints are account-specific and do not replicate. | Pre-configure Private Link on the target account before any failover. |

## Considerations

> **Note**: Store the runbook in version control and review it quarterly. Test it during DR drills (Task 3) to identify gaps or outdated procedures.

**More Information:**
* [ALTER FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/alter-failover-group) — Failover and failback SQL reference
* [Client Redirect](https://docs.snowflake.com/en/user-guide/client-redirect) — Connection failover during DR events
* [Replication Considerations](https://docs.snowflake.com/en/user-guide/account-replication-considerations) — Objects not replicated


### Configuration Questions

#### What name suffix should be used for failover group objects? (`dr_failover_group_name`: text)
**What is this asking?**
Provide a name for the failover group and related objects. This will be used
as the identifier for the failover group, connection objects, etc.

**Connection naming:** This value also determines the client redirect connection
name: `{name}_CONN`. For example, `PROD_DR` produces a connection named
`PROD_DR_CONN`. Choose a name that is meaningful in both the failover group
and connection string contexts — your application teams will reference the
connection URL by this name.

**Naming Guidelines:**
- Use uppercase letters, numbers, and underscores
- Keep it short but descriptive
- Common patterns: `DR`, `PROD_DR`, `CRITICAL_DR`

**Examples:**
- `DR` — Simple, for a single failover group (connection: `DR_CONN`)
- `PROD_DR` — For production tier (connection: `PROD_DR_CONN`)
- `CRITICAL_DR` — For critical-tier databases with tight RPO (connection: `CRITICAL_DR_CONN`)


#### Do you want to enable client redirect for transparent failover? (`dr_enable_client_redirect`: single-select)
**What is this asking?**
Client redirect creates a stable connection URL that automatically points to
whichever account is currently primary. Applications using this URL are
transparently redirected during failover without connection string changes.

**Select "Yes" to:**
- Create a connection object with a stable URL
- Enable automatic client redirection during failover
- Reduce manual intervention needed during DR events

**Select "No" if:**
- You prefer manual connection string management
- Your applications already handle multi-account connections
- You're using DNS CNAME-based routing

**Recommendation:** Yes for production environments. It significantly
reduces RTO by eliminating manual connection string updates.

**Options:**
- Yes
- No

#### What is the target DR account name? (`dr_target_account`: text)
**What is this asking?**
Provide the Snowflake account name for your DR target. This is the account
in a different region that will receive replicated data and serve as your
failover destination.

**Format:**
Use the account name only (not the full URL). Example: `MY_DR_ACCOUNT`

**Requirements:**
- Must be in the same Snowflake organization as the source account
- Should be in a different region (for geographic redundancy)
- Must be Business Critical Edition or higher for failover groups

**How to find it:**
Run `SHOW REPLICATION ACCOUNTS;` on the source to list all accounts in your org.


#### Who has authority to declare a DR event? (`dr_event_approver`: text)
**What is this asking?**
The role or person with authority to declare a disaster recovery event,
authorizing failover and stakeholder notification.

**Examples:**
- `VP Engineering`
- `CTO`
- `Director of Data Platform`
- `Head of Infrastructure`

**Note:** This person is the single "Accountable" party in the RACI matrix
for DR event declaration.


#### What communication channel is used for incident notifications? (`dr_communication_channel`: text)
**What is this asking?**
The primary channel where DR event notifications and updates are sent.

**Examples:**
- `#incident` (Slack channel)
- `#data-platform-alerts` (Slack)
- `PagerDuty` (alerting tool)
- `data-incidents@company.com` (email DL)
- `MS Teams - Incidents` (Teams channel)


#### What is your target RTO (Recovery Time Objective) in minutes? (`dr_rto_target`: text)
**What is this asking?**
RTO defines the maximum acceptable downtime during a disaster. A 30-minute
RTO means services must be restored within 30 minutes of a declared event.

**Common Values:**
- `15` — Aggressive (requires client redirect and minimal manual steps)
- `30` — Standard for business-critical systems
- `60` — Acceptable with some manual intervention
- `240` — 4 hours, typical for non-critical systems

**Components of RTO:**
- Failover promotion time (~1-5 minutes)
- Client redirect (~instant if configured)
- Warehouse resume (seconds per warehouse)
- Manual steps (ETL/BI repointing, if needed)

**Note:** Client redirect significantly reduces RTO by eliminating manual
connection string changes.


#### What is your target RPO (Recovery Point Objective) in minutes? (`dr_rpo_target`: text)
**What is this asking?**
RPO defines the maximum acceptable data loss during a disaster, measured in
time. A 10-minute RPO means you accept losing up to 10 minutes of data.

**Common Values:**
- `5` — Near-zero data loss (aggressive, higher replication cost)
- `10` — Standard for critical business data
- `30` — Acceptable for most analytical workloads
- `60` — Standard for non-critical or batch-oriented data

**Relationship to Replication Frequency:**
Your replication frequency should be equal to or less than your RPO target.
Example: 10-minute RPO requires at least 10-minute replication frequency.

