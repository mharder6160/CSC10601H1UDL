# Brightspace / D2L Import Notes

This folder contains a **conservative IMS Content Packaging test/import package** for CSC1060 UDL starter-shell content.

## Recommended import workflow

1. Download the root repository file `D2L_UDL_StarterShell_CSC1060.zip`.
2. In Brightspace, open a **blank test shell** whenever possible.
3. Go to **Course Admin -> Import/Export/Copy Components**.
4. Choose **Import Components** and upload `D2L_UDL_StarterShell_CSC1060.zip`.
5. Review imported content before copying or rebuilding anything in a live course.

### Packaging requirement for rebuilds

- The ZIP must be created from **inside** `d2l-import-package/`.
- `imsmanifest.xml` and the HTML content files must appear at the **archive root**.
- Do **not** upload or zip a parent folder so that files end up nested under `d2l-import-package/`.

## Expected imported contents

- Start Here page
- UDL course blueprint
- Accessibility checklist
- Weekly module template
- Sample Module 1 for early Java content
- Assessment and feedback guidance
- Suggested course map

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
