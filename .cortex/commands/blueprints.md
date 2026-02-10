# Blueprints Command

Manage Snowflake blueprints, projects, and answer files.

## Usage

```
/blueprints:<subcommand> [options]
```

## Available Subcommands

### Core Commands
| Command | Description |
|---------|-------------|
| `/blueprints:list` | List available blueprints with metadata |
| `/blueprints:describe <name>` | Show blueprint details including task/step tree |
| `/blueprints:build <blueprint-name>` | Start the blueprint building process interactively |
| `/blueprints:validate <answer-file>` | Check answer file completeness against blueprint requirements |
| `/blueprints:render <answer-file>` | Generate SQL/Terraform/Documentation from answers |

### Project Management
| Command | Description |
|---------|-------------|
| `/blueprints:projects:list` | List existing projects |
| `/blueprints:projects:create <name>` | Create a new project directory structure |
| `/blueprints:projects:describe <name>` | Show project status (answers, outputs, history) |

### Answer File Operations
| Command | Description |
|---------|-------------|
| `/blueprints:answers:init <blueprint-name>` | Generate a skeleton answer file with all questions |
| `/blueprints:answers:validate <file>` | Check for missing/invalid values |
| `/blueprints:answers:diff <file1> <file2>` | Compare two answer files |

## Examples

```bash
# List all available blueprints
/blueprints:list

# View details of a specific blueprint
/blueprints:describe platform-foundation-setup

# Start building a blueprint interactively
/blueprints:build platform-foundation-setup

# Create a new project
/blueprints:projects:create my-customer-project

# Generate a skeleton answer file
/blueprints:answers:init platform-foundation-setup --output answers.yaml

# Validate an answer file
/blueprints:validate answers.yaml --blueprint platform-foundation-setup

# Render outputs from answers
/blueprints:render answers.yaml --blueprint platform-foundation-setup --lang sql
```

## Getting Started

1. **List available blueprints**: `/blueprints:list`
2. **Create a project**: `/blueprints:projects:create <project-name>`
3. **Initialize answers**: `/blueprints:answers:init <blueprint-name>`
4. **Build interactively**: `/blueprints:build <blueprint-name>` (or edit answers manually)
5. **Validate answers**: `/blueprints:validate <answer-file>`
6. **Generate outputs**: `/blueprints:render <answer-file>`

For detailed help on any subcommand, run: `/blueprints:<subcommand> --help`
