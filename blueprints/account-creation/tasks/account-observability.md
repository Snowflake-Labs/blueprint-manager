# Account Observability

## Summary
Configure account-level telemetry parameters to enable logging, metrics,
and tracing for stored procedures, UDFs, and handler code in the newly
created account.

## External Requirements
- Security & Identity Configuration complete (Task 2)

## Personas
- Platform Administrator
- SRE / Observability Team

## Role Requirements
- ACCOUNTADMIN role access

## Details
This task configures observability for the newly created account by setting
the event table and account-level telemetry parameters. The `EVENT_TABLE`
parameter has no default value, so this task explicitly sets it to
`SNOWFLAKE.TELEMETRY.EVENTS` (which exists in every Snowflake account) to
ensure telemetry data is collected. If all telemetry parameters are set to
their disabled values, the event table is not activated.

## Steps in This Task

| Step | Title | Purpose |
|------|-------|---------|
| 4.1 | Configure Telemetry Parameters | Set EVENT_TABLE, LOG_LEVEL, METRIC_LEVEL, TRACE_LEVEL, and SQL_TRACE_QUERY_TEXT |

## Account Execution Context

All steps in this task should be executed from the **newly created account**.

| Steps | Execute From |
|-------|--------------|
| 4.1 | **New Account** (the account you created) |

## Time Estimate

- **Telemetry configuration:** 5-10 minutes

## Key Decisions

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Log level | Platform/SRE Team | Verbosity vs. storage cost; INFO recommended for production, consider `DEBUG` for dev, etc. |
| Metric collection | Platform/SRE Team | ALL enables execution metrics; no performance impact |
| Trace level | Platform/SRE Team | ALWAYS captures spans; requires LOG_LEVEL not OFF |
| SQL text capture | Platform/Security Team | Useful for debugging but may expose sensitive SQL |

## Relationship to Platform Foundation

The Platform Foundation workflow established observability for the
Organization Account. This task configures the same telemetry parameters
independently for THIS account. Settings are not inherited — you may choose
different values based on the account's purpose (e.g., more verbose logging
for development accounts).

## Deliverables

Upon completing this task, you will have:
- ✅ Event table set to SNOWFLAKE.TELEMETRY.EVENTS (unless all telemetry is disabled)
- ✅ Account-level logging configured for handler code
- ✅ Execution metrics collection configured
- ✅ Trace spans configured for observability
- ✅ Telemetry parameters verified via SHOW PARAMETERS

## More Information

* [Logging, Tracing, and Metrics](https://docs.snowflake.com/en/developer-guide/logging-tracing/logging-tracing-overview) — Overview of Snowflake observability
* [LOG_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#log-level) — Log level configuration
* [METRIC_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#label-metric-level) — Metric collection
* [TRACE_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#trace-level) — Trace span capture
* [Event Table](https://docs.snowflake.com/en/developer-guide/logging-tracing/event-table-setting-up) — Event table setup