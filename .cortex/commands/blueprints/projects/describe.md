<!-- Copyright (c) YEAR Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. 
     Refer to the LICENSE file in the root of this repository for full terms. -->

# Blueprints Projects Describe

Show detailed status of a project, including answer files, outputs, and history.

## Usage

```
/blueprints:projects:describe <name>
```

## Arguments

- `<name>`: Project name to describe

## Instructions

Display comprehensive information about a project:

1. **Project Overview**: Basic information about the project
2. **Answer Files**: List all answer files organized by blueprint
3. **Rendered Outputs**: List all generated IaC and documentation files
4. **History**: Timeline of project activity

## Output Format

```
# Project: my-project

**Location:** projects/my-project/
**Created:** 2025-01-15
**Last Modified:** 2025-02-10

## Answer Files

### platform-foundation-setup
| File | Created | Status |
|------|---------|--------|
| answers_20250115_143022.yaml | 2025-01-15 14:30 | Complete |
| answers_20250210_091500.yaml | 2025-02-10 09:15 | 3 missing values |

### data-product-setup
| File | Created | Status |
|------|---------|--------|
| answers_20250201_120000.yaml | 2025-02-01 12:00 | Complete |

## Rendered Outputs

### IaC (SQL)
| File | Blueprint | Generated |
|------|-----------|-----------|
| platform-foundation-setup_20250115_143022.sql | platform-foundation-setup | 2025-01-15 |
| data-product-setup_20250201_120000.sql | data-product-setup | 2025-02-01 |

### Documentation
| File | Blueprint | Generated |
|------|-----------|-----------|
| platform-foundation-setup_20250115_143022.md | platform-foundation-setup | 2025-01-15 |
| data-product-setup_20250201_120000.md | data-product-setup | 2025-02-01 |

## Summary
- Blueprints used: 2
- Total answer files: 3
- Total renders: 4
```

## Implementation

1. Verify project exists
2. Scan `projects/<name>/answers/` for answer files
3. Scan `projects/<name>/output/` for rendered files
4. Parse answer files to check completeness status
5. Display formatted report

## Error Handling

If project not found:
```
Error: Project 'my-project' not found.

Available projects:
- sample-project
- acme-corp

Run 'blueprints projects list' to see all projects.
```

Now execute this by reading the project directory and presenting the information.
