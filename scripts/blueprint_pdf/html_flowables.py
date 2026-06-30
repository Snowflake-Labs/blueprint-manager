# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Convert Markdown (via HTML) to ReportLab flowables."""

from __future__ import annotations

import html
import re
from typing import Any, List, Optional, Union

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

from blueprint_pdf.branding import BORDER_LIGHT, CODE_BG, CONTENT_WIDTH, SNOWFLAKE_NAVY

# Horizontal padding inside shaded code blocks (points); keeps Preformatted wrap width sane.
_CODE_BLOCK_PAD = 10

_TASK_H1 = re.compile(r"^Task\s+\d+:", re.I)
_STEP_H2 = re.compile(r"^Step\s+\d+\.\d+:", re.I)
_LEADING_BR = re.compile(r"^(?:<br\s*/?>|\s)+", re.I)
_TRAILING_BR = re.compile(r"(?:<br\s*/?>|\s)+$", re.I)
def _escape_para_fragment(text: str) -> str:
    return (
        html.escape(text, quote=False)
        .replace("\n", "<br/>")
    )


def _inline_markup_from_element(node: Tag) -> str:
    """Build ReportLab Paragraph mini-HTML from inline phrasing content."""
    parts: List[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            parts.append(_escape_para_fragment(str(child)))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in ("strong", "b"):
            parts.append(f"<b>{_escape_para_fragment(child.get_text())}</b>")
        elif name in ("em", "i"):
            parts.append(f"<i>{_escape_para_fragment(child.get_text())}</i>")
        elif name == "code":
            parts.append(f"<font face='Courier'>{_escape_para_fragment(child.get_text())}</font>")
        elif name == "br":
            parts.append("<br/>")
        elif name == "a":
            parts.append(_escape_para_fragment(child.get_text()))
        else:
            parts.append(_inline_markup_from_element(child))
    return "".join(parts)


def _paragraph_from_tag(p: Tag, style: ParagraphStyle) -> Paragraph:
    inner = _inline_markup_from_element(p)
    if not inner.strip():
        inner = _escape_para_fragment(p.get_text())
    return Paragraph(inner, style)


def _normalize_ordered_lists(soup: Tag) -> None:
    """Preserve optional start index for PDF; drop native ``start`` so browsers ignore it."""
    for ol in soup.find_all("ol"):
        if "start" in ol.attrs:
            ol["data-rl-start"] = ol["start"]
            del ol["start"]


def _nested_list_as_inline_markup(list_tag: Tag) -> str:
    """Render a nested ul/ol as mini-HTML (for inside a list-item Paragraph)."""
    name = list_tag.name.lower()
    pieces: List[str] = []
    n = 0
    for li in list_tag.find_all("li", recursive=False):
        if name == "ol":
            n += 1
            prefix = f"<br/>{n}. "
        else:
            prefix = "<br/>\u2022 "
        inner = _list_item_inner_markup(li)
        if inner.strip():
            pieces.append(f"{prefix}{inner}")
    return "".join(pieces)


def _list_item_inner_markup(li: Tag) -> str:
    """
    Build Paragraph mini-HTML for one ``<li>``.

    Skips whitespace-only text nodes between ``<li>`` and ``<p>`` (they become
    stray ``<br/>`` and break ReportLab list layout). Handles nested lists.
    """
    parts: List[str] = []
    for child in li.children:
        if isinstance(child, NavigableString):
            if not str(child).strip():
                continue
            parts.append(_escape_para_fragment(str(child)))
            continue
        if not isinstance(child, Tag):
            continue
        nm = child.name.lower()
        if nm == "p":
            parts.append(_inline_markup_from_element(child))
        elif nm in ("ul", "ol"):
            parts.append(_nested_list_as_inline_markup(child))
        else:
            parts.append(_inline_markup_from_element(child))
    inner = "".join(parts)
    inner = _LEADING_BR.sub("", inner)
    inner = _TRAILING_BR.sub("", inner)
    return inner


def _ordered_list_flowables(ol: Tag, styles: dict) -> List[Any]:
    """One Paragraph per item: ``1.`` inline with text (consistent with markdown)."""
    try:
        start = int(ol.get("data-rl-start", 1) or 1)
    except (TypeError, ValueError):
        start = 1
    lis = ol.find_all("li", recursive=False)
    if not lis:
        return []
    lst_style = styles["BodyListItem"]
    out: List[Any] = []
    for i, li in enumerate(lis, start=start):
        inner = _list_item_inner_markup(li)
        if not inner.strip():
            continue
        out.append(Paragraph(f"{i}. {inner}", lst_style))
    out.append(Spacer(1, 6))
    return out


def _unordered_list_flowables(ul: Tag, styles: dict) -> List[Any]:
    """One Paragraph per item with a bullet (avoids ListFlowable layout quirks)."""
    lis = ul.find_all("li", recursive=False)
    if not lis:
        return []
    lst_style = styles["BodyListItem"]
    out: List[Any] = []
    for li in lis:
        inner = _list_item_inner_markup(li)
        if not inner.strip():
            continue
        out.append(Paragraph(f"\u2022 {inner}", lst_style))
    out.append(Spacer(1, 6))
    return out


def appendix_cell_inner_width_pt() -> float:
    """Usable width inside the shaded appendix cell (points), with a small safety margin."""
    return max(80.0, CONTENT_WIDTH - 2 * _CODE_BLOCK_PAD - 6)


def _split_long_line_mono(line: str, font_name: str, font_size: float, max_w: float) -> List[str]:
    """Break one logical line into segments each fitting ``max_w`` when drawn in ``font_name``."""
    if not line:
        return [""]
    if stringWidth(line, font_name, font_size) <= max_w:
        return [line]
    parts: List[str] = []
    rest = line
    while rest:
        if stringWidth(rest, font_name, font_size) <= max_w:
            parts.append(rest)
            break
        lo, hi = 1, len(rest)
        best = 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if stringWidth(rest[:mid], font_name, font_size) <= max_w:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        if best < 1:
            best = 1
        parts.append(rest[:best])
        rest = rest[best:]
    return parts


def wrap_text_to_mono_cell_width(text: str, styles: dict) -> str:
    """
    Wrap each line so ``stringWidth(line) <= appendix_cell_inner_width_pt()`` for ``BodyMono``.

    ``Preformatted``'s ``maxLineLength`` is a character count and can still draw past the grey
    box for long identifiers; this uses PDF metrics instead.
    """
    mono = styles["BodyMono"]
    fn = mono.fontName
    fs = float(getattr(mono, "fontSize", 8.5) or 8.5)
    max_w = appendix_cell_inner_width_pt()
    out: List[str] = []
    for line in text.replace("\r\n", "\n").split("\n"):
        line = line.expandtabs(4)
        out.extend(_split_long_line_mono(line, fn, fs, max_w))
    return "\n".join(out)


def shaded_preformatted_appendix_table(
    code: str,
    styles: dict,
    *,
    lines_per_subrow: int = 6,
) -> Table:
    """
    Appendix IaC: one logical gray block implemented as **multiple table rows** so
    ``splitByRow=1`` can break across pages (avoids a huge blank when a step does not fit).

    Each row is a short ``Preformatted`` slice so a partial step can start at the bottom of
    a page and continue on the next. Lines are wrapped with :func:`wrap_text_to_mono_cell_width`
    so they stay inside the shaded area (``Preformatted``'s character-based ``maxLineLength``
    is not used).
    """
    text = wrap_text_to_mono_cell_width(code, styles)
    mono = styles["BodyMono"]
    raw_lines = text.split("\n")
    if not raw_lines or not any(line.strip() for line in raw_lines):
        raw_lines = [" "]
    n = len(raw_lines)

    step = max(1, int(lines_per_subrow))
    data: List[List[Preformatted]] = []
    for i in range(0, n, step):
        chunk = "\n".join(raw_lines[i : i + step])
        if not chunk.strip():
            chunk = " "
        # Lines are already width-broken; do not use maxLineLength (char-based) or long tokens
        # can still overflow the grey box.
        data.append([Preformatted(chunk, mono)])

    tbl = Table(data, colWidths=[CONTENT_WIDTH], repeatRows=0, splitByRow=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
                ("RIGHTPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
                ("TOPPADDING", (0, 0), (0, 0), _CODE_BLOCK_PAD),
                ("BOTTOMPADDING", (0, -1), (-1, -1), _CODE_BLOCK_PAD),
                ("TOPPADDING", (0, 1), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -2), 2),
            ]
        )
    )
    return tbl


