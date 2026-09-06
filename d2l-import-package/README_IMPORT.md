# Brightspace / D2L Import Notes

This folder contains a **conservative IMS Content Packaging test/import package** for CSC1060 UDL starter-shell content.

`README_IMPORT.md` is part of the repository source folder for packaging guidance. The generated import ZIP contains the manifest plus the HTML content pages used for import.

## Recommended import workflow

1. Download the root repository file `D2L_UDL_StarterShell_CSC1060.zip`.
2. In Brightspace, open a **blank test shell** whenever possible.
3. Go to **Course Admin -> Import/Export/Copy Components**.
4. Choose **Import Components** and upload `D2L_UDL_StarterShell_CSC1060.zip`.
5. Review imported content before copying or rebuilding anything in a live course.
6. The original D2L export ZIP and syllabus PDF stay preserved separately at the repository root; they are not bundled into this test/import archive.

### Packaging requirement for rebuilds

- The ZIP must be created from **inside** `d2l-import-package/`.
- `imsmanifest.xml` and the HTML content files must appear at the **archive root**.
- Do **not** upload or zip a parent folder so that files end up nested under `d2l-import-package/`.

### Rebuild and validation steps

1. From the repository root, rebuild the archive from the source directory itself:
   - Run a manifest-driven rebuild so the ZIP always includes `imsmanifest.xml` and every manifest-referenced file:
     ```bash
     rm -f D2L_UDL_StarterShell_CSC1060.zip
     python - <<'PY'
     from pathlib import Path
     from zipfile import ZIP_DEFLATED, ZipFile
     import xml.etree.ElementTree as ET
     
     repo = Path('.')
     pkg = repo / 'd2l-import-package'
     ns = {'imscp': 'http://www.imsglobal.org/xsd/imscp_v1p1'}
     root = ET.parse(pkg / 'imsmanifest.xml').getroot()
     
     files = ['imsmanifest.xml']
     for resource in root.findall('.//imscp:resource', ns):
         href = resource.attrib.get('href')
         if href:
             files.append(href)
         for file_node in resource.findall('imscp:file', ns):
             files.append(file_node.attrib['href'])
     
     files = list(dict.fromkeys(files))
     with ZipFile(repo / 'D2L_UDL_StarterShell_CSC1060.zip', 'w', compression=ZIP_DEFLATED) as archive:
         for relative_path in files:
             archive.write(pkg / relative_path, arcname=relative_path)
     PY
     ```
   - `README_IMPORT.md` is intentionally excluded from the import ZIP and remains source-only guidance in `d2l-import-package/`.
2. Confirm the ZIP is non-empty.
3. Confirm `imsmanifest.xml` is visible at the ZIP root.
4. Confirm every manifest `href` and `file` path exists in `d2l-import-package/` and in the rebuilt ZIP.
5. If any HTML page references new images, CSS, PDFs, or other linked files, add those files to the ZIP and add matching `<file>` entries under the correct manifest resource before release.
6. Confirm `imsmanifest.xml` parses as XML.
7. Confirm all HTML files have balanced tags and matched `h1`, `h2`, and `h3` elements.
8. Confirm no confidential data is present before publishing or sharing the archive.

## Expected imported contents

- Start Here page
- UDL course blueprint
- Accessibility checklist
- Weekly module template
- Sample Module 1 for early Java content
- Assessment and feedback guidance
- Suggested course map

### Expected archive-root contents

The generated `D2L_UDL_StarterShell_CSC1060.zip` should contain:

- `imsmanifest.xml`
- the self-contained HTML content pages referenced by `imsmanifest.xml`

## Instructor confirmation placeholders

Before publishing to students, review all `[INSTRUCTOR CONFIRM]` placeholders for:

- instructor contact details
- office hours / support channels
- local policy decisions
- exact due dates, tools, and linked files
- course-specific AI/integrity rules

## Limitations

- This package is intended as a **conservative IMS Content Packaging test/import package**.
- It is **not guaranteed** to reproduce native Brightspace gradebook, quiz, rubric, release-condition, or course-setting objects.
- It does not claim validation in any specific institutional Brightspace instance.
- It focuses on portable HTML content pages rather than vendor-specific course-tool configuration.

## Troubleshooting package-format errors

If Brightspace reports a package-format or conversion error:

1. Confirm you uploaded `D2L_UDL_StarterShell_CSC1060.zip`, not the `d2l-import-package/` folder itself.
2. Confirm the ZIP opens with `imsmanifest.xml` visible at the ZIP root.
3. Re-download the ZIP if the file size looks suspiciously small or the transfer was interrupted.
4. Try importing into a blank test shell to isolate shell-specific issues.
5. If your institution only accepts vendor-specific export packages for some tools, manually copy the HTML content pages after import or use them as source content.
