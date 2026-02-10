# Create Blueprint Command (Deprecated)

> **Note:** This command has been renamed to `blueprints build`. 
> Please use `blueprints build <blueprint-name>` instead.
>
> This alias is preserved for backwards compatibility.

Invoke the blueprint-builder skill to guide the user through creating a Snowflake Blueprint configuration.

## Migration Guide

The `create-blueprint` command has been replaced by a comprehensive `blueprints` command with multiple subcommands:

| Old Command | New Command |
|-------------|-------------|
| `create-blueprint` | `blueprints build <blueprint-name>` |

### New Commands Available

- `blueprints list` - List available blueprints
- `blueprints describe <name>` - Show blueprint details
- `blueprints build <name>` - Build a blueprint interactively
- `blueprints validate <file>` - Validate an answer file
- `blueprints render <file>` - Generate outputs from answers
- `blueprints projects list` - List projects
- `blueprints projects create <name>` - Create a project
- `blueprints answers init <name>` - Generate skeleton answers

Run `blueprints` for full command documentation.

---

$blueprint-builder Help me set up my Snowflake blueprint