def shaded_preformatted_block_table(
    code: str,
    styles: dict,
    *,
    max_line_length: Optional[int] = None,
) -> Table:
    """
    Single-cell table: monospace ``Preformatted`` on ``CODE_BG`` with a light border.

    Used for markdown fenced blocks and for the IaC appendix (possibly one table per step).
    """
    text = code.replace("\r\n", "\n").rstrip("\n")
    if not text.strip():
        text = " "

    mono = styles["BodyMono"]
    fs = float(getattr(mono, "fontSize", 8.5) or 8.5)
    inner_pts = max(120.0, CONTENT_WIDTH - 2 * _CODE_BLOCK_PAD)
    if max_line_length is not None:
        max_len = max(32, int(max_line_length))
    else:
        max_len = max(48, int(inner_pts / (fs * 0.6)))

    pre = Preformatted(text, mono, maxLineLength=max_len)
    tbl = Table([[pre]], colWidths=[CONTENT_WIDTH])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
                ("RIGHTPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
                ("TOPPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
                ("BOTTOMPADDING", (0, 0), (-1, -1), _CODE_BLOCK_PAD),
            ]
        )
    )
    return tbl


def _shaded_code_block_flowables(code: str, styles: dict) -> List[Any]:
    """
    Render fenced / ``<pre>`` code as a full-width shaded box (distinct from body text).

    Uses a single-cell Table so BACKGROUND + BOX apply reliably around ``Preformatted``.
    """
    text = code.replace("\r\n", "\n").rstrip("\n")
    if not text.strip():
        return [Spacer(1, 2)]
    return [Spacer(1, 4), shaded_preformatted_block_table(text, styles), Spacer(1, 8)]


