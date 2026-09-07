# Native Brightspace/D2L UDL Revision Package

## Which package to upload
Upload this file from the repository root:

- `D2L_CSC1060_UDL_Revised_From_Original.zip`

This package is rebuilt from the original native export (`D2LExport_662798_S_PPCC_CSC10601H1_202720_20269657.zip`) and keeps the original package structure/metadata.

## Recommended Brightspace import workflow (existing shell)
1. In Brightspace, open a **blank/duplicate test shell first**.
2. Go to **Course Admin -> Import/Export/Copy Components**.
3. Choose **Import Components** and upload `D2L_CSC1060_UDL_Revised_From_Original.zip`.
4. If Brightspace prompts for selective import, prefer importing **course components/content** first and review results before importing additional tool components.
5. After validation in the test shell, repeat in the target shell.

## What was changed automatically
Automated UDL support updates were added to learner-facing HTML stored in:
- `news_d2l.xml` announcements content
- `dropbox_d2l.xml` assignment instructions
- `syllabus_d2l.xml` syllabus description

Applied changes include:
- clearer heading structure;
- added purpose/instructions/what to submit/how assessed/help/next-step sections;
- chunked plain-language guidance;
- descriptive link text where possible;
- inferred image alt text when missing;
- table caption/header improvements when tables exist;
- instructor placeholders: `[INSTRUCTOR CONFIRM]` for institution-specific details.

Original substantive content remains present; UDL support text was added around existing content.

## Instructor confirmation still required
Review all `[INSTRUCTOR CONFIRM]` placeholders before publishing, especially for:
- contact methods and response times
- office hours and tutoring/support channels
- any local policy clarifications

## Validation outputs
Validation artifacts are in `native-d2l-udl-revision/staging/`:
- `transformation-summary.json` (machine-readable changed-file/category summary)
- `validation-report.json` (integrity/structure/XML/HTML/reference/secret checks)

## Known limitation
No offline process can guarantee compatibility with every institution's Brightspace configuration.
Always test this package in a blank or duplicate shell first, then import into the live shell only after successful verification.
