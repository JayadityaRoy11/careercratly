"""Generate PROJECT_REPORT.pdf from PROJECT_REPORT.md using reportlab."""
from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "PROJECT_REPORT.md"
PDF_PATH = ROOT / "docs" / "PROJECT_REPORT.pdf"

PAGE_W, PAGE_H = A4
MARGIN = 16 * mm


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=6,
            textColor=colors.HexColor("#0f172a"),
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            spaceAfter=14,
            textColor=colors.HexColor("#334155"),
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=14,
            spaceAfter=8,
            textColor=colors.HexColor("#0f172a"),
            borderPadding=3,
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=6,
            textColor=colors.HexColor("#1e293b"),
        ),
        "h3": ParagraphStyle(
            "H3Custom",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            spaceBefore=8,
            spaceAfter=4,
            textColor=colors.HexColor("#334155"),
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            textColor=colors.HexColor("#1e293b"),
        ),
        "meta": ParagraphStyle(
            "MetaCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=3,
            textColor=colors.HexColor("#475569"),
        ),
        "code": ParagraphStyle(
            "CodeCustom",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=10,
            leftIndent=4,
            rightIndent=4,
            backColor=colors.HexColor("#f1f5f9"),
            spaceBefore=4,
            spaceAfter=8,
            textColor=colors.HexColor("#0f172a"),
        ),
        "diagram": ParagraphStyle(
            "DiagramCustom",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7,
            leading=9.5,
            leftIndent=6,
            rightIndent=6,
            backColor=colors.HexColor("#eff6ff"),
            borderPadding=6,
            spaceBefore=4,
            spaceAfter=8,
            textColor=colors.HexColor("#1e3a8a"),
        ),
        "bullet": ParagraphStyle(
            "BulletCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=12.5,
            leftIndent=12,
            spaceAfter=2,
            textColor=colors.HexColor("#1e293b"),
        ),
        "table_cell": ParagraphStyle(
            "TableCell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.white,
        ),
        "footer": ParagraphStyle(
            "FooterCustom",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748b"),
        ),
    }


def esc(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='8'>\1</font>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = text.replace("—", "-").replace("–", "-").replace("→", "->").replace("←", "<-")
    text = text.replace("✓", "[x]").replace("●", "*")
    return text


def mermaid_to_ascii(code: str) -> str:
    """Turn mermaid source into a readable ASCII architecture block for PDF."""
    lines = []
    for raw in code.splitlines():
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue
        # Drop mermaid keywords noise lightly
        line = re.sub(r"^(flowchart|sequenceDiagram|actor|participant|subgraph|end)\b.*", "", line)
        if not line.strip():
            continue
        line = line.replace("-->", " -> ").replace("->>", " -> ").replace("-->>", " -> ")
        line = re.sub(r"\|([^|]+)\|", r" [\1] ", line)
        line = re.sub(r"\[([^\]]+)\]", r"[\1]", line)
        line = re.sub(r"\{([^}]+)\}", r"{\1}", line)
        line = re.sub(r"<br\s*/?>", " / ", line, flags=re.I)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    if not lines:
        return code.strip()
    header = "ARCHITECTURE / DATA FLOW (from diagram)"
    body = "\n".join(f"  {ln}" for ln in lines[:40])
    return f"{header}\n{'-' * 52}\n{body}"


def parse_table(rows: list[str], st) -> Table:
    data = []
    for i, row in enumerate(rows):
        cells = [c.strip() for c in row.strip("|").split("|")]
        style = st["table_header"] if i == 0 else st["table_cell"]
        data.append([Paragraph(esc(c), style) for c in cells])
    # skip separator row like |---|---|
    cleaned = []
    for i, row in enumerate(data):
        raw = rows[i]
        if re.match(r"^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$", raw.strip()):
            continue
        cleaned.append(row)
    if not cleaned:
        return Spacer(1, 1)
    col_count = max(len(r) for r in cleaned)
    for r in cleaned:
        while len(r) < col_count:
            r.append(Paragraph("", st["table_cell"]))
    usable = PAGE_W - 2 * MARGIN
    col_w = usable / col_count
    table = Table(cleaned, colWidths=[col_w] * col_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fafc")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ]
        )
    )
    return table


def build_story(md: str, st):
    story = []
    lines = md.splitlines()
    i = 0
    title_done = False
    table_buf: list[str] = []

    def flush_table():
        nonlocal table_buf
        if table_buf:
            story.append(parse_table(table_buf, st))
            story.append(Spacer(1, 6))
            table_buf = []

    while i < len(lines):
        line = lines[i]

        # Mermaid / fenced code
        if line.strip().startswith("```"):
            flush_table()
            lang = line.strip()[3:].strip().lower()
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1  # closing ```
            code = "\n".join(block)
            if lang == "mermaid":
                ascii_d = mermaid_to_ascii(code)
                story.append(Preformatted(ascii_d, st["diagram"], maxLineLength=95))
            else:
                # Truncate very long code for PDF readability
                clipped = "\n".join(code.splitlines()[:45])
                if len(code.splitlines()) > 45:
                    clipped += "\n... (truncated in PDF; see PROJECT_REPORT.md)"
                story.append(Preformatted(clipped, st["code"], maxLineLength=95))
            continue

        # Tables
        if line.strip().startswith("|"):
            table_buf.append(line)
            i += 1
            continue
        else:
            flush_table()

        if not line.strip():
            i += 1
            continue

        if line.strip() == "---":
            story.append(Spacer(1, 4))
            i += 1
            continue

        if line.startswith("# ") and not title_done:
            story.append(Paragraph(esc(line[2:].strip()), st["title"]))
            title_done = True
            i += 1
            continue

        if line.startswith("## ") and not title_done:
            story.append(Paragraph(esc(line[3:].strip()), st["subtitle"]))
            i += 1
            continue

        if line.startswith("### "):
            story.append(Paragraph(esc(line[4:].strip()), st["h3"]))
            i += 1
            continue

        if line.startswith("## "):
            story.append(Paragraph(esc(line[3:].strip()), st["h1"]))
            i += 1
            continue

        if line.startswith("# "):
            story.append(Paragraph(esc(line[2:].strip()), st["h1"]))
            i += 1
            continue

        # Math-ish lines
        if line.strip().startswith("\\[") or "text{Score}" in line:
            story.append(Preformatted(line.strip("\\[] ").strip(), st["code"]))
            i += 1
            continue

        # List items
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            story.append(Paragraph("• " + esc(m.group(3)), st["bullet"]))
            i += 1
            continue

        # Meta bold lines near top
        if line.strip().startswith("**") and ":" in line:
            story.append(Paragraph(esc(line.strip()), st["meta"]))
            i += 1
            continue

        # Tree / indented structure
        if line.startswith("    ") or line.startswith("├") or line.startswith("└") or line.startswith("│"):
            story.append(Preformatted(line, st["code"], maxLineLength=100))
            i += 1
            continue

        story.append(Paragraph(esc(line.strip()), st["body"]))
        i += 1

    flush_table()
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748b"))
    text = f"Resume Analyzer + Job Portal — Project Report  |  Page {doc.page}"
    canvas.drawCentredString(PAGE_W / 2, 10 * mm, text)
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
    canvas.restoreState()


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    st = styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Resume Analyzer + Job Portal — Project Report",
        author="Academic Prototype",
    )
    story = build_story(md, st)
    # Cover spacer
    story.insert(0, Spacer(1, 8 * mm))
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
