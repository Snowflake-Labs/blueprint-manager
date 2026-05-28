---
name: pipeline-plan-generator
description: "Use when a Pipeline Planner answers file exists and the user wants to generate an implementation plan. Triggers: generate plan from answers, run plan generator, investigate sources, create implementation plan, pipeline plan generator, I have my answers file ready."
---

# Pipeline Plan Generator

## Overview

Accepts a completed Pipeline Planner answers file, investigates the user's source data in Snowflake, generates a transformation topology (DAG), and produces a self-contained implementation plan document.

**Contract:** The answers file is the sole input. This skill never asks blueprint-style questions — requirements are already collected.

## When to Use

- User has completed the Pipeline Planner blueprint and has an answers file
- User says "generate a plan from my answers" or "run the plan generator"
- User has a YAML file with `selected_transform_technology`, `source_seed_reference`, and `transformation_intent` populated

**When NOT to use:**
- User hasn't collected requirements yet → direct them to the Pipeline Planner blueprint first
- User wants to change their technology selection → re-run the blueprint

## Input Contract

The answers file (YAML) must contain these keys:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `selected_transform_technology` | string | Yes | Dynamic Tables, Streams & Tasks, Snowpark, dbt Projects on Snowflake, dbt Core, dbt + Dynamic Tables, Stored Procedures |
| `source_seed_reference` | string | Yes | Table FQN, schema, database, stage, or external description |
| `transformation_intent` | string | Yes | What the pipeline should produce |
| `data_freshness_requirement` | string | Yes | Batch, Near Real-Time, Real-Time |
| `downstream_consumers` | list | Yes | Who/what consumes the output |
| `pipeline_criticality` | string | Yes | Mission-critical, Important, Exploratory |
| `pipeline_trigger_model` | string | No | How the pipeline gets triggered |
| `pipeline_constraints` | list | No | Hard constraints |
| `work_context` | string | No | Build New or Extend Existing |
| `expand_target_project` | string | No | Expansion path only |
| `expansion_technology` | string | No | Expansion path only |

## Locating the Answers File

Answer files are produced by the Pipeline Planner blueprint and stored at:

```
projects/<project_name>/answers/pipeline-planner/answers_<timestamp>.yaml
```

**Projects directory resolution** (same as blueprint-builder):
1. `--projects-dir <path>` CLI flag (highest priority)
2. `BLUEPRINT_MANAGER_PROJECTS_DIR` environment variable
3. `<cwd>/projects` (default)

**Discovery flow when user doesn't provide an explicit path:**

```bash
# Find all pipeline-planner answer files across all projects
find projects/*/answers/pipeline-planner -name "*.yaml" -type f 2>/dev/null | sort -r
```

If multiple files exist, present the list (most recent first by timestamp) and ask the user to select one. If exactly one exists, use it automatically.

The `project_name` is derived from the answer file path: `projects/<project_name>/answers/...` — extract the directory name between `projects/` and `/answers/`.

## Execution

### Step 1: Load and Validate Answers

1. Locate the answers file (user provides path, or discover via the flow above)
2. Read and parse the YAML
3. Extract `project_name` from the file path
4. Verify required keys are populated:
   - `selected_transform_technology`
   - `source_seed_reference`
   - `transformation_intent`
   - `data_freshness_requirement`
   - `downstream_consumers`
   - `pipeline_criticality`

If any required key is missing or null, tell the user which keys are needed and stop. Direct them to re-run the Pipeline Planner blueprint to collect the missing answers.

### Step 2: Source Investigation (silent)

Execute against the user's connected Snowflake account. Do NOT display intermediate results unless errors occur.

**2a. Classify source type** — SQL cascade, stop at first success:

```sql
-- Attempt 1: Table?
DESCRIBE TABLE <source_seed_reference>;
-- Success → source_type = TABLE

-- Attempt 2: Schema?
SHOW TABLES IN SCHEMA <source_seed_reference>;
-- Success → source_type = SCHEMA

-- Attempt 3: Database?
SHOW SCHEMAS IN DATABASE <source_seed_reference>;
-- Success → source_type = DATABASE

-- Attempt 4: Stage?
LIST <source_seed_reference>;
-- Success → source_type = STAGE

-- All failed → source_type = EXTERNAL (ask user for schema)
```

**2b. Resolve to concrete objects:**

| source_type | Action |
|-------------|--------|
| TABLE | Use as-is |
| SCHEMA | Enumerate tables, filter by naming pattern (include RAW/SRC/STG/INGEST/LANDING/EVENT/LOG; exclude DIM/FACT/AGG/MART/RPT/SUMMARY/ARCHIVE). Auto-select ≤5; confirm 6-20; surface top 10 for 20+ |
| DATABASE | Enumerate schemas → tables, same filtering |
| STAGE | LIST files, sample payload (try Parquet → JSON → CSV) |
| EXTERNAL | Ask user for sample payload or column list |

