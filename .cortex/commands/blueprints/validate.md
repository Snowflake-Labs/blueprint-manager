# Blueprints Validate

Check an answer file for completeness against blueprint requirements.

## Usage

```
/blueprints:validate <answer-file> --blueprint <blueprint-name>
```

## Arguments

- `<answer-file>`: Path to the YAML answer file to validate
- `--blueprint <blueprint-name>`: The blueprint ID to validate against

## Instructions

Validate an answer file by checking:

1. **File Existence**: Verify the answer file exists and is valid YAML
2. **Blueprint Match**: Ensure the blueprint exists
3. **Required Variables**: Check each step's templates for required variables
4. **Missing Values**: Identify variables that are missing from the answer file
5. **Null Values**: Identify variables that exist but have null/empty values
6. **Type Validation**: Check that values match expected types (text, list, object-list, multi-select)

## Output Format

### Valid Answer File
```
Validating: answers.yaml
Blueprint: platform-foundation-setup

✅ Answer file is complete!

Summary:
- Total steps: 22
- Renderable steps: 22
- All required variables provided
```

### Invalid Answer File
```
Validating: answers.yaml
Blueprint: platform-foundation-setup

⚠️ Answer file has missing or invalid values

Summary:
- Total steps: 22
- Renderable steps: 18
- Steps with issues: 4

Missing Variables:
| Variable | Required By Steps |
|----------|-------------------|
| org_admin_email | create-organization-account, provision-account-administrators |
| breakglass_accounts | create-break-glass-emergency-access |

Null Variables:
| Variable | Required By Steps |
|----------|-------------------|
| scim_admin_users | configure-scim-integration |

Steps That Cannot Render:
| Step | Missing | Null |
|------|---------|------|
| create-organization-account | org_admin_email | - |
| configure-scim-integration | - | scim_admin_users |
| provision-account-administrators | org_admin_email | - |
| create-break-glass-emergency-access | breakglass_accounts | - |

Run 'blueprints build <blueprint>' to interactively fill missing values.
```

## Implementation

1. Load the answer YAML file
2. Load the blueprint meta.yaml
3. For each step in the blueprint:
   - Find the `code.sql.jinja` and `dynamic.md.jinja` templates
   - Parse templates to find all referenced variables (using Jinja2 AST like render_journey.py)
   - Check if each variable exists in answers and is non-null
4. Aggregate results and display validation report

## Error Handling

- If answer file doesn't exist: `Error: Answer file not found: <path>`
- If answer file is invalid YAML: `Error: Invalid YAML in answer file: <error>`
- If blueprint doesn't exist: `Error: Blueprint '<name>' not found`

## Exit Codes

- `0`: Answer file is complete and valid
- `1`: Answer file has missing or invalid values
- `2`: File or blueprint not found

Now execute this by reading the specified answer file and blueprint, then performing validation.
