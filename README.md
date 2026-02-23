# Blueprint Manager

This repository contains infrastructure-as-code templates and blueprints for setting up Snowflake blueprints.

## Structure

- `definitions/` - Question definitions for configuration
- `blueprints/` - Available blueprint configurations
- `scripts/` - Utility scripts for rendering templates
- `projects/` - Project workspaces for organizing answers and outputs
- `output/` - Generated infrastructure code and documentation

## Setting Up Your Blueprint using Snowflake Cortex (Recommended)

The easiest way to configure your Snowflake Blueprint is using the **Blueprint Builder** skill with Snowflake Cortex. This provides a guided, interactive experience.

### Getting Started

0. Pre-requisite: Cortex Code CLI

In order to get the guided Cortex Code experience you will first need to setup the command line interface on your machine. Those instructions can be found here: https://docs.snowflake.com/LIMITEDACCESS/cortex-code/cortex-code-overview.

1. **Clone the repository:**

```bash
git clone https://github.com/Snowflake-Labs/blueprint-manager.git
cd blueprint-manager
```

2. **Start Cortex CLI:**

```bash
cortex
```

3. **Launch the Blueprint Builder:**

```bash
/blueprints:build platform-foundation-setup
```

### How it works:

1. **Choose your approach:**
   - **Option A:** Provide a description of your organization (size, use case, security requirements, etc.) and Cortex will intelligently configure as many settings as possible
   - **Option B:** Go through each question step-by-step with full guidance

2. **Review the configuration** — Cortex shows you:
   - ✅ Questions it answered automatically (with reasoning)
   - ❓ Questions that need your input (account names, emails, etc.)
   - ⚠️ Questions that need more context from you

3. **Generate SQL** — once your answers are complete, Cortex runs the render script to produce ready-to-execute Snowflake SQL

### Benefits:
- No need to understand the answer file format
- Intelligent defaults based on your organization profile
- Clear explanation of each configuration decision
- Validation and guidance throughout the process

## Cortex Code Commands

The following commands are available when using Cortex Code in this repository:

### Core Commands

| Command | Description |
|---------|-------------|
| `/blueprints:list` | List available blueprints with metadata |
| `/blueprints:describe <name>` | Show blueprint details including task/step tree |
| `/blueprints:build <name>` | Start the interactive blueprint building process |
| `/blueprints:validate <file> --blueprint <name>` | Check answer file completeness |
| `/blueprints:render <file> --blueprint <name>` | Generate SQL/Terraform/Documentation from answers |

### Project Management

| Command | Description |
|---------|-------------|
| `/blueprints:projects:list` | List existing projects |
| `/blueprints:projects:create <name>` | Create a new project directory structure |
| `/blueprints:projects:describe <name>` | Show project status (answers, outputs, history) |

### Answer File Operations

| Command | Description |
|---------|-------------|
| `/blueprints:answers:init <name>` | Generate a skeleton answer file with all questions |
| `/blueprints:answers:validate <file>` | Check for missing/invalid values |
| `/blueprints:answers:diff <file1> <file2>` | Compare two answer files |

### Example Workflow

```bash
# 1. List available blueprints
/blueprints:list

# 2. Create a project for your work
/blueprints:projects:create my-company

# 3. Start building interactively
/blueprints:build platform-foundation-setup --project my-company

# 4. Or generate a skeleton and fill manually
/blueprints:answers:init platform-foundation-setup --project my-company

# 5. Validate your answers
/blueprints:validate answers.yaml --blueprint platform-foundation-setup

# 6. Generate SQL output
/blueprints:render answers.yaml --blueprint platform-foundation-setup --project my-company
```

## Skills

This repository includes two Cortex Code skills that are automatically activated:

### Blueprint Builder

Guides users through constructing answer files interactively. Triggered when you:
- Ask to set up or configure a blueprint
- Want to create your Snowflake environment
- Need help with blueprint configuration

### Snowflake Best Practices

Provides curated guidance from Snowflake SMEs. Triggered when you ask about:
- Best practices or recommendations
- Account strategy, RBAC, security patterns
- Cost management and resource monitoring
- Naming conventions and architecture decisions

## Schema Reference

### Blueprint `meta.yaml` Schema

