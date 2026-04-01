#!/usr/bin/env python3
"""
Migration script for blueprint answer files.

Addresses backwards compatibility issues introduced when question answer types
were refactored from multi-select to single-select, and when option values were
changed for certain questions.

See scripts/TROUBLESHOOTING.md for a full description of what changed and why.

Usage:
    # Preview changes (no files written)
    .venv/bin/python scripts/migration/migrate_answers.py <answer_file.yaml> --dry-run

    # Migrate a single file (creates .bak backup first)
    .venv/bin/python scripts/migration/migrate_answers.py <answer_file.yaml>

    # Migrate all answer files under projects/
    .venv/bin/python scripts/migration/migrate_answers.py --all [--dry-run]
"""

import argparse
import glob
import os
import re
import shutil
import sys

try:
    import yaml
except ImportError:
    print("Error: pyyaml is required. Run: .venv/bin/pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
QUESTIONS_FILE = os.path.join(REPO_ROOT, "definitions", "questions.yaml")
PROJECTS_DIR = os.path.join(REPO_ROOT, "projects")

# ---------------------------------------------------------------------------
# Questions that changed from multi-select to single-select.
# If an answer file stores a YAML list for any of these keys, the migration
# converts it to a single string (first element, with a warning if >1 items).
# ---------------------------------------------------------------------------

MULTI_TO_SINGLE_SELECT = {
    "account_configure_saml",
    "account_budget_threshold",
    "account_domain",
    "account_environment",
    "account_log_level",
    "account_metric_level",
    "account_resource_monitor_action",
    "account_resource_monitor_reset_frequency",
    "account_sql_trace_query_text",
    "account_strategy",
    "account_trace_level",
    "apply_auth_policies_account_level",
    "budget_notification_threshold",
    "budget_refresh_interval",
    "configure_saml",
    "data_product_domain",
    "data_product_environment",
    "default_time_travel_days",
    "enable_account_network_policy",
    "enable_budgets",
    "enable_cost_tags",
    "enable_org_account",
    "enable_resource_monitors",
    "identity_provider",
    "mfa_enforcement_timeline",
    "new_account_edition",
    "object_component_order",
    "org_account_edition",
    "preferred_mfa_method",
    "rbac_audit_scope",
    "rbac_enable_alerts",
    "rbac_enforce_managed_access",
    "rbac_restrict_public",
    "rbac_review_frequency",
    "replication_schedule",
    "require_cost_tags",
    "resource_monitor_action",
    "resource_monitor_frequency",
    "saml_sso_login_page",
    "scim_provisioner_role",
    "security_config_approach",
}

# ---------------------------------------------------------------------------
# Option text migrations.
# Maps answer_title -> {old_value: new_value}.
# new_value may be a string (single-select) or list (multi-select).
# ---------------------------------------------------------------------------

VALUE_MIGRATIONS = {
    "mfa_method": {
        "Either TOTP or Passkey": "TOTP (Authenticator Apps)",
    },
    "additional_tag_dimensions": {
        "All (Cost Center, Owner, Project, Application)": [
            "Cost Center", "Owner", "Project", "Application"
        ],
        "Essential (Cost Center, Owner)": ["Cost Center", "Owner"],
        "Minimal (Owner only)": ["Owner"],
        "None": [],
    },
    "service_auth_methods": {
        "OAuth Only": ["OAuth"],
        "Key Pair Only": ["Key Pair"],
        "OAuth or Key Pair": ["OAuth", "Key Pair"],
        "OAuth, Key Pair, or PAT": ["OAuth", "Key Pair", "PAT"],
    },
}

# ---------------------------------------------------------------------------
# Text-based migration helpers (preserve YAML comments and formatting)
# ---------------------------------------------------------------------------

# YAML scalars that must be quoted to avoid boolean/null interpretation.
_YAML_SPECIAL = {"yes", "no", "true", "false", "null", "on", "off", "~"}


def _needs_quotes(value: str) -> bool:
    return (
        str(value).lower() in _YAML_SPECIAL
        or ":" in str(value)
        or "#" in str(value)
        or str(value).startswith("*")
        or str(value).startswith("&")
    )


def _yaml_scalar(value: str) -> str:
    """Return a safe YAML scalar representation for a string value."""
    if _needs_quotes(value):
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"
    return str(value)


def _build_line_pattern(key: str, old_value: str) -> list:
    """
    Return a list of compiled regex patterns that match a YAML line of the form:
        <indent>key: <old_value><optional trailing comment>
    Handles unquoted, single-quoted, and double-quoted value forms.
    """
    esc_key = re.escape(key)
    esc_val = re.escape(str(old_value))
    trailing = r"(\s*(?:#.*)?)$"
    return [
        re.compile(rf"^(\s*{esc_key}:\s+){esc_val}{trailing}"),
        re.compile(rf"^(\s*{esc_key}:\s+)'{esc_val}'{trailing}"),
        re.compile(rf'^(\s*{esc_key}:\s+)"{esc_val}"{trailing}'),
    ]


def _replace_scalar_to_scalar(
    content: str, key: str, old_value: str, new_value: str
) -> tuple[str, int]:
    """Replace 'key: old_value' with 'key: new_value' in raw YAML text."""
    patterns = _build_line_pattern(key, old_value)
    lines = content.split("\n")
    result = []
    count = 0
    for line in lines:
        replaced = False
        for pat in patterns:
            m = pat.match(line)
            if m:
                prefix, trailing = m.group(1), m.group(2)
                result.append(f"{prefix}{_yaml_scalar(new_value)}{trailing}")
                count += 1
                replaced = True
                break
        if not replaced:
            result.append(line)
    return "\n".join(result), count


def _replace_scalar_to_list(
    content: str, key: str, old_value: str, new_value: list
) -> tuple[str, int]:
    """Replace 'key: old_value' with a YAML block sequence for key."""
    patterns = _build_line_pattern(key, old_value)
    lines = content.split("\n")
    result = []
    count = 0
    for line in lines:
        replaced = False
        for pat in patterns:
            m = pat.match(line)
            if m:
                indent = len(line) - len(line.lstrip())
                indent_str = " " * indent
                trailing = m.group(2)
                if len(new_value) == 0:
                    result.append(f"{indent_str}{key}: []{trailing}")
                else:
                    result.append(f"{indent_str}{key}:{trailing}")
                    for item in new_value:
                        result.append(f"{indent_str}- {_yaml_scalar(item)}")
                count += 1
                replaced = True
                break
        if not replaced:
            result.append(line)
    return "\n".join(result), count


def _replace_list_to_scalar(
    content: str, key: str, old_list: list, new_value: str
) -> tuple[str, int]:
    """
    Replace a YAML block sequence for key with a scalar.
    Matches patterns like:
        key:
        - item1
        - item2
    Replaces the entire block (key line + item lines) with 'key: new_value'.
    """
    lines = content.split("\n")
    result = []
    i = 0
    count = 0
    esc_key = re.escape(key)
    key_pattern = re.compile(rf"^(\s*{esc_key}:\s*)$")

    while i < len(lines):
        m = key_pattern.match(lines[i])
        if m:
            indent = len(lines[i]) - len(lines[i].lstrip())
            indent_str = " " * indent
            # Collect following list items
            j = i + 1
            items = []
            while j < len(lines):
                item_line = lines[j]
                item_m = re.match(rf"^{indent_str}- (.+)$", item_line)
                if item_m:
                    items.append(item_m.group(1).strip().strip("'\""))
                    j += 1
                else:
                    break
            # Only replace if the collected items match old_list (order-insensitive)
            if sorted(items) == sorted(str(v) for v in old_list):
                result.append(f"{indent_str}{key}: {_yaml_scalar(new_value)}")
                i = j
                count += 1
                continue
        result.append(lines[i])
        i += 1
    return "\n".join(result), count


# ---------------------------------------------------------------------------
# Core migration logic
# ---------------------------------------------------------------------------


def detect_issues(answer_data: dict) -> list[tuple]:
    """
    Scan parsed answer data for known migration issues.
    Returns a list of (key, current_value, new_value, reason) tuples.
    """
    issues = []

    for key, value in answer_data.items():
        if value is None:
            continue

        # 1. Known option text changes
        if key in VALUE_MIGRATIONS:
            mapping = VALUE_MIGRATIONS[key]
            if value in mapping:
                issues.append(
                    (key, value, mapping[value], "option text changed in latest schema")
                )

        # 2. List stored for a now-single-select question
        elif key in MULTI_TO_SINGLE_SELECT and isinstance(value, list):
            if len(value) == 0:
                issues.append(
                    (key, value, None, "changed to single-select; empty list → null")
                )
            elif len(value) == 1:
                issues.append(
                    (
                        key, value, value[0],
                        "changed to single-select; single-item list unwrapped",
                    )
                )
            else:
                issues.append(
                    (
                        key, value, value[0],
                        (
                            f"changed to single-select; kept first value, "
                            f"discarded: {value[1:]!r}"
                        ),
                    )
                )

    return issues


def apply_migrations_to_text(content: str, issues: list[tuple]) -> str:
    """Apply all detected issues as text-based replacements, preserving comments."""
    for key, old_val, new_val, _reason in issues:
        if isinstance(old_val, list) and not isinstance(new_val, list):
            # list → scalar (multi-select list stored for now-single-select question)
            content, _n = _replace_list_to_scalar(content, key, old_val, new_val or "")
        elif isinstance(new_val, list):
            # scalar → list  (e.g. additional_tag_dimensions, service_auth_methods)
            content, _n = _replace_scalar_to_list(content, key, str(old_val), new_val)
        else:
            # scalar → scalar  (e.g. mfa_method)
            content, _n = _replace_scalar_to_scalar(
                content, key, str(old_val), str(new_val) if new_val is not None else ""
            )
    return content


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


def load_answer_file(path: str) -> tuple[str, dict]:
    """Return (raw_text, parsed_dict). Raises on YAML error."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    data = yaml.safe_load(content)
    return content, (data or {})


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def backup_file(path: str) -> str:
    backup_path = path + ".bak"
    shutil.copy2(path, backup_path)
    return backup_path


# ---------------------------------------------------------------------------
# Process a single file
# ---------------------------------------------------------------------------


def process_file(path: str, dry_run: bool = False) -> bool:
    """
    Detect and apply migrations for a single answer file.
    Returns True if changes were made (or would be made in dry-run mode).
    """
    label = f"[DRY RUN] " if dry_run else ""
    print(f"\n{label}Processing: {path}")

    try:
        content, data = load_answer_file(path)
    except yaml.YAMLError as exc:
        print(f"  ERROR: YAML parse error — {exc}")
        print("  Tip: see scripts/TROUBLESHOOTING.md §4 for YAML syntax help.")
        return False
    except OSError as exc:
        print(f"  ERROR: Could not read file — {exc}")
        return False

    if not data:
        print("  Skipped: file is empty.")
        return False

    issues = detect_issues(data)

    if not issues:
        print("  No migration needed.")
        return False

    print(f"  Found {len(issues)} change(s):")
    for key, old_val, new_val, reason in issues:
        print(f"    - {key}:")
        print(f"        old:    {old_val!r}")
        print(f"        new:    {new_val!r}")
        print(f"        reason: {reason}")

    if not dry_run:
        new_content = apply_migrations_to_text(content, issues)
        backup_path = backup_file(path)
        write_file(path, new_content)
        print(f"  Backup: {backup_path}")
        print(f"  Updated: {path}")
    else:
        print("  (No files written — dry-run mode)")

    return True


# ---------------------------------------------------------------------------
# Discover all answer files
# ---------------------------------------------------------------------------


def find_all_answer_files() -> list[str]:
    pattern = os.path.join(PROJECTS_DIR, "**", "answers", "**", "*.yaml")
    return sorted(f for f in glob.glob(pattern, recursive=True) if not f.endswith(".bak"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate blueprint answer files to be compatible with the latest schema.\n"
            "See scripts/TROUBLESHOOTING.md for details on what changed."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "answer_file",
        nargs="?",
        metavar="ANSWER_FILE",
        help="Path to a specific answer file to migrate.",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help=f"Migrate all answer files found under {PROJECTS_DIR}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing any files.",
    )
    args = parser.parse_args()

    if args.all:
        files = find_all_answer_files()
        if not files:
            print(f"No answer files found under: {PROJECTS_DIR}")
            sys.exit(0)
        print(f"Found {len(files)} answer file(s) to inspect.")
        changed = sum(
            1 for f in files if process_file(f, dry_run=args.dry_run)
        )
        verb = "would be updated" if args.dry_run else "updated"
        print(f"\nDone. {changed}/{len(files)} file(s) {verb}.")
    else:
        if not os.path.isfile(args.answer_file):
            print(f"Error: file not found: {args.answer_file}")
            sys.exit(1)
        changed = process_file(args.answer_file, dry_run=args.dry_run)
        if not changed:
            print("\nNo changes needed.")
        else:
            verb = "would be updated" if args.dry_run else "updated"
            print(f"\nDone. File {verb}.")


if __name__ == "__main__":
    main()
