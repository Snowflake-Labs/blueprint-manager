This step calculates all cost components: initial replication, ongoing monthly replication compute and transfer, target storage, serverless maintenance, and DR drill costs. Produces a comprehensive cost report.

## Why is this important?

- DR cost is frequently an afterthought that surprises teams at first invoice — understanding it upfront enables budget approval before committing to a topology
- Initial replication (one-time full copy) is often the largest single cost and determines whether the project needs a maintenance window
- Serverless features (materialized views, clustering, search optimization) will run on the target account too — omitting them understates ongoing cost
- For greenfield accounts, the formula-based estimate block provides actionable projections even with no historical data

## Prerequisites

- ACCOUNTADMIN role access with `SNOWFLAKE.ACCOUNT_USAGE` view access
- Storage footprint measured (step 5.2)
- Cost parameters collected (step 5.1) — topology, credit rate, storage rate, daily change rate

## Key Concepts

- **Initial Replication Cost**: One-time cost to fully replicate all data to the target account.
- **Incremental Replication Cost**: Ongoing monthly cost for syncing daily data changes.
- **Target Storage Cost**: Monthly storage charge for maintaining the replica on the target account.
- **Operational Cost**: DR drill compute, serverless maintenance (clustering, search optimization, materialized views).

## What Gets Calculated

| Cost Category | Components |
|---------------|------------|
| Initial (one-time) | Data transfer + compute for full copy |
| Monthly replication | Transfer + compute for daily changes + metadata overhead |
| Monthly storage | Replicated data on target at standard storage rate |
| Monthly operational | Serverless features + amortized drill costs |
| Annual total | Year 1 (with initial) and Year 2+ projections |

## Considerations

> **Note**: Actual costs depend on data complexity and change patterns. Use existing `REPLICATION_GROUP_USAGE_HISTORY` data when available for more accurate estimates. Rates should be verified against your Snowflake contract.

**More Information:**
* [Replication Cost](https://docs.snowflake.com/en/user-guide/account-replication-cost) — Cost model and formula documentation
* [REPLICATION_GROUP_USAGE_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/replication_group_usage_history) — Historical replication usage data


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
