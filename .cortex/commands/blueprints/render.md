<!-- Copyright (c) YEAR Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. 
     Refer to the LICENSE file in the root of this repository for full terms. -->

# Blueprints Render

Generate SQL/Terraform/Documentation from an answer file. This command wraps the `render_journey.py` script.

## Usage

```
/blueprints:render <answer-file> --blueprint <blueprint-name> [options]
```

## Arguments

- `<answer-file>`: Path to the YAML answer file
- `--blueprint <blueprint-name>`: The blueprint ID to render

## Options

- `--lang <sql|terraform>`: Output language (default: sql)
- `--project <name>`: Project name for organizing outputs
- `--skip-guidance`: Skip rendering documentation, only generate IaC code

## Instructions

Execute the `render_journey.py` script with the provided arguments to generate:

1. **IaC Code** (SQL or Terraform): Rendered templates from each step
2. **Documentation**: Step-by-step guidance with filled-in values

## Output Structure

When using `--project`:
```
projects/<project-name>/
├── answers/
│   └── <blueprint-id>/
│       └── answers_<timestamp>.yaml
└── output/
    ├── iac/
    │   └── sql/
    │       └── <blueprint-id>_<timestamp>.sql
    └── documentation/
        └── <blueprint-id>_<timestamp>.md
```

## Implementation

Run the render_journey.py script:

```bash
python scripts/render_journey.py \
  <answer-file> \
  --blueprint <blueprint-name> \
  --lang <language> \
  --project <project-name>
```

## Output Format

```
Rendering blueprint: platform-foundation-setup
Language: sql
Project: my-project

Processing steps...
  ✓ determine-account-strategy
  ✓ configure-organization-name-for-connectivity
  ⚠ enable-organization-account (skipped: missing variables)
  ...

Output generated:
  IaC:    projects/my-project/output/iac/sql/platform-foundation-setup_20250210143022.sql
  Docs:   projects/my-project/output/documentation/platform-foundation-setup_20250210143022.md

Summary:
  Steps rendered: 18/22
  Steps skipped: 4 (missing variables)

Tip: Run '/blueprints:validate <answer-file> --blueprint <blueprint>' to see missing variables.
```

## Error Handling

- If answer file doesn't exist: `Error: Answer file not found: <path>`
- If blueprint doesn't exist: `Error: Blueprint '<name>' not found`
- If render fails: Display error message from render_journey.py

## Examples

```bash
# Render SQL with default project
/blueprints:render answers.yaml --blueprint platform-foundation-setup

# Render to a specific project
/blueprints:render answers.yaml --blueprint data-product-setup --project acme-corp --lang sql

# Render only IaC (skip documentation)
/blueprints:render answers.yaml --blueprint account-creation --skip-guidance
```

Now execute the render_journey.py script with the specified arguments.
