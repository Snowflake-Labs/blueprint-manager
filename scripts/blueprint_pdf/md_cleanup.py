# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Strip duplicate header / generated Markdown TOC before PDF body conversion."""

from __future__ import annotations

import re

# HTML <details> blocks (e.g. Task Overview expanders) — body removed for PDF; no duplicate narrative.
_DETAILS_BLOCK = re.compile(r"<details\b[^>]*>.*?</details>", re.DOTALL | re.IGNORECASE)

# Emoji and common PUA / replacement glyphs that render as tofu or ■ in Helvetica
_EMOJI_AND_ARTIFACTS = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental
    "\U0001FA00-\U0001FAFF"  # extended-A
    "\U00002600-\U000026FF"  # misc symbols
    "\u200D"  # ZWJ
    "\uFE0F"  # VS16
    "\uFFFD"  # replacement char
    "\u25A0"  # black square (emoji fallback)
    "]+",
    flags=re.UNICODE,
)


def strip_generated_table_of_contents(markdown: str) -> str:
    """
    Remove the "## Table of Contents" block through the closing --- separator
    produced by generate_table_of_contents() in render_journey.py.
    """
    pattern = re.compile(
        r"(?:^|\n)## Table of Contents\n.*?\n---\n\n",
        re.DOTALL | re.MULTILINE,
    )
    return pattern.sub("\n", markdown)


def strip_leading_header_block(markdown: str) -> str:
    """
    Remove the initial render_journey header: title, blockquote metadata, first ---,
    and optional overview section up to the following ---.
    """
    s = markdown.lstrip()
    if not s.startswith("#"):
        return markdown
    sep = "\n---\n"
    pos = s.find(sep)
    if pos == -1:
        return markdown
    s = s[pos + len(sep) :].lstrip()
    if s and not s.startswith("#"):
        pos2 = s.find(sep)
        if pos2 != -1:
            s = s[pos2 + len(sep) :].lstrip()
    return s


def strip_html_details_blocks(text: str) -> str:
    """Remove <details>...</details> (Task Overview expanders, etc.)."""
    return _DETAILS_BLOCK.sub("", text)


def ensure_blank_line_before_pipe_tables(text: str) -> str:
    """
    GFM pipe tables require a blank line after preceding block text.

    Some blueprint templates use ``**Label:**`` immediately followed by ``|`` rows;
    without a blank line, python-markdown does not emit a <table> (tables break in PDF).

    (We only match ``**...:**`` here to avoid altering fenced code that may contain
    ``#`` lines before pipe characters.)
    """
    # Colon inside bold: ``**Example URLs:**`` then ``|`` row
    text = re.sub(r"(\*\*[^*]+:\*\*)\n(\|)", r"\1\n\n\2", text)
    # Colon outside bold: ``**Note**:\n|``
    text = re.sub(r"(\*\*[^*\n]+\*\*):\n(\|)", r"\1:\n\n\2", text)
    # Intro line ending with ":" (e.g. ``...`:`" before Example Names table) — Jinja ``{%-`` can remove the blank line
    text = re.sub(
        r"(^[^\n|][^\n]*:)\n(\|)",
        r"\1\n\n\2",
        text,
        flags=re.MULTILINE,
    )
    return text


def strip_emojis_and_artifacts(text: str) -> str:
    """Remove emoji and characters that render poorly in core PDF fonts."""
    return _EMOJI_AND_ARTIFACTS.sub("", text)


def strip_thematic_break_lines_for_pdf(markdown: str) -> str:
    """
    Remove standalone GFM thematic-break lines (``---``, ``***``, ``___``).

    ``render_journey`` inserts ``---`` between steps and after task intros; the PDF
    already draws ``HRFlowable`` rules under Task titles and before Step titles.
    Keeping both yields stacked double/triple horizontal lines in the PDF.
    """
    lines = markdown.split("\n")
    out: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if re.match(r"^(?:---+|\*\*\*+|___+)\s*$", stripped):
            continue
        out.append(line)
    return "\n".join(out)


def normalize_checklist_markers(text: str) -> str:
    """
    Pass-through for checklist markdown.

    ``- [ ]`` / ``- [x]`` stay as-is; the PDF renderer shows them as normal bullet
    lists (``• [ ] item``) so ASCII checkboxes stay readable in core fonts.
    """
    return text


def prepare_guidance_markdown_for_pdf(markdown: str) -> str:
    """Apply all Markdown cleanups for the guidance section."""
    text = strip_leading_header_block(markdown)
    text = strip_generated_table_of_contents(text)
    text = ensure_blank_line_before_pipe_tables(text)
    text = strip_html_details_blocks(text)
    text = strip_thematic_break_lines_for_pdf(text)
    text = strip_emojis_and_artifacts(text)
    text = normalize_checklist_markers(text)
    return text.strip() + "\n"


def prepare_executive_summary_markdown_for_pdf(markdown: str) -> str:
    """Clean executive summary markdown (optional Jinja output)."""
    text = strip_emojis_and_artifacts(markdown)
    text = normalize_checklist_markers(text)
    return text.strip() + "\n"
