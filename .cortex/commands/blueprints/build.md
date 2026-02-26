<!-- Copyright (c) 2026 Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. See LICENSE file. -->

# Blueprints Build

Start the interactive blueprint building process. This command wraps the `blueprint-builder` skill to guide users through creating a complete answer file for a blueprint.

## Usage

```
/blueprints:build <blueprint-name> [--project <project-name>]
```

## Arguments

- `<blueprint-name>`: The blueprint ID to build (e.g., `platform-foundation-setup`)
- `--project <project-name>`: Optional project name to organize answers and outputs

## Instructions

This command invokes the `blueprint-builder` skill with the specified blueprint. The skill will:

1. **Select/Create Project** - Choose or create a project workspace
2. **Load Blueprint** - Load the specified blueprint definition
3. **Initialize Answer File** - Create new or load existing answers
4. **Collect User Context** - Gather requirements through open-ended description or step-by-step
5. **Generate Answers** - Auto-fill answers based on provided context
6. **Present Summary** - Show answered/unanswered questions
7. **Interactive Walkthrough** - Review each step and fill remaining values
8. **Generate IaC** - Render SQL/Terraform/Documentation

## Implementation

$blueprint-builder Help me build the {{blueprint-name}} blueprint{{#if project}} for project {{project}}{{/if}}

## Example

```bash
# Start building the platform foundation blueprint
/blueprints:build platform-foundation-setup

# Build with a specific project
/blueprints:build data-product-setup --project acme-corp
```

## Error Handling

If blueprint not found:
```
Error: Blueprint '<name>' not found.

Available blueprints:
- account-creation
- data-product-setup  
- platform-foundation-setup

Run '/blueprints:list' to see all available blueprints.
```

## Notes

- The build process is interactive and will ask questions to gather requirements
- You can provide a description of your organization/requirements upfront for auto-filling
- Progress is saved and can be resumed later
- Use `/blueprints:validate` to check answer completeness at any time
