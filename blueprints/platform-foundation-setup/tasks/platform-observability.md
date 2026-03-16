# Platform Observability

## Summary
Configure account-level telemetry parameters to enable logging, metrics,
and tracing for stored procedures, UDFs, and handler code in the
Organization Account.

## External Requirements
- Task 1 (Platform Foundation) completed
- Task 2 (Security & Identity Configuration) completed

## Personas
- Platform Administrator
- SRE / Observability Team

## Role Requirements
- ACCOUNTADMIN role access

## Details
This task configures observability for your Organization Account by setting
the event table and account-level telemetry parameters. The `EVENT_TABLE`
parameter has no default value, so this task explicitly sets it to
`SNOWFLAKE.TELEMETRY.EVENTS` (which exists in every Snowflake account) to
ensure telemetry data is collected. If all telemetry parameters are set to
their disabled values, the event table is not activated.

**Account Context:** All steps in this task should be executed in your
Organization Account (if created in the Create Organization Account step)
or your primary account.

## Steps in This Task

| Step | Title | Purpose |
|------|-------|---------|
| 4.1 | Configure Telemetry Parameters | Set EVENT_TABLE, LOG_LEVEL, METRIC_LEVEL, TRACE_LEVEL, and SQL_TRACE_QUERY_TEXT |

## Time Estimate

- **Telemetry configuration:** 5-10 minutes

## Key Decisions

| Decision | Who Should Decide | Impact |
|----------|-------------------|--------|
| Log level | Platform/SRE Team | Verbosity vs. storage cost; INFO recommended for production |
| Metric collection | Platform/SRE Team | ALL enables execution metrics; no performance impact |
| Trace level | Platform/SRE Team | ALWAYS captures spans; requires LOG_LEVEL not OFF |
| SQL text capture | Platform/Security Team | Useful for debugging but may expose sensitive SQL |

## Parameter Reference

| Parameter | Recommended (Production) | Recommended (Development) |
|-----------|--------------------------|---------------------------|
| LOG_LEVEL | INFO | DEBUG |
| METRIC_LEVEL | ALL | ALL |
| TRACE_LEVEL | ALWAYS | ALWAYS |
| SQL_TRACE_QUERY_TEXT | OFF | ON |

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