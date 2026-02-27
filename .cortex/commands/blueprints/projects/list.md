<!-- Copyright (c) YEAR Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. 
     Refer to the LICENSE file in the root of this repository for full terms. -->

# Blueprints Projects List

List all existing projects in the blueprint-manager workspace.

## Usage

```
blueprints projects list
```

## Instructions

Scan the `projects/` directory and list all project subdirectories with their status information.

For each project, show:
- **Name**: Project directory name
- **Blueprints**: Which blueprints have answer files
- **Last Modified**: When the project was last updated
- **Status**: Brief status (e.g., "3 answer files, 2 renders")

## Output Format

```
Projects:

| Project | Blueprints | Answer Files | Last Modified |
|---------|------------|--------------|---------------|
| sample-project | platform-foundation-setup, account-creation, data-product-setup | 3 | 2025-01-15 |
| acme-corp | platform-foundation-setup | 1 | 2025-02-01 |
| demo-customer | data-product-setup | 2 | 2025-02-10 |

Total: 3 projects
```

## Implementation

1. List all directories in `projects/`
2. For each project directory:
   - Check `answers/` subdirectory for blueprint answer files
   - Count answer files per blueprint
   - Get last modification time
3. Display results in a formatted table

## Empty State

If no projects exist:
```
No projects found.

Create a new project with: /blueprints:projects:create <name>
```

Now execute this by scanning the projects directory and presenting the information.