**2c. Cortex availability probe:**

```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'ping') AS cortex_probe;
```

Record `cortex_available = true/false`.

**2d. Describe sources:**

```sql
DESCRIBE TABLE <each_resolved_source_object>;
```

Record columns, types, nullability for each table.

**2e. Enrich (if Cortex available):**

```sql
-- Semantic descriptions
SELECT SNOWFLAKE.CORTEX.AI_GENERATE_TABLE_DESC(
  '<table_fqn>',
  OBJECT_CONSTRUCT('describe_columns', TRUE, 'use_table_data', TRUE)
) AS ai_description;

-- Relationship inference (2+ tables only)
SELECT SYSTEM$CORTEX_ANALYST_FAST_GENERATION(
  ARRAY_CONSTRUCT('<table_1>', '<table_2>', ...)
) AS fastgen_result;
```

Extract `structuredSuggestions.relationships` (left_table, right_table, left_column, right_column, cardinality, join_type).

**2f. Heuristic fallback (if Cortex unavailable, 2+ tables):**

Pattern-match columns ending in `_ID`, `_KEY`, `_CODE` across tables. Shared names → inferred relationship with `inferred_by: "heuristic"`.

**2g. Error handling:**

If any DESCRIBE or enrichment step fails, surface the specific error to the user and ask whether to remove the problematic table or fix permissions. Otherwise proceed silently.

### Step 3: Generate Topology (silent)

Generate a minimal DAG appropriate for the selected technology:

| Technology | Node type | Refresh mechanism |
|-----------|-----------|-------------------|
| Dynamic Tables | Dynamic Table | TARGET_LAG |
| Streams & Tasks | Task | Stream trigger or CRON |
| Snowpark | DataFrame step | Python orchestration |
| dbt | dbt model | staging → intermediate → mart |
| Stored Procedures | Procedure | Orchestration chain |

For each node, record:
- `name`: fully-qualified object name
- `object_type`: dynamic_table / stream / task / snowpark_procedure / dbt_model / stored_procedure
- `purpose`: one-sentence description
- `depends_on`: upstream object names
- `sql_body`: complete, executable SQL using real column names from DESCRIBE
- Technology-specific config: `target_lag`, `schedule`, `after`, `stream_trigger`, `file_path`

**Design principle:** Fewest nodes that satisfy the intent. Typical: 2-4 nodes (staging → transform → output).

Write `topology_nodes` back to the answers file as structured YAML.

### Step 4: Generate Test Plan (silent)

Use `pipeline_criticality` from the answers file to determine test scope. Combine with column metadata from Step 2 to produce concrete, executable test SQL.

**4a. Test categories by criticality tier:**

| Category | Mission-critical | Important | Exploratory |
|----------|:---:|:---:|:---:|
| Primary key uniqueness | Yes | Yes | Yes |
| Non-null constraints (key columns) | Yes | Yes | Yes |
| Data completeness (partition existence) | Yes | Yes | — |
| Row count stability (day-over-day variance) | Yes | Yes | — |
| Referential integrity | Yes | — | — |
| Statistical stability (distribution drift) | Yes | — | — |
| Enum validity & conditional column gating | Yes | — | — |
| Downstream compatibility | Yes | — | — |
| Monitoring alerts (severity + recovery) | Yes | Basic | — |
| Retention & housekeeping validation | Yes | Yes | — |

**4b. For each applicable category, generate:**

