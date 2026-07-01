# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Orchestrate Snowflake-styled Blueprint PDF generation (ReportLab)."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from blueprint_pdf.answers_flat import flatten_answers, format_cell as format_answer_cell
from blueprint_pdf.branding import (
    BORDER_LIGHT,
    CODE_BG,
    CONTENT_WIDTH,
    MARGIN_BOTTOM,
    MARGIN_LEFT,
    MARGIN_RIGHT,
    MARGIN_TOP,
    SNOWFLAKE_CYAN,
    SNOWFLAKE_NAVY,
    TEXT_MUTED,
    build_styles,
)
from blueprint_pdf.iac_sections import split_rendered_iac_by_step_sections
from blueprint_pdf.html_flowables import markdown_to_flowables, shaded_preformatted_appendix_table
from blueprint_pdf.md_cleanup import (
    prepare_executive_summary_markdown_for_pdf,
    prepare_guidance_markdown_for_pdf,
)


def _customer_display_name(answers: Dict[str, Any], project_name: str) -> str:
    for key in ("customer_display_name", "snowflake_org_name", "account_name"):
        v = answers.get(key)
        if v is not None and str(v).strip():
            return str(v).strip()
    return project_name


def _sa_display_name(answers: Dict[str, Any]) -> Optional[str]:
    for key in ("engagement_lead_name", "sa_name", "snowflake_sa_name"):
        v = answers.get(key)
        if v is not None and str(v).strip():
            return str(v).strip()
    return None


# Paragraph styles that register in the PDF TOC (two logical levels: section vs step).
_TOC_LEVEL0_STYLES = frozenset(
    {
        "TaskHeading",
        "ExecutiveSummaryHeading",
        "GuidanceSectionHeading",
        "AppendixHeading",
    }
)
_TOC_LEVEL1_STYLES = frozenset({"StepHeading"})


