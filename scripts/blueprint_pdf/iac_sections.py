# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Split rendered IaC (SQL / Terraform) into per-step sections for PDF appendix layout."""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

# Matches ``-- ----------`` or ``# ----------`` (render_journey step band)
_STEP_BAND = re.compile(r"^(?:--|#) -{10,}\s*$")
# Second line of the band: ``-- Step 1.1: Title`` or ``-- SKIPPED Step 1.1: ...`` (Terraform uses ``#``)
_STEP_TITLE = re.compile(r"^(?:--|#)\s*(((?:SKIPPED )?Step \d+\.\d+:.*))$")


def split_rendered_iac_by_step_sections(text: str) -> List[Tuple[Optional[str], str]]:
    """
    Split concatenated journey IaC on ``render_journey`` step markers.

    Each rendered step is wrapped with::

        -- ------------------------------------------------------------
        -- Step N.M: <title>
        -- ------------------------------------------------------------

    (or ``#`` for Terraform). Returns ``(section_title, body)`` pairs; ``section_title``
    is ``None`` for the leading preamble (journey header, task banners) before the first step.
    If no markers are found, returns a single chunk ``(None, full_text)``.
    """
    raw = text.replace("\r\n", "\n")
    lines = raw.split("\n")
    n = len(lines)
    starts: List[int] = []
    i = 0
    while i <= n - 3:
        if _STEP_BAND.match(lines[i]) and _STEP_TITLE.match(lines[i + 1]) and _STEP_BAND.match(lines[i + 2]):
            starts.append(i)
            i += 3
            continue
        i += 1

    if not starts:
        return [(None, raw.rstrip("\n"))]

    out: List[Tuple[Optional[str], str]] = []
    preamble = "\n".join(lines[: starts[0]]).rstrip("\n")
    if preamble.strip():
        out.append((None, preamble))

    for j, pos in enumerate(starts):
        m = _STEP_TITLE.match(lines[pos + 1])
        title = m.group(1).strip() if m else None
        end = starts[j + 1] if j + 1 < len(starts) else n
        body = "\n".join(lines[pos:end]).rstrip("\n")
        out.append((title, body))

    return out
