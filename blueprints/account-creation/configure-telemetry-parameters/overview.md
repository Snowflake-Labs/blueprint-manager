## Overview

This step configures the account's event table and telemetry parameters so that logs, metrics, and traces from stored procedures, UDFs, and other handler code are captured. These settings enable observability across your Snowflake workloads, providing visibility into execution behavior, performance, and errors.

Every Snowflake account contains a pre-existing event table at `SNOWFLAKE.TELEMETRY.EVENTS`, but the `EVENT_TABLE` parameter has no default value. If telemetry collection is enabled, this step explicitly sets it to `SNOWFLAKE.TELEMETRY.EVENTS` so that telemetry data is collected, then configures four additional parameters that control what gets recorded and how much detail is captured. If all telemetry parameters are set to their disabled values (`LOG_LEVEL = OFF`, `METRIC_LEVEL = NONE`, `TRACE_LEVEL = OFF`, `SQL_TRACE_QUERY_TEXT = OFF`), the event table is not activated since no data would be collected.

### Key Concepts

- **Log Level**: Controls which severity of log messages are captured from handler code. When set at multiple levels (account, database, function), the more verbose level wins.
- **Metric Level**: Controls whether execution metrics (CPU, memory, duration) are collected from handler code.
- **Trace Level**: Controls whether trace spans are captured for handler code execution. Requires `LOG_LEVEL` to not be `OFF`.
- **SQL Trace Query Text**: Controls whether the SQL text of traced statements is included in the event table (up to 1024 characters per statement). Useful for debugging but should be disabled if SQL may contain sensitive data.

### What Gets Configured

| Parameter | Purpose | Scope |
|-----------|---------|-------|
| EVENT_TABLE | Target event table for telemetry data | Account |
| LOG_LEVEL | Severity threshold for log capture | Account |
| METRIC_LEVEL | Enable/disable metrics collection | Account |
| TRACE_LEVEL | Enable/disable trace span capture | Account |
| SQL_TRACE_QUERY_TEXT | Include SQL text in traces | Account |

### Important Considerations

> **Note**: `TRACE_LEVEL` requires `LOG_LEVEL` to be set to a value other than `OFF`. If `LOG_LEVEL` is `OFF`, traces will not be captured regardless of the `TRACE_LEVEL` setting.

> **Note**: These are account-level defaults. The values for `LOG_LEVEL`, `METRIC_LEVEL`, and `TRACE_LEVEL` can be overridden at the object or session level with more verbose settings as needed.

> **Note**: Enabling `SQL_TRACE_QUERY_TEXT` captures SQL statement text in the event table. Disable this if your SQL statements may contain sensitive information such as PII or credentials.


### Configuration Questions

#### What log level should be set for this account? (`account_log_level`: multi-select)
**What is this asking?**
Select the minimum severity level for log messages captured from stored
procedures, UDFs, and other handler code.

**Options (least to most verbose):**
- **Off**: Logging disabled — no messages captured
- **Fatal**: Captures FATAL only
- **Error**: Captures ERROR and FATAL
- **Warn**: Captures WARN, ERROR, and FATAL
- **Info**: Captures INFO, WARN, ERROR, and FATAL — **recommended for production**
- **Debug**: Captures DEBUG, INFO, WARN, ERROR, and FATAL
- **Trace**: Captures everything — TRACE, DEBUG, INFO, WARN, ERROR, and FATAL

**Precedence:** When set at multiple levels (account, object, session),
the more verbose level wins. For example, if the account is set to Error
but a specific function is set to Debug, Debug is used for that function.

**Recommendation:** Use `Info` for production accounts and `Debug` for
development or test accounts.

**More Information:**
* [LOG_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#log-level)
* [How Snowflake determines the level in effect](https://docs.snowflake.com/en/developer-guide/logging-tracing/telemetry-levels#label-telemetry-level-effective)

**Options:**
- Trace
- Debug
- Info
- Warn
- Error
- Fatal
- Off

#### Should execution metrics be collected for this account? (`account_metric_level`: multi-select)
**What is this asking?**
Choose whether to collect execution metrics (CPU, memory, duration) from
stored procedures, UDFs, and other handler code.

**Options explained:**
- **All**: Collect all execution metrics — recommended
- **None**: No metrics collected (disabled)

**Recommendation:** Use `All` for all accounts. Metrics have minimal
performance impact and provide valuable insight into handler code
execution performance.

**More Information:**
* [METRIC_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#label-metric-level)

**Options:**
- All
- None

#### What trace level should be set for this account? (`account_trace_level`: multi-select)
**What is this asking?**
Choose whether trace spans are captured from handler code execution.
Traces record start/end timestamps, execution status, and query context
for each handler invocation.

**Options explained:**
- **Always**: Always capture trace spans — recommended
- **On Event**: Only capture traces when custom events are added in code
- **Off**: No tracing (disabled)

**Important:** Tracing requires the `LOG_LEVEL` parameter 
(`account_log_level` in this document) to be set to a value other
than `Off`. If `LOG_LEVEL` is `Off`, traces will not be captured
regardless of this setting.

**Recommendation:** Use `Always` to get full observability for both 
auto-instrumented and explicitly instrumented code. Use `On Event`
if you only want traces for explicitly instrumented code.

**More Information:**
* [TRACE_LEVEL Parameter](https://docs.snowflake.com/en/sql-reference/parameters#trace-level)

**Options:**
- Always
- On_Event
- Off

#### Should SQL statement text be captured in trace data? (`account_sql_trace_query_text`: multi-select)
**What is this asking?**
Choose whether the SQL text of traced statements is included in the
event table. When enabled, up to 1024 characters of each SQL statement
are captured alongside trace data.

**Options explained:**
- **On**: Capture SQL text — useful for debugging
- **Off**: Do not capture SQL text — recommended for production

**Security consideration:** Disable this if your SQL statements may
contain sensitive information such as PII, credentials, or other
confidential data.

**Recommendation:** Use `Off` for production accounts. Use `On` for
development or debugging scenarios where you need to correlate traces
with specific SQL statements.

**More Information:**
* [SQL_TRACE_QUERY_TEXT Parameter](https://docs.snowflake.com/en/sql-reference/parameters#sql-trace-query-text)

**Options:**
- On
- Off