def _heading_flowables(tag: str, raw_text: str, styles: dict) -> List[Any]:
    """Map HTML headings to Task/Step (TOC) vs body headings; add visual separation."""
    t = " ".join(raw_text.split()).strip()
    esc = html.escape(t)
    out: List[Any] = []

    if tag == "h1" and _TASK_H1.match(t):
        out.append(Spacer(1, 8))
        out.append(Paragraph(esc, styles["TaskHeading"]))
        out.append(
            HRFlowable(
                width="100%",
                thickness=0.75,
                color=BORDER_LIGHT,
                spaceBefore=4,
                spaceAfter=10,
            )
        )
        return out

    if tag == "h2" and _STEP_H2.match(t):
        out.append(Spacer(1, 10))
        out.append(
            HRFlowable(
                width="100%",
                thickness=0.5,
                color=BORDER_LIGHT,
                spaceBefore=2,
                spaceAfter=6,
            )
        )
        out.append(Paragraph(esc, styles["StepHeading"]))
        return out

    if tag == "h1":
        return [Paragraph(esc, styles["BodyHeading2"])]
    if tag == "h2":
        return [Paragraph(esc, styles["BodyHeading2"])]
    return [Paragraph(esc, styles["BodyHeading3"])]


def markdown_to_flowables(
    md_text: str,
    styles: dict,
) -> List[Any]:
    """Render Markdown to a list of Platypus flowables."""
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    html_str = md.convert(md_text)
    soup = BeautifulSoup(f"<div id='root'>{html_str}</div>", "html.parser")
    root = soup.find(id="root")
    if root is None:
        return []
    _normalize_ordered_lists(root)
    flowables: List[Any] = []
    for child in root.children:
        if isinstance(child, NavigableString) and not str(child).strip():
            continue
        flowables.extend(_flowable_for_node(child, styles))
    return flowables


