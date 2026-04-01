<!-- Author: Richie Bachala (richie.bachala@snowflake.com) -->
In this step, you'll configure Snowflake Alerts that automatically detect and notify your security team when RBAC-relevant changes occur. This provides real-time visibility into privilege modifications that could weaken your security posture.

**Account Context:** Execute from the target account with SYSADMIN role.

## Why is this important?

Even after hardening your RBAC configuration, changes can reintroduce vulnerabilities:
- A new user gets ACCOUNTADMIN during an emergency and it's never revoked
- A developer grants SELECT directly to a user for quick debugging
- A new warehouse gets USAGE granted to PUBLIC by mistake
- Dormant users retain active roles for months after leaving the team

Alerts provide automated detection so your security team can respond before these issues compound.

## Prerequisites

- Step 4.1 (RBAC Monitoring Views) completed — alerts reference these views
- Notification integration configured (e.g., email, Slack, PagerDuty)
- Monitoring warehouse provisioned
- SYSADMIN role access

## Key Concepts

**Snowflake Alerts**
| Property | Description |
|----------|-------------|
| WAREHOUSE | Compute used to run the alert condition check |
| SCHEDULE | CRON expression defining check frequency |
| IF (EXISTS (...)) | Condition that must be true to fire the alert |
| THEN | Action to take (send notification) |

**Alert Configuration**
| Alert | Frequency | Severity |
|-------|-----------|----------|
| New ACCOUNTADMIN Grant | Hourly | Critical |
| Direct User Grant | Every 6 hours | High |
| PUBLIC Role Grant | Every 6 hours | High |
| Dormant Users | Weekly | Medium |

**Notification Integration**
Alerts send notifications via `SYSTEM$SEND_NOTIFICATION()`. You must have a notification integration configured:
```sql
CREATE NOTIFICATION INTEGRATION my_notification
  TYPE = QUEUE
  NOTIFICATION_PROVIDER = <provider>
  ...;
```

## Best Practices

- Start with critical alerts (ACCOUNTADMIN) and expand gradually
- Tune alert frequency based on your team's response capacity
- Use separate notification channels for different severity levels
- Review alert history monthly to ensure alerts are firing correctly
- Suppress known-good patterns to reduce alert fatigue

## How to Test

1. After creating alerts, check `SHOW ALERTS` to confirm they're active
2. Trigger a test: grant ACCOUNTADMIN to a test user
3. Wait for the alert schedule to fire
4. Verify the notification was received
5. Revoke the test grant

## More Information

* [Snowflake Alerts](https://docs.snowflake.com/en/user-guide/alerts) — Alert documentation
* [SYSTEM$SEND_NOTIFICATION](https://docs.snowflake.com/en/sql-reference/stored-procedures/system_send_notification) — Notification function
* [Notification Integrations](https://docs.snowflake.com/en/sql-reference/sql/create-notification-integration) — Setup guide


### Configuration Questions

#### Do you want to configure alerts for privilege changes? (`rbac_enable_alerts`: single-select)
**What is this asking?**
Choose whether to create Snowflake alerts that monitor for suspicious
GRANT and REVOKE activity and notify your security team.

**Why does this matter?**
Privilege escalation is a common attack vector. Alerts can detect:
- New ACCOUNTADMIN grants
- Grants to/from PUBLIC role
- Bulk privilege changes (potential automation errors)
- Role hierarchy modifications

**Options explained:**
- **Yes**: Create alerts that check Account Usage views on a schedule
  and send notifications via your configured integration.
- **No**: Skip alert creation. Choose this if you use external SIEM
  tools for Snowflake monitoring.

**Prerequisites for Yes:**
- A notification integration must exist (email, Slack, webhook, etc.)
- A warehouse must be available for alert execution

**Recommendation:** Yes, unless you already have external monitoring
(e.g., Splunk, Datadog) consuming Snowflake audit logs.

**More Information:**
* [Snowflake Alerts](https://docs.snowflake.com/en/user-guide/alerts)
* [Notification Integrations](https://docs.snowflake.com/en/sql-reference/sql/create-notification-integration)

**Options:**
- Yes
- No

#### What is the name of the notification integration for RBAC alerts? (`rbac_alert_notification_integration`: text)
**What is this asking?**
Provide the name of an existing Snowflake notification integration that
will receive RBAC alert notifications.

**Why does this matter?**
Snowflake alerts use notification integrations to deliver messages when
alert conditions are met. The integration must already exist before
creating alerts.

**How to find your integration:**
Run `SHOW NOTIFICATION INTEGRATIONS;` to list available integrations.

**Examples:**
- `EMAIL_NOTIFICATION` — Email-based alerts
- `SLACK_SECURITY_ALERTS` — Slack channel integration
- `PAGERDUTY_INTEGRATION` — PagerDuty for on-call alerts

**If no integration exists:**
Create one before running this blueprint:
```sql
CREATE NOTIFICATION INTEGRATION my_email_int
  TYPE = EMAIL
  ENABLED = TRUE
  ALLOWED_RECIPIENTS = ('security-team@company.com');
```

**More Information:**
* [CREATE NOTIFICATION INTEGRATION](https://docs.snowflake.com/en/sql-reference/sql/create-notification-integration)


#### Which warehouse should be used for RBAC monitoring tasks and alerts? (`rbac_monitoring_warehouse`: text)
**What is this asking?**
Specify the warehouse that will execute RBAC monitoring queries and alert
checks. This warehouse runs the scheduled monitoring views and alert
conditions.

**Why does this matter?**
RBAC monitoring queries run against Account Usage views and can be
resource-intensive on large accounts. Using a dedicated or shared platform
warehouse keeps monitoring costs separate from data product workloads.

**Examples:**
- `PLAT_INFRA_WH_ADMIN` — Platform administration warehouse
- `MONITORING_WH` — Dedicated monitoring warehouse
- `COMPUTE_WH` — General-purpose warehouse (for smaller accounts)

**Recommendation:** Use your platform administration warehouse if one exists.
For cost efficiency, an X-Small warehouse with AUTO_SUSPEND = 60 is sufficient
for monitoring workloads.

**More Information:**
* [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse)

