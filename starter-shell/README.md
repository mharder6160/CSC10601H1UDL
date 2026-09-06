# CSC1060 UDL Starter-Shell Package (Instructor Draft)

This package provides instructor-ready starter content for **CSC1060 / Computer Science I: Java** in Brightspace/D2L, redesigned with Universal Design for Learning (UDL) principles.

## Source materials preserved

Original source files remain unchanged at repository root:

- `D2LExport_662798_S_PPCC_CSC10601H1_202720_20269657.zip`
- `Fall-2026-CSC-(PPSC)-1060-1H1-Computer-Science-I_-Java.pdf`

## What is source-derived vs newly authored

### Source-derived facts used in this package

Derived from the syllabus PDF and D2L export XML:

- Course title and level: Computer Science I: Java
- Delivery method listed as hybrid
- Credit/contact hours in source syllabus
- Course outcomes and topical outline themes
- Existing module sequence (Start Here, Module 1 ... Module 14, final review/final project)
- Existing programming-project cadence (Module 3 onward, plus midterm/final projects)
- Existing policy signals: attendance emphasis, non-participation drop warning, institutional integrity/AI language

### Newly authored content in this package

All files under `starter-shell/` are newly authored as UDL starter-shell materials, including:

- UDL blueprint and implementation guidance
- Course home/welcome page content
- Weekly reusable module template
- Complete sample introductory module (Java program structure, variables, data types, input/output)
- UDL-aligned assessment and feedback guidance
- Accessibility/quality review checklist
- Suggested 15-week course map
- D2L-ready HTML companions for key pages

## Folder structure

- [`blueprint/udl-course-blueprint.md`](./blueprint/udl-course-blueprint.md)
- [`modules/course-home-welcome.md`](./modules/course-home-welcome.md)
- [`modules/weekly-module-template.md`](./modules/weekly-module-template.md)
- [`modules/sample-module-01-early-java.md`](./modules/sample-module-01-early-java.md)
- [`assessments/assessment-feedback-guidance.md`](./assessments/assessment-feedback-guidance.md)
- [`checklists/accessibility-quality-checklist.md`](./checklists/accessibility-quality-checklist.md)
- [`course-map/suggested-15-week-course-map.md`](./course-map/suggested-15-week-course-map.md)
- [`d2l-html/welcome-page.html`](./d2l-html/welcome-page.html)
- [`d2l-html/weekly-module-template.html`](./d2l-html/weekly-module-template.html)
- [`d2l-html/sample-module-early-java.html`](./d2l-html/sample-module-early-java.html)

## How to use in Brightspace/D2L

1. In your starter shell, create a **Start Here** module and weekly modules.
2. Copy/paste from Markdown pages into D2L HTML editor, or upload HTML files from `starter-shell/d2l-html/`.
3. Update every `[INSTRUCTOR CONFIRM]` placeholder before publishing.
4. Attach existing course files/quizzes/projects from your D2L shell where indicated.
5. Apply this structure consistently across all weeks for predictable navigation.

## Alignment to existing course shell

- Welcome content aligns to your existing **Start Here** concept.
- Weekly template aligns to the current module-based design (Module 1–14 pattern).
- Sample module is intentionally early-sequence and maps to introductory Java foundations.
- Course map mirrors the observed progression (algorithms/SDLC -> Java basics -> selections/loops/methods -> arrays -> objects -> exceptions/text I/O -> recursion -> final project/review).

## Change summary

- Added a substantial UDL starter-shell package in a dedicated `starter-shell/` directory.
- Included both Markdown and simple accessible HTML for direct D2L use.
- Marked institution-specific or uncertain details as `[INSTRUCTOR CONFIRM]` instead of inventing facts.

## Limitations

- This package does **not** import content into D2L automatically.
- Exact due dates, grading weights implementation details, attendance penalties, and AI policy option selection must be finalized by instructor/institution.
- Existing attached assignment documents/rubrics in the D2L export were not rewritten verbatim; this package provides UDL-ready structure and sample content to integrate with those assets.