class BlueprintPDFTemplate(SimpleDocTemplate):
    """Registers selected headings for the table of contents (Task > Step + major sections)."""

    def __init__(self, *args, footer_left: str, **kwargs):
        self._footer_left = footer_left
        self._toc_dest_seq = 0
        kwargs["onFirstPage"] = self._draw_footer
        kwargs["onLaterPages"] = self._draw_footer
        super().__init__(*args, **kwargs)

    def beforeDocument(self):
        """Reset per-pass counters so TOC keys match across multiBuild passes."""
        super().beforeDocument()
        self._toc_dest_seq = 0

    def _next_toc_destination(self) -> str:
        """Stable PDF-internal name for TOC / outline links (must be ASCII-safe)."""
        self._toc_dest_seq += 1
        return f"toc_{self._toc_dest_seq:05d}"

    def afterFlowable(self, flowable):
        from reportlab.platypus import Paragraph

        if isinstance(flowable, Paragraph):
            style_name = flowable.style.name
            if style_name in _TOC_LEVEL0_STYLES:
                key = self._next_toc_destination()
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page, key))
            elif style_name in _TOC_LEVEL1_STYLES:
                key = self._next_toc_destination()
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (1, flowable.getPlainText(), self.page, key))
        super().afterFlowable(flowable)

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(SNOWFLAKE_CYAN)
        canvas.setLineWidth(3)
        top_y = letter[1] - MARGIN_TOP + 4
        canvas.line(MARGIN_LEFT, top_y, MARGIN_LEFT + 0.35 * inch, top_y)
        canvas.setFillColor(TEXT_MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(MARGIN_LEFT, 0.55 * inch, self._footer_left)
        canvas.drawRightString(
            letter[0] - MARGIN_RIGHT,
            0.55 * inch,
            f"Page {canvas.getPageNumber()}",
        )
        canvas.restoreState()


def build_blueprint_pdf(
    *,
    output_path: Path,
    blueprint_meta: Dict[str, Any],
    answers: Dict[str, Any],
    rendered_guidance_md: str,
    rendered_iac: str,
    iac_label: str,
    project_display_name: str,
    date_display: str,
    executive_summary_md: Optional[str] = None,
) -> None:
    """
    Write a branded PDF to output_path.

    :param iac_label: Short label for the code appendix, e.g. "SQL" or "Terraform".
    """
    styles = build_styles()
    blueprint_name = blueprint_meta.get("name", output_path.stem)
    blueprint_id = blueprint_meta.get("blueprint_id", "")
    customer = _customer_display_name(answers, project_display_name)
    sa_name = _sa_display_name(answers)

    footer_bits = ["Snowflake Blueprint deliverable", f"Generated {date_display}"]
    if blueprint_id:
        footer_bits.append(str(blueprint_id))
    footer_left = " · ".join(footer_bits)

    toc_style_0 = ParagraphStyle(
        name="TOC0",
        parent=styles["TOCEntry"],
        fontSize=11,
        leading=14,
        leftIndent=18,
        firstLineIndent=-18,
    )
    toc_style_1 = ParagraphStyle(
        name="TOC1",
        parent=styles["TOCEntry"],
        fontSize=10,
        leading=13,
        leftIndent=36,
        firstLineIndent=-18,
    )
    toc_style_2 = ParagraphStyle(
        name="TOC2",
        parent=styles["TOCEntry"],
        fontSize=9,
        leading=12,
        leftIndent=54,
        firstLineIndent=-18,
    )

    toc = TableOfContents()
    toc.levelStyles = [toc_style_0, toc_style_1, toc_style_2]
    toc.dotsMinLevel = 0

    story: List[Any] = []

    story.append(Spacer(1, 1.4 * inch))
    story.append(Paragraph(html.escape(blueprint_name), styles["CoverTitle"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Blueprint engagement summary", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(f"<b>Customer:</b> {html.escape(customer)}", styles["CoverMeta"]))
    if sa_name:
        story.append(
            Paragraph(f"<b>Engagement lead:</b> {html.escape(sa_name)}", styles["CoverMeta"])
        )
    story.append(
        Paragraph(f"<b>Project:</b> {html.escape(project_display_name)}", styles["CoverMeta"])
    )
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(f"<b>Generated:</b> {date_display}", styles["CoverMeta"]))
    if blueprint_id:
        story.append(
            Paragraph(f"<b>Blueprint id:</b> {html.escape(blueprint_id)}", styles["CoverMeta"])
        )

    story.append(PageBreak())
    story.append(Paragraph("Table of Contents", styles["TOCSectionTitle"]))
    story.append(Spacer(1, 12))
    story.append(toc)
    story.append(PageBreak())

    if executive_summary_md and executive_summary_md.strip():
        story.append(Paragraph("Executive Summary", styles["ExecutiveSummaryHeading"]))
        exec_md = prepare_executive_summary_markdown_for_pdf(executive_summary_md)
        story.extend(markdown_to_flowables(exec_md, styles))
        story.append(Spacer(1, 12))

    story.append(Paragraph("Guidance & recommendations", styles["GuidanceSectionHeading"]))
    guidance_md = prepare_guidance_markdown_for_pdf(rendered_guidance_md)
    story.extend(markdown_to_flowables(guidance_md, styles))

    story.append(PageBreak())
    story.append(Paragraph("Appendix A: Configuration summary", styles["AppendixHeading"]))
    cell_key_style = ParagraphStyle(
        name="AnsKey",
        parent=styles["Body"],
        fontSize=8,
        leading=10,
        textColor=SNOWFLAKE_NAVY,
    )
    cell_val_style = ParagraphStyle(
        name="AnsVal",
        parent=styles["Body"],
        fontSize=8,
        leading=10,
    )
    hdr_key = ParagraphStyle(
        name="AnsHdr",
        parent=styles["Body"],
        fontSize=9,
        leading=11,
        textColor=SNOWFLAKE_NAVY,
        fontName="Helvetica-Bold",
    )
    rows = [
        [
            Paragraph("Answer key", hdr_key),
            Paragraph("Value", hdr_key),
        ]
    ]
    for key_path, val in flatten_answers(answers):
        rows.append(
            [
                Paragraph(html.escape(format_answer_cell(key_path)), cell_key_style),
                Paragraph(html.escape(format_answer_cell(val)), cell_val_style),
            ]
        )

    key_col = CONTENT_WIDTH * 0.38
    val_col = CONTENT_WIDTH * 0.62
    ans_table = Table(rows, colWidths=[key_col, val_col], repeatRows=1)
    ans_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CODE_BG),
                ("GRID", (0, 0), (-1, -1), 0.25, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(ans_table)
    story.append(PageBreak())

    story.append(Paragraph(f"Appendix B: {iac_label} reference", styles["AppendixHeading"]))
    story.append(Spacer(1, 6))
    for sec_title, sec_body in split_rendered_iac_by_step_sections(rendered_iac):
        if sec_title:
            story.append(Paragraph(html.escape(sec_title), styles["BodyHeading3"]))
            story.append(Spacer(1, 4))
        story.append(shaded_preformatted_appendix_table(sec_body, styles, lines_per_subrow=6))
        story.append(Spacer(1, 8))

    doc = BlueprintPDFTemplate(
        str(output_path),
        footer_left=footer_left,
        pagesize=letter,
        rightMargin=MARGIN_RIGHT,
        leftMargin=MARGIN_LEFT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
    )

    doc.multiBuild(story)
