This step collects pricing parameters and DR topology choices needed for accurate cost estimation.

## Why is this important?

- DR costs are often underestimated because teams focus only on replication compute and forget data transfer, target storage, and ongoing drill costs
- Topology choice (same-region vs. cross-region vs. cross-cloud) has a 2x–4x impact on data transfer cost — getting this right early prevents budget surprises
- On new or POC accounts, historical `ACCOUNT_USAGE` data doesn't exist yet; the formula-based estimate in step 5.3 provides a projected cost using these parameters
- Credit rate and storage rate should match your Snowflake contract, not list pricing — using on-demand rates will overestimate costs for contract customers

> **New or POC accounts:** The historical queries in steps 5.2 and 5.3 rely on
> `SNOWFLAKE.ACCOUNT_USAGE` data that does not exist until replication has run at least once.
> If you are setting up DR for the first time, use the formula-based estimate block
> in step 5.3 instead — it calculates projected costs from the `dr_daily_change_rate`,
> `dr_credit_rate`, `dr_storage_rate`, and `dr_topology` values in your answer file.

## Prerequisites

- ACCOUNTADMIN role access
- Knowledge of your Snowflake contract rates (credit rate, storage rate)
- Target region identified (determines data transfer cost tier)

## Key Concepts

- **DR Topology**: The relationship between source and target regions determines data transfer costs. Same-region is free; cross-region and cross-cloud incur per-TB charges.
- **Credit Rate**: The dollar cost per Snowflake credit varies by edition and contract type.
- **Daily Change Rate**: The percentage of total data that changes per day, driving incremental replication volume.

## What Gets Collected

| Parameter | Purpose |
|-----------|---------|
| Target topology | Determines data transfer rate ($0, $20, or $40 per TB) |
| Credit rate | Converts replication credits to dollars |
| Storage rate | Monthly cost for data on target account |
| Daily change rate | Drives incremental replication volume estimates |
| Replication frequency | Affects metadata overhead costs |
| Drill frequency | Annual cost of DR testing |

## Cost Attribution for the Target Account

Replication compute and any post-failover warehouse usage on the target account will appear in billing. Before running drills or executing failover, set up cost controls on the target:

**Tag DR-related warehouses** for cost tracking and chargeback:
```sql
-- Execute on the TARGET account
ALTER WAREHOUSE <warehouse_name> SET TAG cost_center = 'DR', workload_type = 'REPLICATION';
```

**Add a resource monitor** to cap unexpected credit consumption post-failover. Without one, resumed warehouses on the target account have no spending guardrail:
```sql
-- Execute on the TARGET account
CREATE RESOURCE MONITOR dr_target_monitor
  WITH CREDIT_QUOTA = <monthly_estimate>
  TRIGGERS ON 80 PERCENT DO NOTIFY
           ON 100 PERCENT DO SUSPEND;

ALTER ACCOUNT SET RESOURCE_MONITOR = dr_target_monitor;
```

Replace `<monthly_estimate>` with the projected monthly cost from step 5.3 to set a meaningful cap.

**More Information:**
* [Replication Cost](https://docs.snowflake.com/en/user-guide/account-replication-cost) — Cost model documentation
* [Service Consumption Table](https://www.snowflake.com/legal/snowflake-service-consumption-table/) — Current pricing reference


### Configuration Questions

#### What is the relationship between source and target regions? (`dr_topology`: single-select)
**What is this asking?**
Select the geographic relationship between your source and target accounts.
This determines data transfer costs.

**Options:**
- **Same-Region**: Source and target in the same cloud region (e.g., both AWS us-west-2).
  Data transfer: $0/TB (free).
- **Cross-Region Same-Cloud**: Different regions on the same cloud provider
  (e.g., AWS us-west-2 → AWS us-east-1). Data transfer: ~$20/TB.
- **Cross-Cloud**: Different cloud providers (e.g., AWS → Azure).
  Data transfer: ~$40/TB.

**Recommendation:** Cross-Region Same-Cloud provides geographic redundancy
at moderate cost. Cross-Cloud provides maximum isolation but at higher cost.

**Options:**
- Same-Region
- Cross-Region Same-Cloud
- Cross-Cloud

#### What is your Snowflake credit rate ($/credit)? (`dr_credit_rate`: text)
**What is this asking?**
The dollar cost per Snowflake credit under your contract. This is used for
cost estimation calculations.

**Default Rates (On-Demand):**
- Standard Edition: $2.00/credit
- Enterprise Edition: $3.00/credit
- Business Critical Edition: $4.00/credit

**Capacity/Pre-Purchased Rates:**
Typically 20-50% lower than on-demand. Check your Snowflake contract for
your actual negotiated rate.

**Default:** If unsure, enter `3.00` (Enterprise on-demand).


#### What is your storage rate ($/TB/month)? (`dr_storage_rate`: text)
**What is this asking?**
The monthly cost per terabyte of storage. Used to estimate target account
storage costs.

**Common Values:**
- `23` — Capacity pricing (most contracts)
- `40` — On-demand pricing

**Default:** If unsure, enter `23`.


#### What percentage of data changes daily? (`dr_daily_change_rate`: text)
**What is this asking?**
The estimated percentage of total storage that changes (inserts, updates,
deletes) per day. This drives incremental replication cost calculations.

**Common Values:**
- `1` — Low-change environments (mostly historical/analytical data)
- `2` — Typical for mixed workloads (default)
- `5` — High-change environments (heavy ingestion/ETL)
- `10` — Very high-change (streaming or frequent full-table refreshes)

**How to estimate:**
Check INFORMATION_SCHEMA.TABLE_STORAGE_METRICS for bytes_inserted/updated
relative to total table size over recent days.


#### How often should replication run? (`dr_replication_frequency`: single-select)
**What is this asking?**
Select the replication interval. This directly sets your RPO — data
ingested between refreshes could be lost during failover.

**Options:**
- `10 MINUTE` — 10-minute RPO (recommended for critical data)
- `30 MINUTE` — 30-minute RPO (standard workloads)
- `60 MINUTE` — 1-hour RPO (non-critical data)
- `120 MINUTE` — 2-hour RPO (low-criticality data)
- `USING CRON 0 0 * * * UTC` — Daily at midnight UTC

**Note:** Snowflake's `REPLICATION_SCHEDULE` only accepts `<n> MINUTE`
or `USING CRON <expr> <timezone>` syntax. The selected value is used
verbatim in the generated SQL.

**Recommendation:** Start with `10 MINUTE` for critical databases.
You can create separate failover groups with different frequencies for
different RPO tiers.

**Options:**
- 10 MINUTE
- 30 MINUTE
- 60 MINUTE
- 120 MINUTE
- USING CRON 0 0 * * * UTC

#### How often will you run DR drills? (`dr_drill_frequency`: single-select)
**What is this asking?**
How frequently you plan to execute DR failover/failback drills to validate
your disaster recovery readiness.

**Options:**
- **Monthly**: Best for highly regulated environments or critical systems
- **Quarterly**: Recommended for most production environments
- **Semi-Annually**: Minimum for compliance requirements
- **Annually**: Bare minimum (not recommended)

**Recommendation:** Quarterly (4/year) balances validation frequency with
operational overhead and cost.

**Options:**
- Monthly (12/year)
- Quarterly (4/year)
- Semi-Annually (2/year)
- Annually (1/year)
