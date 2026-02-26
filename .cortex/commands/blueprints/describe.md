<!-- Copyright (c) 2026 Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. See LICENSE file. -->

# Blueprints Describe

Show detailed information about a specific blueprint, including its task/step tree.

## Usage

```
/blueprints:describe <blueprint-name>
```

## Arguments

- `<blueprint-name>`: The blueprint ID/directory name (e.g., `platform-foundation-setup`, `account-creation`, `data-product-setup`)

## Instructions

1. Load the blueprint's `meta.yaml` from `blueprints/<blueprint-name>/meta.yaml`
2. If the blueprint doesn't exist, show an error with available blueprint names
3. Display comprehensive blueprint information

## Output Format

```
# Blueprint: <name>

**ID:** <blueprint_id>
**Summary:** <summary>
**Repeatable:** <Yes/No>

## Overview

<overview text>

## Steps (<count> total)

| # | Step ID | Title |
|---|---------|-------|
| 1 | determine-account-strategy | Determine Account Strategy |
| 2 | configure-organization-name | Configure Organization Name |
...

## Step Details

For each step, if `overview.md` exists in the step directory, show:
- Step number and ID
- First heading from the overview (title)
- First paragraph (brief description)
```

## Implementation

1. Read `blueprints/<blueprint-name>/meta.yaml`
2. Parse the YAML to get: `name`, `blueprint_id`, `summary`, `overview`, `is_repeatable`, `steps`
3. For each step in the `steps` list:
   - Check if `blueprints/<blueprint-name>/<step-id>/` exists
   - Read `dynamic.md.jinja` to extract the title (first `# ` heading)
   - Read `overview.md` if it exists for additional context
4. Display all information in a well-formatted markdown structure

## Error Handling

If blueprint not found:
```
Error: Blueprint '<name>' not found.

Available blueprints:
- account-creation
- data-product-setup  
- platform-foundation-setup

Run 'blueprints list' to see all available blueprints with details.
```

Now execute this by reading the specified blueprint's meta.yaml and presenting the information.
