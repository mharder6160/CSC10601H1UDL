#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_ZIP = REPO_ROOT / "D2LExport_662798_S_PPCC_CSC10601H1_202720_20269657.zip"
REVISED_ZIP = REPO_ROOT / "D2L_CSC1060_UDL_Revised_From_Original.zip"
STAGING_ROOT = REPO_ROOT / "native-d2l-udl-revision" / "staging"
TRANSFORMED_DIR = STAGING_ROOT / "transformed"
SUMMARY_PATH = STAGING_ROOT / "transformation-summary.json"

TARGET_XML_FILES = ("news_d2l.xml", "dropbox_d2l.xml", "syllabus_d2l.xml")

URL_TEXT_RE = re.compile(r"<a(?P<attrs>[^>]*)>(?P<text>.*?)</a>", re.IGNORECASE | re.DOTALL)
IMG_RE = re.compile(r"<img(?P<attrs>[^>]*)>", re.IGNORECASE | re.DOTALL)
TABLE_RE = re.compile(r"<table(?P<attrs>[^>]*)>", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _strip_tags(raw: str) -> str:
    return re.sub(r"<[^>]+>", "", raw)


def _host_text(href: str) -> str:
    url = href.strip()
    url = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
    return url.split("/")[0] if url else "linked resource"


def improve_links(html_fragment: str) -> tuple[str, int]:
    changed = 0

    def _replace(m: re.Match[str]) -> str:
        nonlocal changed
        attrs = m.group("attrs")
        text = m.group("text")
        href_m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        href = href_m.group(1).strip() if href_m else ""
        text_clean = _strip_tags(html.unescape(text)).strip()
        new_text = text
        if not text_clean:
            new_text = f"Open {_host_text(href)}"
        elif href and text_clean.lower() == href.lower():
            new_text = f"Open {_host_text(href)}"
        if new_text != text:
            changed += 1
            return f"<a{attrs}>{html.escape(new_text)}</a>"
        return m.group(0)

    return URL_TEXT_RE.sub(_replace, html_fragment), changed


def improve_images(html_fragment: str) -> tuple[str, int]:
    changed = 0

    def _replace(m: re.Match[str]) -> str:
        nonlocal changed
        attrs = m.group("attrs")
        if re.search(r"\balt\s*=", attrs, flags=re.IGNORECASE):
            return m.group(0)
        title_m = re.search(r'title\s*=\s*["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        src_m = re.search(r'src\s*=\s*["\']([^"\']+)["\']', attrs, flags=re.IGNORECASE)
        if title_m:
            alt_text = title_m.group(1).strip()
        elif src_m:
            src_name = Path(src_m.group(1)).name
            alt_text = "Decorative image" if src_name.startswith("image_") else f"Image: {src_name}"
        else:
            alt_text = "Decorative image"
        changed += 1
        return f"<img{attrs} alt=\"{html.escape(alt_text)}\">"

    return IMG_RE.sub(_replace, html_fragment), changed


def improve_tables(html_fragment: str) -> tuple[str, int]:
    changed = 0

    def _replace_table(m: re.Match[str]) -> str:
        nonlocal changed
        attrs = m.group("attrs")
        changed += 1
        return f"<table{attrs}><caption>[INSTRUCTOR CONFIRM] Add a short table summary.</caption>"

    if "<table" in html_fragment.lower() and "<caption" not in html_fragment.lower():
        html_fragment = TABLE_RE.sub(_replace_table, html_fragment, count=1)

    th_count = len(re.findall(r"<th\b", html_fragment, flags=re.IGNORECASE))
    if th_count == 0 and "<table" in html_fragment.lower():
        html_fragment, n = re.subn(r"<td\b", "<th scope=\"col\"", html_fragment, count=1, flags=re.IGNORECASE)
        if n:
            html_fragment, _ = re.subn(r"</td>", "</th>", html_fragment, count=1, flags=re.IGNORECASE)
            changed += 1

    return html_fragment, changed


def add_news_udl_block(headline: str) -> str:
    safe = html.escape(headline.strip() or "Announcement")
    return (
        "<hr>"
        "<h2>Purpose</h2>"
        f"<p>This announcement supports your progress in <strong>{safe}</strong>.</p>"
        "<h2>Instructions</h2>"
        "<p>Read the announcement details above and complete any linked course task.</p>"
        "<h2>Next step</h2>"
        "<p>Open the linked Brightspace item and plan your completion steps.</p>"
        "<h2>Help</h2>"
        "<p>If anything is unclear, contact your instructor through Brightspace messages. "
        "[INSTRUCTOR CONFIRM: preferred contact method and response time]</p>"
    )


def wrap_dropbox_udl(folder_name: str, points: str, allowed_exts: list[str], existing_html: str) -> str:
    safe_name = html.escape(folder_name.strip())
    points_text = html.escape(points)
    ext_text = ", ".join(sorted(allowed_exts)) if allowed_exts else "See assignment details"
    return (
        f"<h1>{safe_name}</h1>"
        "<h2>Purpose</h2>"
        f"<p>This submission folder collects your work for <strong>{safe_name}</strong>.</p>"
        "<h2>Instructions</h2>"
        f"{existing_html}"
        "<h2>What to submit</h2>"
        f"<p>Submit the files required by the assignment directions. Allowed file types: {html.escape(ext_text)}.</p>"
        "<h2>How you will be assessed</h2>"
        f"<p>This assignment is graded out of {points_text} points using the configured course rubric/criteria.</p>"
        "<h2>Multiple ways to show learning</h2>"
        "<p>Use comments in your files or a short note to explain your approach, testing, and decisions where relevant.</p>"
        "<h2>Help</h2>"
        "<p>If you need support before submitting, contact your instructor or approved course support channel. "
        "[INSTRUCTOR CONFIRM: tutoring/support options]</p>"
        "<h2>Next step</h2>"
        "<p>Review the checklist above, prepare your files, then upload and submit before the due date shown in Brightspace.</p>"
    )


def wrap_syllabus_udl(existing_html: str) -> str:
    return (
        "<h1>Course Information and Learning Guide</h1>"
        "<h2>Purpose</h2>"
        "<p>This page keeps the original course syllabus information and adds a clear navigation layer for planning your learning.</p>"
        "<h2>How to use this page</h2>"
        "<p>Read each section in order, then note key expectations, due-date patterns, and required resources.</p>"
        "<h2>Objectives and planning</h2>"
        "<p>Use the course outcomes and schedule details below to set weekly goals and track your progress.</p>"
        "<h2>Help</h2>"
        "<p>For policy or schedule clarification, contact your instructor and check course announcements. "
        "[INSTRUCTOR CONFIRM: office hours and support contact details]</p>"
        "<hr>"
        f"{existing_html}"
    )


def apply_shared_improvements(fragment: str) -> tuple[str, dict[str, int]]:
    categories = {
        "descriptive_links": 0,
        "image_alt_text": 0,
        "table_accessibility": 0,
    }
    fragment, link_changes = improve_links(fragment)
    categories["descriptive_links"] += link_changes
    fragment, img_changes = improve_images(fragment)
    categories["image_alt_text"] += img_changes
    fragment, table_changes = improve_tables(fragment)
    categories["table_accessibility"] += table_changes
    return fragment, categories


def transform_news(xml_text: str) -> tuple[str, dict[str, int]]:
    root = ET.fromstring(xml_text)
    counts = {
        "heading_structure": 0,
        "purpose_objective_sections": 0,
        "plain_language_chunking": 0,
        "navigation_next_step": 0,
        "multiple_means": 0,
        "instructor_confirm_placeholders": 0,
        "descriptive_links": 0,
        "image_alt_text": 0,
        "table_accessibility": 0,
    }
    for item in root.findall("item"):
        content = item.find("content")
        if content is None or content.attrib.get("text_type", "").lower() != "text/html":
            continue
        original = content.text or ""
        updated, shared = apply_shared_improvements(original)
        updated = f"<h1>{html.escape((item.findtext('headline') or 'Announcement').strip())}</h1>" + updated
        updated += add_news_udl_block(item.findtext("headline") or "Announcement")
        content.text = updated
        counts["heading_structure"] += 1
        counts["purpose_objective_sections"] += 1
        counts["plain_language_chunking"] += 1
        counts["navigation_next_step"] += 1
        counts["multiple_means"] += 1
        counts["instructor_confirm_placeholders"] += 1
        for k, v in shared.items():
            counts[k] += v
    return ET.tostring(root, encoding="utf-8").decode("utf-8"), counts


def transform_dropbox(xml_text: str) -> tuple[str, dict[str, int]]:
    root = ET.fromstring(xml_text)
    counts = {
        "heading_structure": 0,
        "purpose_objective_sections": 0,
        "plain_language_chunking": 0,
        "navigation_next_step": 0,
        "multiple_means": 0,
        "instructor_confirm_placeholders": 0,
        "descriptive_links": 0,
        "image_alt_text": 0,
        "table_accessibility": 0,
    }
    for folder in root.findall("folder"):
        instructions = folder.find("instructions")
        if instructions is None or instructions.attrib.get("text_type", "").lower() != "text/html":
            continue
        text_node = instructions.find("text")
        if text_node is None:
            continue
        original = text_node.text or ""
        updated, shared = apply_shared_improvements(original)
        allowed_exts = [ext.attrib.get("value", "") for ext in folder.findall("allowable_file_type_custom_list/extension")]
        points = folder.attrib.get("out_of", "")
        if "." in points:
            points = points.rstrip("0").rstrip(".")
        text_node.text = wrap_dropbox_udl(folder.attrib.get("name", "Assignment"), points or "[INSTRUCTOR CONFIRM]", allowed_exts, updated)
        counts["heading_structure"] += 1
        counts["purpose_objective_sections"] += 1
        counts["plain_language_chunking"] += 1
        counts["navigation_next_step"] += 1
        counts["multiple_means"] += 1
        counts["instructor_confirm_placeholders"] += 1
        for k, v in shared.items():
            counts[k] += v
    return ET.tostring(root, encoding="utf-8").decode("utf-8"), counts


def transform_syllabus(xml_text: str) -> tuple[str, dict[str, int]]:
    root = ET.fromstring(xml_text)
    counts = {
        "heading_structure": 0,
        "purpose_objective_sections": 0,
        "plain_language_chunking": 0,
        "navigation_next_step": 0,
        "multiple_means": 0,
        "instructor_confirm_placeholders": 0,
        "descriptive_links": 0,
        "image_alt_text": 0,
        "table_accessibility": 0,
    }
    desc = root.attrib.get("description", "")
    updated, shared = apply_shared_improvements(desc)
    root.attrib["description"] = wrap_syllabus_udl(updated)
    counts["heading_structure"] += 1
    counts["purpose_objective_sections"] += 1
    counts["plain_language_chunking"] += 1
    counts["navigation_next_step"] += 1
    counts["multiple_means"] += 1
    counts["instructor_confirm_placeholders"] += 1
    for k, v in shared.items():
        counts[k] += v
    return ET.tostring(root, encoding="utf-8").decode("utf-8"), counts


def main() -> None:
    if not ORIGINAL_ZIP.exists():
        raise SystemExit(f"Missing original export: {ORIGINAL_ZIP}")

    TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)

    original_hash_before = sha256_file(ORIGINAL_ZIP)

    transformers = {
        "news_d2l.xml": transform_news,
        "dropbox_d2l.xml": transform_dropbox,
        "syllabus_d2l.xml": transform_syllabus,
    }

    transformed_xml: dict[str, bytes] = {}
    per_file_summary = []

    with ZipFile(ORIGINAL_ZIP, "r") as zin:
        for xml_name, fn in transformers.items():
            source_text = zin.read(xml_name).decode("utf-8-sig")
            transformed_text, counts = fn(source_text)
            transformed_bytes = transformed_text.encode("utf-8")
            transformed_xml[xml_name] = transformed_bytes
            out_path = TRANSFORMED_DIR / xml_name
            out_path.write_bytes(transformed_bytes)
            per_file_summary.append({
                "file": xml_name,
                "change_categories": counts,
            })

        with ZipFile(REVISED_ZIP, "w", compression=ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = transformed_xml.get(info.filename)
                if data is None:
                    data = zin.read(info.filename)
                preserved = info
                preserved.compress_type = ZIP_DEFLATED
                zout.writestr(preserved, data)

    original_hash_after = sha256_file(ORIGINAL_ZIP)
    revised_hash = sha256_file(REVISED_ZIP)

    summary = {
        "source_original_zip": ORIGINAL_ZIP.name,
        "revised_zip": REVISED_ZIP.name,
        "original_zip_sha256_before": original_hash_before,
        "original_zip_sha256_after": original_hash_after,
        "revised_zip_sha256": revised_hash,
        "original_unchanged": original_hash_before == original_hash_after,
        "changed_files": per_file_summary,
        "limitations": [
            "Automated UDL changes were applied only to learner-facing HTML embedded in news, dropbox instructions, and syllabus description.",
            "Institution-specific Brightspace behavior can vary and must be verified with a test import shell.",
        ],
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
