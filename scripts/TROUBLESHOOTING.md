# Blueprint Manager — Troubleshooting Guide

## Table of Contents

1. [Outdated Answer Files: Type & Option Migrations](#1-outdated-answer-files-type--option-migrations)
2. [Running the Migration Script](#2-running-the-migration-script)
3. [Render Script Errors](#3-render-script-errors)
4. [YAML Syntax Errors](#4-yaml-syntax-errors)
5. [Python Environment Issues](#5-python-environment-issues)
6. [Missing or Mismatched Question Definitions](#6-missing-or-mismatched-question-definitions)

---

## 1. Outdated Answer Files: Type & Option Migrations

If you see any of the following symptoms, your answer file was created before a breaking
schema change and needs to be migrated:

- `ValueError: Invalid answer for '<key>': '...' is not a valid option.`
- Render completes but steps are silently skipped or empty

Run the migration script — it detects and fixes all known issues automatically.
See [Section 2](#2-running-the-migration-script).

---

## 2. Running the Migration Script

The migration script at `scripts/migration/migrate_answers.py` detects and fixes all known
backwards compatibility issues automatically.

### Prerequisites

The script uses only `pyyaml`, which is included in the project's virtual environment:

```bash
# Verify the venv is available
ls .venv/bin/python
```

### Migrate a Single Answer File

```bash
# Preview changes without writing (recommended first step)
.venv/bin/python scripts/migration/migrate_answers.py path/to/answers.yaml --dry-run

# Apply migrations (creates a .bak backup of the original first)
.venv/bin/python scripts/migration/migrate_answers.py path/to/answers.yaml
```

**Example:**

```bash
.venv/bin/python scripts/migration/migrate_answers.py \
  projects/TechCorp/answers/platform-foundation-setup/answers_techcorp.yaml --dry-run
```

### Migrate All Answer Files in the Project

```bash
# Dry run across all projects
.venv/bin/python scripts/migration/migrate_answers.py --all --dry-run

# Apply migrations to all answer files
.venv/bin/python scripts/migration/migrate_answers.py --all
```

### Output

The script prints a summary of every change applied:

```
Processing: projects/TechCorp/answers/platform-foundation-setup/answers_techcorp.yaml
  Found 2 change(s):
    - mfa_method:
        old: 'Either TOTP or Passkey'
        new: 'TOTP (Authenticator Apps)'
        reason: option text changed in latest schema
    - service_auth_methods:
        old: 'OAuth or Key Pair'
        new: ['OAuth', 'Key Pair']
        reason: option text changed in latest schema
  Backup saved to: ...answers_techcorp.yaml.bak
  File updated: ...answers_techcorp.yaml
```

### After Migration

After running the migration script, verify the answer file renders correctly:

```bash
.venv/bin/python scripts/render_journey.py \
  path/to/answers.yaml \
  --blueprint <blueprint_id> \
  --lang sql \
  --project <project_name>
```

If the render still fails, check section [3](#3-render-script-errors) below.

---

## 3. Render Script Errors

### `KeyError` or `UndefinedError` in Jinja2 template

**Cause:** An answer key referenced in a template does not exist in the answer file.

**Fix:** Run `blueprints answers validate` to see which required keys are missing, then add
them to your answer file.

### Steps are silently skipped

**Cause:** A conditional in a `code.sql.jinja` or `dynamic.md.jinja` template evaluated to
`false` because the answer value doesn't match the expected option text exactly.

**Fix:**
1. Check the template's condition (e.g., `{% if answers.enable_budgets == 'Yes' %}`).
2. Verify the answer file has the exact matching string (case-sensitive).
3. Run the migration script if the value was created before the latest schema update.

### `yaml.scanner.ScannerError` when loading answer file

**Cause:** The answer file contains invalid YAML syntax.

**Fix:** See [Section 4](#4-yaml-syntax-errors).

---

## 4. YAML Syntax Errors

### Common mistakes

**Unquoted special values**

YAML interprets bare `Yes`, `No`, `True`, `False`, `Null` as booleans or null. Always quote
these when they are meant as strings:

```yaml
# Wrong — parsed as boolean true
rbac_restrict_public: Yes

# Correct — parsed as string "Yes"
rbac_restrict_public: 'Yes'
```

**Colon in a value**

```yaml
# Wrong — YAML interprets the colon as a key separator
description: My product: v2

# Correct
description: 'My product: v2'
```

**Inconsistent list indentation**

```yaml
# Wrong
allowed_network_rules:
- rule_name: corporate
  ip_addresses: 10.0.0.0/8
 - rule_name: vpn   # wrong indentation

# Correct
allowed_network_rules:
- rule_name: corporate
  ip_addresses: 10.0.0.0/8
- rule_name: vpn
  ip_addresses: 203.0.113.1
```

### Validating YAML syntax

```bash
.venv/bin/python -c "import yaml; yaml.safe_load(open('path/to/answers.yaml'))" && echo "OK"
```

---

## 5. Python Environment Issues

### `ModuleNotFoundError: No module named 'yaml'`

The project uses a local virtual environment. Use `.venv/bin/python` instead of the system
`python`:

```bash
# Wrong
python scripts/render_journey.py ...

# Correct
.venv/bin/python scripts/render_journey.py ...
```

### Recreating the virtual environment

```bash
python3 -m venv .venv
.venv/bin/pip install jinja2 pyyaml
```

---

## 6. Missing or Mismatched Question Definitions

### `answer_title` not found in `definitions/questions.yaml`

**Cause:** The answer file references a key that does not match any `answer_title` in
`questions.yaml`. This can happen if a question was renamed in a schema update.

**Fix:**
1. Check `definitions/questions.yaml` for the correct `answer_title`.
2. Update the key in your answer file to match.

### Answer file has keys not used by the blueprint

This is harmless — extra keys in an answer file are ignored by `render_journey.py`.
However, if you are auditing your answer file, run:

```bash
blueprints answers validate path/to/answers.yaml --blueprint <blueprint_id>
```
