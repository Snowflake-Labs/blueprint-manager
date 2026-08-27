This step generates a RACI (Responsible, Accountable, Consulted, Informed) matrix that assigns clear ownership for every activity during a DR event.

## Why is this important?

- Without pre-assigned ownership, DR events devolve into improvised coordination — the RACI eliminates ambiguity under pressure
- Each activity must have exactly ONE Accountable person; multiple accountables cause delays at critical moments
- The matrix covers both Snowflake-specific actions and external steps (ETL repointing, BI tools, communication) so no team is surprised
- Reviewing this matrix with stakeholders before a drill reveals ownership gaps and disagreements while there's time to resolve them

## Prerequisites

- DR Implementation completed (Task 2)
- Organizational context collected (step 4.1) — team name, approver, communication channels

## Key Concepts

- **Responsible (R)**: Does the work
- **Accountable (A)**: Owns the outcome, approves (exactly ONE per activity)
- **Consulted (C)**: Provides input before action
- **Informed (I)**: Notified after action is taken

## What Gets Generated

| Activity Category | Examples |
|------------------|----------|
| Event declaration | Monitor, declare, initial notification |
| Snowflake failover | Suspend, promote, redirect, resume warehouses |
| External repointing | ETL pipelines, BI tools, application connections |
| Validation | Data integrity, pipeline verification, dashboard check |
| Communication | Status updates, recovery complete, failback notice |

## Considerations

> **Note**: Each activity must have exactly ONE Accountable person. Review this matrix with all stakeholders before a DR event occurs. Update it after each drill based on lessons learned.

**More Information:**
* [Introduction to Replication and Failover](https://docs.snowflake.com/en/user-guide/account-replication-intro) — DR event context and roles


### Configuration Questions

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

