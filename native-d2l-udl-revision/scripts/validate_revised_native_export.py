#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

REPO_ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_ZIP = REPO_ROOT / "D2LExport_662798_S_PPCC_CSC10601H1_202720_20269657.zip"
REVISED_ZIP = REPO_ROOT / "D2L_CSC1060_UDL_Revised_From_Original.zip"
SUMMARY_PATH = REPO_ROOT / "native-d2l-udl-revision" / "staging" / "transformation-summary.json"
REPORT_PATH = REPO_ROOT / "native-d2l-udl-revision" / "staging" / "validation-report.json"

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "/")
SECRET_PATTERNS = [
    r"AKIA[0-9A-Z]{16}",
    r"ghp_[A-Za-z0-9]{36}",
    r"AIza[0-9A-Za-z\-_]{35}",
    r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----",
]


class BalancedHTMLParser(HTMLParser):
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() not in self.VOID_TAGS:
            self.stack.append(tag.lower())

    def handle_endtag(self, tag: str):
        t = tag.lower()
        if not self.stack:
            self.errors.append(f"unexpected closing tag </{t}>")
            return
        if self.stack[-1] == t:
            self.stack.pop()
            return
        if t in self.stack:
            while self.stack and self.stack[-1] != t:
                self.errors.append(f"implicit close for <{self.stack.pop()}>")
            if self.stack and self.stack[-1] == t:
                self.stack.pop()
        else:
            self.errors.append(f"unexpected closing tag </{t}>")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_manifest_refs(manifest_bytes: bytes) -> tuple[set[str], set[str]]:
    root = ET.fromstring(manifest_bytes)
    ns = {"imscp": "http://www.imsglobal.org/xsd/imscp_v1p1"}
    refs: set[str] = set()
    for resource in root.findall(".//imscp:resource", ns):
        href = resource.attrib.get("href")
        if href:
            refs.add(href.replace("\\", "/"))
        for file_node in resource.findall("imscp:file", ns):
            href2 = file_node.attrib.get("href")
            if href2:
                refs.add(href2.replace("\\", "/"))

    local: set[str] = set()
    external: set[str] = set()
    for ref in refs:
        if ref.startswith(EXTERNAL_PREFIXES) or "{orgUnitId}" in ref or "?" in ref:
            external.add(ref)
        else:
            local.add(ref)
    return local, external


def extract_html_fragments(zipf: ZipFile) -> list[tuple[str, str]]:
    fragments: list[tuple[str, str]] = []
    targets = ["news_d2l.xml", "dropbox_d2l.xml", "syllabus_d2l.xml"]
    for name in targets:
        raw = zipf.read(name).decode("utf-8-sig")
        root = ET.fromstring(raw)
        if name == "news_d2l.xml":
            for item in root.findall("item"):
                c = item.find("content")
                if c is not None and c.attrib.get("text_type", "").lower() == "text/html":
                    fragments.append((f"{name}:item:{item.attrib.get('id','?')}", c.text or ""))
        elif name == "dropbox_d2l.xml":
            for folder in root.findall("folder"):
                ins = folder.find("instructions")
                if ins is None or ins.attrib.get("text_type", "").lower() != "text/html":
                    continue
                text = ins.find("text")
                if text is not None:
                    fragments.append((f"{name}:folder:{folder.attrib.get('id','?')}", text.text or ""))
        elif name == "syllabus_d2l.xml":
            fragments.append((f"{name}:description", root.attrib.get("description", "")))

    for zip_name in zipf.namelist():
        if zip_name.lower().endswith((".html", ".htm")):
            fragments.append((zip_name, zipf.read(zip_name).decode("utf-8", errors="replace")))
    return fragments


def scan_secrets(zipf: ZipFile) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for name in zipf.namelist():
        if not name.lower().endswith((".xml", ".html", ".htm", ".txt", ".md", ".json", ".java", ".doc", ".docx", ".rtf", ".pdf")):
            continue
        data = zipf.read(name)
        if b"\x00" in data:
            continue
        text = data.decode("utf-8", errors="ignore")
        for pat in SECRET_PATTERNS:
            m = re.search(pat, text)
            if m:
                findings.append({"file": name, "pattern": pat, "match": m.group(0)[:80]})
    return findings


