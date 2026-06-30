# Copyright (c) 2026 Snowflake Inc. All rights reserved.
# Licensed under the Snowflake Skills License.

"""Snowflake-inspired palette and paragraph styles for PDF output."""

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch

# Balto-adjacent blues (internal design skill alignment)
SNOWFLAKE_CYAN = colors.HexColor("#29B5E8")
SNOWFLAKE_NAVY = colors.HexColor("#11567F")
TEXT_PRIMARY = colors.HexColor("#111827")
TEXT_MUTED = colors.HexColor("#6B7280")
BORDER_LIGHT = colors.HexColor("#E5E7EB")
CODE_BG = colors.HexColor("#F3F4F6")
# Step titles — distinct from in-step markdown ## headers
STEP_ACCENT = colors.HexColor("#0EA5E9")
BODY_HEADING = colors.HexColor("#374151")


def build_styles():
    """Return a dict of ParagraphStyle instances used across the PDF."""
    base = getSampleStyleSheet()
    styles = {
        "CoverTitle": ParagraphStyle(
            name="CoverTitle",
            parent=base["Heading1"],
            fontSize=22,
            leading=28,
            textColor=SNOWFLAKE_NAVY,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "CoverSubtitle": ParagraphStyle(
            name="CoverSubtitle",
            parent=base["Normal"],
            fontSize=12,
            leading=16,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "CoverMeta": ParagraphStyle(
            name="CoverMeta",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "Heading1": ParagraphStyle(
            name="Heading1",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=18,
            spaceAfter=10,
        ),
        "Heading2": ParagraphStyle(
            name="Heading2",
            parent=base["Heading2"],
            fontSize=13,
            leading=17,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "Heading3": ParagraphStyle(
            name="Heading3",
            parent=base["Heading3"],
            fontSize=11,
            leading=15,
            textColor=TEXT_PRIMARY,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "Body": ParagraphStyle(
            name="Body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=TEXT_PRIMARY,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        # Tighter vertical rhythm for markdown list items (avoid ListFlowable bullet/line split).
        "BodyListItem": ParagraphStyle(
            name="BodyListItem",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=TEXT_PRIMARY,
            alignment=TA_JUSTIFY,
            spaceAfter=4,
        ),
        "BodyMono": ParagraphStyle(
            name="BodyMono",
            parent=base["Code"],
            fontSize=8.5,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=8,
            fontName="Courier",
            # ``Code`` inherits a large leftIndent; ``Preformatted`` draws from leftIndent, so a
            # non-zero value shrinks the usable line width without ``stringWidth`` wrap logic
            # knowing about it — last characters can sit past the shaded cell edge.
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=0,
        ),
        "BlockQuote": ParagraphStyle(
            name="BlockQuote",
            parent=base["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=TEXT_MUTED,
            leftIndent=12,
            spaceAfter=8,
        ),
        "Footer": ParagraphStyle(
            name="Footer",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            textColor=TEXT_MUTED,
            alignment=TA_CENTER,
        ),
        "TOCEntry": ParagraphStyle(
            name="TOCEntry",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=TEXT_PRIMARY,
        ),
        # Like Heading1 but must not trigger TOC registration in afterFlowable.
        "TOCSectionTitle": ParagraphStyle(
            name="TOCSectionTitle",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=0,
            spaceAfter=10,
        ),
        # TOC-registered: blueprint Task sections (level 0)
        "TaskHeading": ParagraphStyle(
            name="TaskHeading",
            parent=base["Heading1"],
            fontSize=15,
            leading=19,
            textColor=SNOWFLAKE_NAVY,
            fontName="Helvetica-Bold",
            spaceBefore=20,
            spaceAfter=6,
        ),
        # TOC-registered: Step N.M (level 1)
        "StepHeading": ParagraphStyle(
            name="StepHeading",
            parent=base["Heading2"],
            fontSize=12.5,
            leading=16,
            textColor=STEP_ACCENT,
            fontName="Helvetica-Bold",
            spaceBefore=6,
            spaceAfter=8,
        ),
        # In-guidance ## / ### — not in TOC
        "BodyHeading2": ParagraphStyle(
            name="BodyHeading2",
            parent=base["Heading2"],
            fontSize=11,
            leading=15,
            textColor=BODY_HEADING,
            fontName="Helvetica-Bold",
            spaceBefore=12,
            spaceAfter=6,
        ),
        "BodyHeading3": ParagraphStyle(
            name="BodyHeading3",
            parent=base["Heading3"],
            fontSize=10,
            leading=14,
            textColor=TEXT_MUTED,
            fontName="Helvetica-Bold",
            spaceBefore=8,
            spaceAfter=4,
        ),
        # TOC level 0 — major PDF sections
        "ExecutiveSummaryHeading": ParagraphStyle(
            name="ExecutiveSummaryHeading",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=0,
            spaceAfter=10,
        ),
        "GuidanceSectionHeading": ParagraphStyle(
            name="GuidanceSectionHeading",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=12,
            spaceAfter=10,
        ),
        "AppendixHeading": ParagraphStyle(
            name="AppendixHeading",
            parent=base["Heading1"],
            fontSize=16,
            leading=20,
            textColor=SNOWFLAKE_NAVY,
            spaceBefore=12,
            spaceAfter=10,
        ),
        "TableCell": ParagraphStyle(
            name="TableCell",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=TEXT_PRIMARY,
            alignment=TA_LEFT,
        ),
        "TableHeaderCell": ParagraphStyle(
            name="TableHeaderCell",
            parent=base["Normal"],
            fontSize=8,
            leading=11,
            textColor=SNOWFLAKE_NAVY,
            fontName="Helvetica-Bold",
            alignment=TA_LEFT,
        ),
    }
    return styles


PAGE_WIDTH = 8.5 * inch
PAGE_HEIGHT = 11 * inch
MARGIN_LEFT = 0.75 * inch
MARGIN_RIGHT = 0.75 * inch
MARGIN_TOP = 0.75 * inch
MARGIN_BOTTOM = 0.85 * inch

# Usable content width for tables and full-width flowables (Letter, side margins).
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
