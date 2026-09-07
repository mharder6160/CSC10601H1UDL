#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path
from fpdf import FPDF
from fpdf.errors import FPDFException

ROOT = Path(__file__).resolve().parents[2]
SOURCE_MD = ROOT / "udl-syllabus" / "Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java-UDL.md"
OUT_PDF = ROOT / "Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java-UDL.pdf"


def sanitize(text: str) -> str:
    cleaned = (
        text.replace("•", "- ")
        .replace("–", "-")
        .replace("—", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    return cleaned.encode("latin-1", "replace").decode("latin-1")


def write_line(pdf: FPDF, text: str, line_height: float = 5.5) -> None:
    text = sanitize(text)
    try:
        pdf.multi_cell(0, line_height, text, new_x="LMARGIN", new_y="NEXT")
    except FPDFException:
        tokens = []
        for token in text.split(" "):
            if len(token) > 60:
                tokens.extend(token[i : i + 60] for i in range(0, len(token), 60))
            else:
                tokens.append(token)
        pdf.multi_cell(0, line_height, " ".join(tokens), new_x="LMARGIN", new_y="NEXT")


def render_markdown_to_pdf(source_markdown: Path, output_pdf: Path) -> None:
    lines = source_markdown.read_text(encoding="utf-8").splitlines()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    in_code = False

    for raw in lines:
        line = raw.rstrip("\n")

        if line.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            pdf.set_font("Courier", size=9)
            write_line(pdf, line if line else " ", line_height=4.5)
            continue

        if not line.strip():
            write_line(pdf, " ", line_height=3)
            continue

        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            write_line(pdf, line[2:].strip(), line_height=8)
            continue
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            write_line(pdf, line[3:].strip(), line_height=7)
            continue
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            write_line(pdf, line[4:].strip(), line_height=6)
            continue

        if line.startswith("> "):
            pdf.set_font("Helvetica", "", 10)
            write_line(pdf, f"Note: {line[2:].strip()}")
            continue

        if re.match(r"^\d+\.\s+", line):
            pdf.set_font("Helvetica", "", 10)
            write_line(pdf, line)
            continue

        if line.startswith("- "):
            pdf.set_font("Helvetica", "", 10)
            write_line(pdf, f"- {line[2:].strip()}")
            continue

        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(set(c) <= {"-", ":"} for c in cells):
                continue
            pdf.set_font("Helvetica", "", 10)
            write_line(pdf, " | ".join(cells))
            continue

        pdf.set_font("Helvetica", "", 10)
        write_line(pdf, line)

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_pdf))


if __name__ == "__main__":
    render_markdown_to_pdf(SOURCE_MD, OUT_PDF)
    print(f"Wrote {OUT_PDF}")