Each blueprint contains a `meta.yaml` file that defines its structure. The schema supports both flat (steps-only) and nested (tasks with steps) formats for backwards compatibility.

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `blueprint_id` | string | Unique identifier for the blueprint |
| `name` | string | Display name for the blueprint |
| `summary` | string | Brief description of the blueprint's purpose |
| `overview` | string | Detailed description of what the blueprint accomplishes |
| `steps` | list | List of step slugs (references to step directories) |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `is_repeatable` | boolean | Whether the blueprint can be run multiple times (default: false) |
| `tasks` | list | Groupings of steps with metadata (see below) |

#### Tasks Structure

The `tasks` field enables grouping steps into logical units with explicit metadata. This provides context about what each group accomplishes, who should perform it, and what prerequisites are required.

```yaml
tasks:
  - slug: string              # Unique identifier for the task (e.g., "platform-planning")
    title: string             # Display title for the task
    summary: string           # Short summary of what will be accomplished
    role_requirements:        # Snowflake role requirements
      - string
    external_requirements:    # External requirements (SSO, data integration sources, etc.)
      - string
    personas:                 # Personas/roles needed for this task
      - string
    description: string       # Optional detailed content for the Skill and future UI
    steps:                    # Steps that belong to this task
      - slug: string          # Reference to step slug in the blueprint's steps list
        title: string         # Display title for the step within this task
```

#### Example: Minimal Blueprint (flat, without tasks)

```yaml
blueprint_id: blueprint_abc123
name: Simple Setup
summary: Basic configuration workflow
overview: A straightforward setup process.
steps:
  - step-one
  - step-two
  - step-three
```

#### Example: Full Blueprint (with tasks)

```yaml
blueprint_id: blueprint_def456
name: Platform Foundation Setup
summary: Establish core platform infrastructure
overview: Complete platform setup workflow.
is_repeatable: false
steps:
  - determine-account-strategy
  - configure-organization-name
  - create-infrastructure-database
tasks:
  - slug: platform-foundation
    title: Platform Foundation
    summary: Define account strategy and create shared infrastructure.
    external_requirements:
      - Snowflake account (trial or provisioned)
      - Organization information
    personas:
      - Platform Administrator
      - Cloud/Infrastructure Team
    role_requirements:
      - ORGADMIN or ACCOUNTADMIN privileges
    steps:
      - slug: determine-account-strategy
        title: Determine Account Strategy
      - slug: configure-organization-name
        title: Configure Organization Name
      - slug: create-infrastructure-database
        title: Create Infrastructure Database
```

#### Task Content Files

Task overview content can also be stored in separate markdown files using a flat directory structure:

```
blueprints/<blueprint-name>/
├── meta.yaml
├── overview.md
├── tasks/
│   ├── platform-planning.md      # Flat structure (recommended)
│   ├── security-setup.md
│   └── cost-management.md
└── <step-slug>/
    ├── overview.md
    ├── code.sql.jinja
    └── dynamic.md.jinja
```

The task markdown files can include additional details like time estimates, key decisions, and deliverables that supplement the structured fields in `meta.yaml`.

## Manual Configuration (Alternative)

If you prefer to manage files directly without the guided experience:

### 1. Choose a blueprint

```bash
ls blueprints/
```

Review the blueprint's `meta.yaml` and step `overview.md` files to understand what will be configured.

### 2. Create a project and answer file

Create a project directory structure:

```bash
# Create project structure
mkdir -p projects/my-project/answers/<blueprint_id>
mkdir -p projects/my-project/output/iac/sql
mkdir -p projects/my-project/output/documentation
```

Create an answer file (e.g., `projects/my-project/answers/<blueprint_id>/my_answers.yaml`) and provide values for each question. See `definitions/questions.yaml` for question details and valid options.

### 3. Generate infrastructure code

```bash
python scripts/render_journey.py \
  projects/my-project/answers/<blueprint_id>/my_answers.yaml \
  --blueprint <blueprint_id> \
  --project my-project \
  --lang sql
```

**Options:**
- `--lang sql` or `--lang terraform` — choose output language
- `--project <name>` — project name for organizing outputs
- `--skip-guidance` — skip generating documentation

**Output:**
- SQL/Terraform files in `projects/<project>/output/iac/sql/`
- Documentation in `projects/<project>/output/documentation/`

### 4. Execute the generated code

Review the generated SQL file, then execute it in your Snowflake worksheet. The SQL is idempotent — safe to run multiple times.
