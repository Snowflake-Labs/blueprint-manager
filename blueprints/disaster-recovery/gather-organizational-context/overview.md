This step collects information about your team structure, tools, and incident management processes to populate the DR runbook with organization-specific details.

## Why is this important?

- A runbook that references real team names, approvers, and channels is actionable during an actual DR event — a generic template is not
- Identifying the single accountable approver (the person who can declare a DR event) prevents decision paralysis during an outage
- Documenting communication channels ensures notifications reach the right people at the right time
- This context flows directly into the RACI matrix (step 4.2) and full runbook (step 4.3)

## Prerequisites

- DR Implementation completed (Task 2)
- Knowledge of your team structure, incident management tools, and on-call processes

## Key Concepts

- **On-Call Team**: The team responsible for monitoring Snowflake and initiating DR events.
- **DR Event Approver**: The authority who declares a DR event (e.g., VP Engineering, CTO).
- **Communication Channels**: Where incident notifications are sent (Slack, PagerDuty, email).

## What Gets Collected

| Input | Purpose |
|-------|---------|
| Team name | Identifies the responsible organization |
| On-call team | Who monitors and responds first |
| ETL/BI tools | Tools requiring manual repointing |
| Communication channels | Where to send notifications |
| DR event approver | Who has authority to declare DR |
| RTO/RPO targets | Define acceptable thresholds |

**More Information:**
* [Failover Groups Overview](https://docs.snowflake.com/en/user-guide/account-replication-failover-groups) — DR event management context


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


#### What is the primary team responsible for Snowflake operations? (`dr_team_name`: text)
**What is this asking?**
The name of the team that owns Snowflake platform operations and would be
responsible for executing DR procedures.

**Examples:**
- `Data Platform Team`
- `Cloud Infrastructure Team`
- `Data Engineering`
- `SRE Team`


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

