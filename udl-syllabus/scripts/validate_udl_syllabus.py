#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_PDF = ROOT / "Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java.pdf"
REVISED_PDF = ROOT / "Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java-UDL.pdf"
SOURCE_MD = ROOT / "udl-syllabus" / "Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java-UDL.md"
SUMMARY_JSON = ROOT / "udl-syllabus" / "validation-summary.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_original_unchanged() -> tuple[bool, str]:
    cmd = ["git", "diff", "--name-only", "--", str(ORIGINAL_PDF.name)]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    changed = bool(result.stdout.strip())
    return (not changed, "No working-tree diff for original PDF" if not changed else "Original PDF has working-tree changes")


def extract_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


required_section_tokens = [
    "Instructor Information",
    "Course Information",
    "Course Outcomes",
    "Course Materials",
    "Grade Distribution",
    "Grading Scale",
    "Course Schedule",
    "Instructor Policies",
    "Institutional Policies",
]


if __name__ == "__main__":
    checks: dict[str, dict[str, object]] = {}

    ok, message = check_original_unchanged()
    checks["original_pdf_unchanged"] = {"ok": ok, "detail": message, "path": str(ORIGINAL_PDF)}

    revised_exists = REVISED_PDF.exists() and REVISED_PDF.stat().st_size > 0
    checks["revised_pdf_non_empty"] = {
        "ok": revised_exists,
        "detail": "Revised PDF exists and has non-zero size" if revised_exists else "Revised PDF missing or empty",
        "path": str(REVISED_PDF),
        "bytes": REVISED_PDF.stat().st_size if REVISED_PDF.exists() else 0,
    }

    revised_text = ""
    if revised_exists:
        try:
            revised_text = extract_pdf_text(REVISED_PDF)
            checks["revised_pdf_extractable_text"] = {
                "ok": len(revised_text.strip()) > 0,
                "detail": "Extracted text from revised PDF" if revised_text.strip() else "No text extracted from revised PDF",
                "characters": len(revised_text),
            }
        except Exception as exc:  # pragma: no cover
            checks["revised_pdf_extractable_text"] = {"ok": False, "detail": f"Text extraction failed: {exc}"}
    else:
        checks["revised_pdf_extractable_text"] = {"ok": False, "detail": "Skipped (revised PDF missing)"}

    md_text = SOURCE_MD.read_text(encoding="utf-8") if SOURCE_MD.exists() else ""
    missing_sections = [s for s in required_section_tokens if s not in md_text]
    checks["major_sections_present"] = {
        "ok": len(missing_sections) == 0,
        "detail": "All required major section tokens found" if not missing_sections else "Missing required section tokens",
        "missing": missing_sections,
    }

    expected_link_text = [
        "PPSC ACCESSibility Services webpage",
        "Accessibility Contact Request Form",
        "Assessment landing page",
        "PPSC Counseling Center website",
        "BetterMynd website",
        "Tutoring Center website",
        "Learning Commons",
        "Brown University LibGuide",
    ]
    missing_links = [t for t in expected_link_text if t not in md_text]
    checks["links_preserved_or_flagged"] = {
        "ok": len(missing_links) == 0,
        "detail": "Named links/resource text preserved" if not missing_links else "Some named link/resource text missing",
        "missing": missing_links,
    }

    checks["instructor_confirm_placeholders"] = {
        "ok": "[INSTRUCTOR CONFIRM]" in md_text,
        "detail": "At least one instructor confirmation placeholder is present" if "[INSTRUCTOR CONFIRM]" in md_text else "No [INSTRUCTOR CONFIRM] placeholders found",
    }

    checks["hashes"] = {
        "ok": True,
        "detail": "SHA-256 captured for source and revised PDFs",
        "original_sha256": sha256(ORIGINAL_PDF) if ORIGINAL_PDF.exists() else None,
        "revised_sha256": sha256(REVISED_PDF) if REVISED_PDF.exists() else None,
    }

    overall_ok = all(item.get("ok") is True for item in checks.values())

    summary = {
        "overall_ok": overall_ok,
        "checks": checks,
        "artifacts": {
            "original_pdf": str(ORIGINAL_PDF),
            "revised_pdf": str(REVISED_PDF),
            "editable_source": str(SOURCE_MD),
        },
        "limitations": [
            "Source appendix is machine-extracted and may contain layout artifacts.",
            "Named resources in source text may require instructor-confirmed official URLs.",
        ],
    }

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not overall_ok:
        raise SystemExit(1)
