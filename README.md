# Blueprint Manager

This repository contains infrastructure-as-code templates and blueprints for setting up Snowflake blueprints.

## Structure

- `definitions/` - Question definitions for configuration
- `blueprints/` - Available blueprint configurations
- `scripts/` - Utility scripts for rendering templates
- `answers/` - Answer files for blueprints
- `output/` - Generated infrastructure code and documentation

## Setting Up Your Blueprint using Snowflake Cortex (Recommended)

The easiest way to configure your Snowflake Blueprint is using the **Answer File Builder** skill with Snowflake Cortex. This provides a guided, interactive experience.

### Getting Started

0. Pre-requisite: Cortex Code CLI

In order to get the guided Cortex Code experience you will first need to setup the command line interface on your machine. Those instructions can be found here: https://docs.snowflake.com/LIMITEDACCESS/cortex-code/cortex-code-overview.

2. **Clone the repository:**

```bash

git clone https://github.com/Snowflake-Labs/blueprint-manager.git

cd blueprint-manager
```

2. **Start Cortex CLI:**

```bash
cortex
```

3. **Launch the skill:**

```bash
> Help me set up my Snowflake blueprint
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

## Manual Configuration (Alternative)

If you prefer to manage files directly without the guided experience:

### 1. Choose a blueprint

```bash
ls blueprints/
```

Review the blueprint's `meta.yaml` and step `overview.md` files to understand what will be configured.

### 2. Create an answer file

Copy an existing sample or create a new YAML file in `answers/<blueprint_id>/`:

```bash
mkdir -p answers/<blueprint_id>
cp answers/<blueprint_id>/sample.yaml answers/<blueprint_id>/my_answers.yaml
```

Edit the answer file to provide values for each question. See `definitions/questions.yaml` for question details and valid options.

### 3. Generate infrastructure code

```bash
python scripts/render_journey.py \
  answers/<blueprint_id>/my_answers.yaml \
  --blueprint <blueprint_id> \
  --lang sql
```

**Options:**
- `--lang sql` or `--lang terraform` — choose output language
- `--output-dir <path>` — custom output directory (default: `output/iac`)
- `--guidance-dir <path>` — custom documentation directory (default: `output/documentation`)
- `--skip-guidance` — skip generating documentation

**Output:**
- SQL/Terraform files in `output/iac/<lang>/`
- Documentation in `output/documentation/`

### 4. Execute the generated code

Review the generated SQL file, then execute it in your Snowflake worksheet. The SQL is idempotent — safe to run multiple times.
