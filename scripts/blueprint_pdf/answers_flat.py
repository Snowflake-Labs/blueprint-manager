# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Flatten answers.yaml into (key_path, value) rows for PDF tables."""

from __future__ import annotations

from typing import Any, List, Tuple


def flatten_answers(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """
    Flatten a nested mapping/list structure into display rows.

    Keys use dot notation and bracket indices, e.g. zone_list[0], manual_admin_users[0].email.
    """
    rows: List[Tuple[str, str]] = []

    if isinstance(obj, dict):
        if not obj:
            rows.append((prefix or "(empty)", ""))
            return rows
        for key in sorted(obj.keys(), key=lambda k: str(k)):
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_answers(obj[key], path))
    elif isinstance(obj, list):
        if not obj:
            rows.append((prefix or "(empty list)", ""))
            return rows
        for i, item in enumerate(obj):
            path = f"{prefix}[{i}]"
            rows.extend(flatten_answers(item, path))
    else:
        if obj is None:
            val = ""
        elif isinstance(obj, bool):
            val = "true" if obj else "false"
        else:
            val = str(obj)
        rows.append((prefix, val))

    return rows


def format_cell(value: str, max_len: int = 2000) -> str:
    """Truncate very long scalar values for table cells."""
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if len(value) > max_len:
        return value[: max_len - 3] + "..."
    return value
