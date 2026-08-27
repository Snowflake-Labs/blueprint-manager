This step restores the original source account as primary by syncing changes made during the drill, then promoting it back. Completes the full drill cycle.

## Why is this important?

- Completing failback restores normal operations and resets the DR topology for the next event
- Syncing changes before failback ensures no data written to the temporary primary is lost
- A drill that doesn't include failback is incomplete — you won't know your actual failback RTO until you've practiced it
- The post-drill retrospective captures lessons learned before they're forgotten, improving the runbook for the next event

## Prerequisites

- ACCOUNTADMIN role access on the original source account (now secondary)
- Validation on new primary complete (step 3.3)
- Stakeholders notified that failback is beginning

## Key Concepts

- **Failback**: The reverse of failover — restoring the original account as primary after a drill or outage resolution.
- **Sync Before Failback**: Any data changes made on the DR target during the drill must be replicated back to the original primary before re-promotion.
- **Resume Schedule**: After failback, the normal replication schedule resumes from source to target.

## What Happens

| Action | Effect |
|--------|--------|
| Resume replication on original | Allow it to receive updates from current primary |
| Trigger refresh | Sync changes back to original |
| Suspend before promote | Stop replication on original before promotion |
| Promote original back | Restore original as primary |
| Redirect clients back | Point connection URL to original account |
| Resume schedule | Normal replication resumes |

## Post-Drill Retrospective

After completing failback, record the drill results while they are fresh. File this in your runbook (Task 4) and address action items before the next drill.

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| RTO achieved | _(from dr_rto_target)_ min | ___ min | Pass / Fail |
| RPO at failover | _(from dr_rpo_target)_ min | ___ min | Pass / Fail |
| Governance policies verified | All policies active | ___ | Pass / Fail |
| Non-replicated objects recreated | All listed exceptions handled | ___ | Pass / Fail |
| Issues encountered | — | ___ | — |
| Runbook gaps identified | — | ___ | — |
| Action items before next drill | — | ___ | — |

Update the runbook in Task 4 with any gaps found, and schedule remediation before the next drill.

**More Information:**
* [ALTER FAILOVER GROUP](https://docs.snowflake.com/en/sql-reference/sql/alter-failover-group) — Failback and replication resume syntax
* [Failover and Failback](https://docs.snowflake.com/en/user-guide/account-replication-failover-groups) — Full lifecycle documentation


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