- **Test name**: descriptive, prefixed with category (e.g., `pk_uniqueness__orders_daily`)
- **Test SQL**: executable SELECT that returns rows only on failure (zero rows = pass)
- **Severity**: `critical` (blocks deploy), `warning` (alerts but doesn't block), `info` (logged only)
- **Schedule**: how often to run (aligned with pipeline refresh cadence)
- **Recovery action**: what to do when the test fails (Mission-critical only)

**4c. Test SQL patterns:**

```sql
-- Primary key uniqueness
SELECT pk_col, COUNT(*) AS cnt
FROM <target_table>
GROUP BY pk_col HAVING cnt > 1;

-- Non-null constraints
SELECT COUNT(*) AS null_count
FROM <target_table>
WHERE <key_column> IS NULL;

-- Data completeness (partition exists for expected date)
SELECT 'missing_partition' AS issue
WHERE NOT EXISTS (
  SELECT 1 FROM <target_table>
  WHERE <partition_col> = CURRENT_DATE - 1
);

-- Row count stability (>30% day-over-day variance)
WITH today AS (SELECT COUNT(*) AS cnt FROM <target_table> WHERE <date_col> = CURRENT_DATE - 1),
     yesterday AS (SELECT COUNT(*) AS cnt FROM <target_table> WHERE <date_col> = CURRENT_DATE - 2)
SELECT 'row_count_drift' AS issue, today.cnt, yesterday.cnt
FROM today, yesterday
WHERE ABS(today.cnt - yesterday.cnt) > yesterday.cnt * 0.3;

-- Referential integrity
SELECT child.<fk_col>, COUNT(*) AS orphan_count
FROM <child_table> child
LEFT JOIN <parent_table> parent ON child.<fk_col> = parent.<pk_col>
WHERE parent.<pk_col> IS NULL
GROUP BY child.<fk_col>;

-- Enum validity
SELECT <enum_col>, COUNT(*) AS invalid_count
FROM <target_table>
WHERE <enum_col> NOT IN (<valid_values>)
GROUP BY <enum_col>;
```

**4d. Monitoring alerts (Mission-critical and Important):**

| Tier | Alert triggers | Severity | Recovery |
|------|---------------|----------|----------|
| Mission-critical | Missing partition, row count drop >30%, PK violation, null in required column, referential integrity failure | Critical | Documented per-alert (re-run, page oncall, pause downstream) |
| Important | Missing partition, row count drop >50% | Warning | Re-run pipeline; escalate if persists |

Write `test_plan` back to the answers file as structured YAML.

### Step 5: Present Plan (user-facing)

Display to the user:

1. **ASCII DAG** — box-drawing characters (NOT mermaid). Example style:
```
┌─────────────────┐    ┌─────────────────┐
│  source_table_1 │    │  source_table_2 │
└────────┬────────┘    └────────┬────────┘
         └──────────┬───────────┘
                    ▼
         ┌──────────────────┐
         │  stg_enriched    │
         └────────┬─────────┘
                  ▼
         ┌──────────────────┐
         │  final_output    │
         └──────────────────┘
```

2. **Node Walkthrough** — table: # | Name | Type | Operation | Why Separate
3. **Output Dataset** — name, grain, columns, satisfies intent
4. **Test & Monitoring Plan** — summary table: test name, category, severity, schedule
5. **Configuration Context** — technology, freshness, trigger, consumers, criticality tier

### Step 6: Approve Plan (user-facing)

Ask: **"Do you approve this transformation plan?"**

| Option | Action |
|--------|--------|
| Approved | Proceed to save |
| Adjust Intent | Re-ask intent, regenerate topology (loop to Step 3) |
| Add Source | Collect new source, re-investigate (loop to Step 2) |
| Change Node | Ask which node + what change, regenerate (loop to Step 3) |

Loop until "Approved".

### Step 7: Save Plan

Use `project_name` extracted in Step 1 and the original `answer_file_path` for all paths below.

**7a. Render SQL artifact:**

```bash
mkdir -p projects/<project_name>/output/iac/sql
.venv/bin/python scripts/render_journey.py \
  projects/<project_name>/answers/pipeline-planner/<answers_file>.yaml \
  --blueprint pipeline-planner \
  --lang sql \
  --project <project_name>
```

**7b. Write plan document** to `projects/<project_name>/output/plans/<intent-slug>-plan.md`

Required sections:

1. **Executive Summary** — intent, technology choice, source → output, SQL artifact path
2. **Pipeline Topology** — ASCII DAG diagram
3. **Source Data Profile** — per table: FQN, columns, relationships, row estimates
4. **Node Specifications** — per node: purpose, input, output, transform logic, implementation SQL, dependencies, configuration
5. **Output Dataset Definition** — final table, grain, columns, consumers
6. **Test & Monitoring Plan** — per test: name, category, SQL, severity, schedule, recovery action (tier-appropriate)
7. **Implementation Sequence** — ordered DDL with prerequisites and validation queries
8. **Configuration Context** — technology, freshness, trigger, consumers, constraints, criticality tier
9. **Assumptions & Open Questions** — what to verify before executing

**Writing rules:**
- Use actual table/column names from investigation (never placeholders)
- SQL must be concrete and immediately executable
- Technical specification, not tutorial
- Target 200-600 lines depending on complexity and criticality tier

**7c. Confirm to user:**
- SQL artifact: `projects/<name>/output/iac/sql/<file>.sql`
- Plan document: `projects/<name>/output/plans/<intent-slug>-plan.md`

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using mermaid for DAG diagrams | Use ASCII box-drawing characters — mermaid doesn't render in terminal |
| Placeholder SQL (`<your_warehouse>`) | Use real names from investigation; note assumptions in Section 8 |
| Generating topology without DESCRIBE data | Always complete investigation first — topology needs real column names |
| Skipping Cortex probe | Always probe — determines enrichment path (AI vs heuristic) |
| Presenting raw DESCRIBE output | Investigation is silent; only surface errors |
