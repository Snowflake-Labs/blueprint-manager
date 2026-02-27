<!-- Copyright (c) YEAR Snowflake Inc. All rights reserved.
     Licensed under the Snowflake Skills License. 
     Refer to the LICENSE file in the root of this repository for full terms. -->

# Blueprints Answers Init

Generate a skeleton answer file with all questions for a blueprint.

## Usage

```
/blueprints:answers:init <blueprint-name> [options]
```

## Arguments

- `<blueprint-name>`: The blueprint ID to generate answers for

## Options

- `--output <file>`: Output file path (default: `answers_<blueprint>_<timestamp>.yaml`)
- `--project <name>`: Project to save the answer file in
- `--format <full|minimal>`: Output format (default: full)
  - `full`: Include question text and guidance as comments
  - `minimal`: Just variable names with null values

## Instructions

Generate a skeleton answer file by:

1. Loading the blueprint's meta.yaml to get the step list
2. Scanning all step templates (code.sql.jinja, dynamic.md.jinja) for required variables
3. Loading question definitions from `definitions/questions.yaml`
4. Creating a YAML file with all variables, organized by category

## Output Format (Full)

```yaml
# Blueprint: Platform Foundation Setup
# Generated: 2025-02-10 14:30:22
# 
# Instructions:
# - Fill in values for each variable below
# - Variables marked [REQUIRED] must have values for rendering
# - Run 'blueprints validate' to check completeness

# ==============================================================================
# ACCOUNT STRATEGY
# ==============================================================================

# What is your organization's Snowflake account strategy?
# Options: Single Account, Hub-and-Spoke, Multi-Account
# [REQUIRED]
account_strategy: null

# What is your Snowflake organization name?
# This is used for connectivity configuration
# [REQUIRED]
snowflake_org_name: null

# ==============================================================================
# IDENTITY MANAGEMENT
# ==============================================================================

# What identity provider will you use?
# Options: Okta, Azure AD, Other SAML Provider, Snowflake Native
identity_provider: null

# ... more variables ...
```

## Output Format (Minimal)

```yaml
# Blueprint: Platform Foundation Setup
# Generated: 2025-02-10 14:30:22

account_strategy: null
snowflake_org_name: null
identity_provider: null
# ... more variables ...
```

## Implementation

1. Load blueprint meta.yaml
2. For each step, parse templates to find referenced variables
3. Load definitions/questions.yaml
4. Match variables to questions for metadata
5. Generate organized YAML with comments
6. Write to output file

## Error Handling

- Blueprint not found: `Error: Blueprint '<name>' not found`
- Cannot write output: `Error: Cannot write to '<path>'`

## Example

```bash
# Generate full answer file
blueprints answers init platform-foundation-setup

# Generate minimal file to specific location
blueprints answers init data-product-setup --output my-answers.yaml --format minimal

# Generate in a project
blueprints answers init account-creation --project acme-corp
```

Now execute this by analyzing the blueprint and generating the skeleton answer file.