def main() -> None:
    if not ORIGINAL_ZIP.exists() or not REVISED_ZIP.exists():
        raise SystemExit("Both original and revised zip files must exist before validation.")

    checks: dict[str, object] = {}

    checks["original_zip_sha256"] = sha256_file(ORIGINAL_ZIP)
    checks["revised_zip_sha256"] = sha256_file(REVISED_ZIP)

    with ZipFile(ORIGINAL_ZIP, "r") as zorig, ZipFile(REVISED_ZIP, "r") as zrev:
        checks["revised_zip_opens"] = zrev.testzip() is None

        original_names = zorig.namelist()
        revised_names = zrev.namelist()
        checks["file_list_matches_original"] = original_names == revised_names

        required_metadata = ["imsmanifest.xml", "orgunitconfig/orgunitconfig.xml", "news_d2l.xml", "dropbox_d2l.xml", "grades_d2l.xml"]
        checks["required_metadata_present"] = all(name in revised_names for name in required_metadata)

        original_local_refs, _ = collect_manifest_refs(zorig.read("imsmanifest.xml"))
        revised_local_refs, _ = collect_manifest_refs(zrev.read("imsmanifest.xml"))
        original_missing_local = sorted(ref for ref in original_local_refs if ref not in original_names)
        revised_missing_local = sorted(ref for ref in revised_local_refs if ref not in revised_names)
        checks["manifest_local_reference_count_original"] = len(original_local_refs)
        checks["manifest_local_reference_count_revised"] = len(revised_local_refs)
        checks["manifest_local_missing_count_original"] = len(original_missing_local)
        checks["manifest_local_missing_count_revised"] = len(revised_missing_local)
        checks["manifest_local_missing_not_worse"] = len(revised_missing_local) <= len(original_missing_local)
        checks["manifest_local_new_missing_refs"] = sorted(set(revised_missing_local) - set(original_missing_local))

        xml_errors = []
        for name in revised_names:
            if not name.lower().endswith(".xml"):
                continue
            try:
                ET.fromstring(zrev.read(name).decode("utf-8-sig"))
            except Exception as exc:
                xml_errors.append({"file": name, "error": str(exc)})
        checks["xml_well_formed"] = len(xml_errors) == 0
        checks["xml_errors"] = xml_errors

        html_errors = []
        for label, fragment in extract_html_fragments(zrev):
            parser = BalancedHTMLParser()
            try:
                parser.feed(fragment)
                parser.close()
            except Exception as exc:
                html_errors.append({"fragment": label, "error": str(exc)})
                continue
            if parser.stack:
                html_errors.append({"fragment": label, "error": f"unclosed tags: {parser.stack[:8]}"})
            if parser.errors:
                html_errors.append({"fragment": label, "error": "; ".join(parser.errors[:3])})
        checks["html_fragments_parseable"] = len(html_errors) == 0
        checks["html_errors"] = html_errors

        secret_findings = scan_secrets(zrev)
        checks["secret_scan_passed"] = len(secret_findings) == 0
        checks["secret_findings"] = secret_findings

    checks["transformation_summary_present"] = SUMMARY_PATH.exists()
    if SUMMARY_PATH.exists():
        try:
            summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
            checks["transformation_summary_has_changed_files"] = bool(summary.get("changed_files"))
        except Exception as exc:
            checks["transformation_summary_has_changed_files"] = False
            checks["transformation_summary_error"] = str(exc)

    checks["overall_pass"] = all([
        checks["revised_zip_opens"],
        checks["file_list_matches_original"],
        checks["required_metadata_present"],
        checks["manifest_local_missing_not_worse"],
        checks["xml_well_formed"],
        checks["html_fragments_parseable"],
        checks["secret_scan_passed"],
        checks.get("transformation_summary_present", False),
    ])

    REPORT_PATH.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
