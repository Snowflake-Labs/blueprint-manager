# Blueprints Answers Diff

Compare two answer files to show differences.

## Usage

```
/blueprints:answers:diff <file1> <file2>
```

## Arguments

- `<file1>`: Path to the first answer file (base)
- `<file2>`: Path to the second answer file (comparison)

## Instructions

Compare two answer files and display:

1. **Added**: Variables in file2 but not in file1
2. **Removed**: Variables in file1 but not in file2
3. **Changed**: Variables with different values
4. **Unchanged**: Variables with identical values (summary only)

## Output Format

```
Comparing answer files:
  Base:    answers_v1.yaml
  Compare: answers_v2.yaml

## Summary
- Added: 3 variables
- Removed: 1 variable
- Changed: 5 variables
- Unchanged: 37 variables

## Added (in answers_v2.yaml)
| Variable | Value |
|----------|-------|
| new_budget_limit | 5000 |
| enable_new_feature | Yes |
| extra_domains | [analytics, ml] |

## Removed (not in answers_v2.yaml)
| Variable | Original Value |
|----------|----------------|
| deprecated_setting | old_value |

## Changed
| Variable | Base Value | New Value |
|----------|------------|-----------|
| account_strategy | Single Account | Hub-and-Spoke |
| budget_alert_emails | [old@example.com] | [new@example.com, finance@example.com] |
| identity_provider | Okta | Azure AD |
| mfa_enforcement | Immediately | 30 days grace |
| resource_monitor_limit | 100 | 500 |
```

## Implementation

1. Load both YAML files
2. Get all unique keys from both files
3. For each key:
   - If only in file1: mark as removed
   - If only in file2: mark as added
   - If in both: compare values (deep comparison for lists/objects)
4. Display categorized differences

## Options

- `--format <table|yaml|json>`: Output format (default: table)
- `--only <added|removed|changed>`: Only show specific changes
- `--ignore <key1,key2>`: Ignore specific keys in comparison

## Error Handling

- File not found: `Error: File not found: <path>`
- Invalid YAML: `Error: Invalid YAML in <file>: <error>`
- Same file: `Warning: Comparing file to itself - no differences`

## Use Cases

1. **Version comparison**: Compare old and new versions of answers
2. **Environment diff**: Compare prod vs dev configurations  
3. **Review changes**: See what changed before re-rendering
4. **Merge assistance**: Identify conflicts when combining answer files

## Example

```bash
# Compare two answer files
blueprints answers diff answers_old.yaml answers_new.yaml

# Compare across projects
blueprints answers diff projects/dev/answers.yaml projects/prod/answers.yaml

# Output as YAML for further processing
blueprints answers diff file1.yaml file2.yaml --format yaml
```

Now execute this by loading both files and computing the differences.
