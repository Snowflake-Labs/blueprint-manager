<!-- Copyright (c) 2026 Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. See LICENSE file. -->

# Blueprints Answers Validate

Check an answer file for missing or invalid values without needing to specify a blueprint.

## Usage

```
/blueprints:answers:validate <file> [--blueprint <name>]
```

## Arguments

- `<file>`: Path to the YAML answer file to validate

## Options

- `--blueprint <name>`: Blueprint to validate against (auto-detected from file if not specified)

## Instructions

This is an alias/alternative to `blueprints validate` that focuses on the answer file perspective.

Validate an answer file by:

1. **Parse YAML**: Load and validate YAML syntax
2. **Detect Blueprint**: Infer blueprint from file path or comments if not specified
3. **Check Values**: Identify null, empty, or missing required values
4. **Type Validation**: Verify values match expected types from questions.yaml

## Output Format

### Valid Answer File
```
Validating: projects/acme-corp/answers/platform-foundation-setup/answers.yaml

✅ Answer file is valid!

Summary:
- Total variables: 45
- Filled: 45
- Empty/Null: 0

Ready to render with: blueprints render <file> --blueprint platform-foundation-setup
```

### Answer File with Issues
```
Validating: answers.yaml

⚠️ Answer file has issues

Summary:
- Total variables: 45
- Filled: 38
- Empty/Null: 5
- Invalid type: 2

Null Values (need input):
| Variable | Expected Type | Description |
|----------|---------------|-------------|
| org_admin_email | text | Organization admin email address |
| breakglass_accounts | list | Emergency access accounts |

Invalid Types:
| Variable | Expected | Got | Value |
|----------|----------|-----|-------|
| domain_list | list | text | "sales" |
| budget_alert_emails | list | text | "finance@example.com" |

Fix suggestions:
- domain_list should be a YAML list: 
    domain_list:
      - sales
      - marketing
- budget_alert_emails should be a YAML list:
    budget_alert_emails:
      - finance@example.com
```

## Implementation

1. Load the answer YAML file
2. If blueprint not specified, try to detect from:
   - File path (e.g., `answers/platform-foundation-setup/answers.yaml`)
   - YAML comments (e.g., `# Blueprint: platform-foundation-setup`)
3. Load questions.yaml to get expected types
4. Validate each value:
   - Non-null for required fields
   - Correct type (text, list, multi-select, object-list)
   - Valid options for multi-select fields
5. Display validation report

## Error Handling

- File not found: `Error: Answer file not found: <path>`
- Invalid YAML: `Error: Invalid YAML syntax: <error>`
- Blueprint not detected: `Error: Cannot detect blueprint. Use --blueprint to specify.`

Now execute this by reading the answer file and performing validation.