def _flowable_for_node(node: Any, styles: dict) -> List[Any]:
    if isinstance(node, NavigableString):
        text = str(node).strip()
        if not text:
            return []
        return [Paragraph(_escape_para_fragment(text), styles["Body"])]

    if not isinstance(node, Tag):
        return []

    name = node.name.lower()

    if name in ("h1", "h2", "h3"):
        return _heading_flowables(name, node.get_text(), styles)

    if name == "p":
        return [_paragraph_from_tag(node, styles["Body"])]

    if name == "ol":
        return _ordered_list_flowables(node, styles)

    if name == "ul":
        return _unordered_list_flowables(node, styles)

    if name == "blockquote":
        inner = _inline_markup_from_element(node) or _escape_para_fragment(node.get_text())
        return [Paragraph(inner, styles["BlockQuote"])]

    if name == "pre":
        return _shaded_code_block_flowables(node.get_text(), styles)

    if name == "hr":
        return [
            HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceBefore=6, spaceAfter=6),
        ]

    if name == "table":
        return [_table_from_html(node, styles)]

    if name == "details":
        # Stripped in prepare_guidance_markdown_for_pdf; no-op if any remain.
        return []

    if name in ("div", "section", "article", "body"):
        out: List[Any] = []
        for sub in node.children:
            out.extend(_flowable_for_node(sub, styles))
        return out

    out = []
    for sub in node.children:
        out.extend(_flowable_for_node(sub, styles))
    return out


def _table_from_html(table: Tag, styles: dict) -> Union[Table, Spacer]:
    rows_html = table.find_all("tr")
    if not rows_html:
        return Spacer(1, 1)

    header_style = styles["TableHeaderCell"]
    cell_style = styles["TableCell"]

    data: List[List[Any]] = []
    for ri, tr in enumerate(rows_html):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue
        row: List[Any] = []
        is_header_row = all(c.name == "th" for c in cells)
        for c in cells:
            txt = _truncate_table_cell(c.get_text())
            esc = html.escape(txt)
            if ri == 0 and is_header_row:
                row.append(Paragraph(esc, header_style))
            else:
                row.append(Paragraph(esc, cell_style))
        if row:
            data.append(row)

    if not data:
        return Spacer(1, 1)

    ncols = len(data[0])
    col_w = CONTENT_WIDTH / ncols
    t = Table(data, colWidths=[col_w] * ncols, repeatRows=1 if _first_row_is_header(rows_html) else 0)

    style_cmds = [
        ("GRID", (0, 0), (-1, -1), 0.25, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if _first_row_is_header(rows_html):
        style_cmds.insert(
            0,
            ("BACKGROUND", (0, 0), (-1, 0), CODE_BG),
        )
    t.setStyle(TableStyle(style_cmds))
    return t


def _first_row_is_header(rows_html: List[Tag]) -> bool:
    if not rows_html:
        return False
    cells = rows_html[0].find_all(["th", "td"])
    return bool(cells) and all(c.name == "th" for c in cells)


def _truncate_table_cell(text: str, max_len: int = 1200) -> str:
    t = text.replace("\r\n", "\n").strip()
    if len(t) > max_len:
        return t[: max_len - 3] + "..."
    return t


def wrap_sql_text(sql: str, width: int = 92) -> str:
    """Wrap long lines for monospace appendix (deterministic splits)."""
    lines = sql.replace("\r\n", "\n").split("\n")
    out_lines = []
    for line in lines:
        if len(line) <= width:
            out_lines.append(line)
            continue
        chunk = line
        while len(chunk) > width:
            out_lines.append(chunk[:width])
            chunk = chunk[width:]
        if chunk:
            out_lines.append(chunk)
    return "\n".join(out_lines)
