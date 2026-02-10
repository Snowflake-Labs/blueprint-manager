# Blueprints List

List all available blueprints with their metadata.

## Instructions

Read all blueprint meta.yaml files from the `blueprints/` directory and display them in a formatted table.

For each blueprint, show:
- **Name**: The human-readable blueprint name
- **ID**: The directory name/blueprint identifier  
- **Summary**: Brief description of what the blueprint does
- **Repeatable**: Whether this blueprint can be run multiple times (Yes/No)
- **Steps**: Number of steps in the blueprint

## Output Format

Display as a markdown table:

```
| Name | ID | Summary | Repeatable | Steps |
|------|-----|---------|------------|-------|
| Platform Foundation Setup | platform-foundation-setup | Establish core platform... | No | 22 |
| Account Creation | account-creation | Create and configure... | Yes | 21 |
| Data Product Setup | data-product-setup | Set up data product... | Yes | 16 |
```

## Implementation

1. Find all `meta.yaml` files in subdirectories of the `blueprints/` folder
2. Parse each meta.yaml to extract: `name`, `summary`, `is_repeatable`, and count of `steps`
3. Skip the `images/` subdirectory (it contains images.yaml, not a blueprint)
4. Sort blueprints alphabetically by name
5. Display the results as a formatted table

## Example Output

```
Available Blueprints:

| Name | ID | Summary | Repeatable | Steps |
|------|-----|---------|------------|-------|
| Account Creation | account-creation | Create and configure new Snowflake accounts | Yes | 21 |
| Data Product Setup | data-product-setup | Set up a new data product domain | Yes | 16 |
| Platform Foundation Setup | platform-foundation-setup | Establish core platform infrastructure | No | 22 |

Total: 3 blueprints available
```

Now execute this by reading the blueprint meta.yaml files and presenting the information.
