# Meeting Readiness Auditor

[中文说明](README.zh-CN.md)

An open-source Codex Skill that audits a business presentation against its supporting files, separates confirmed errors from unresolved risks, and prepares evidence-grounded answers for the meeting that follows.

It is designed for management reviews, operating reviews, sales reports, project updates, and client proposals. The current workflow is optimized for Chinese-language materials and outputs.

## What it does

- Extracts evidence from PPTX, XLSX/XLSM, CSV, DOCX, and PDF files into a local, queryable workspace.
- Checks arithmetic, formulas, metric definitions, time windows, units, chart claims, cross-file consistency, attribution, segmentation, and execution readiness.
- Distinguishes confirmed errors, definition risks, logic gaps, visual risks, important omissions, and issues that still need investigation.
- Generates an interactive HTML report, a mobile-friendly rehearsal page, an XLSX action workbook, and a one-page Markdown briefing.
- Keeps deterministic extraction and validation in scripts while leaving business judgment to the agent, with explicit evidence and uncertainty boundaries.

## Privacy model

The bundled scripts process files locally and do not upload source documents. Your chosen agent runtime may have its own data-handling behavior, so review that runtime before using confidential material. Generated workspaces can contain extracted business data and absolute local paths; keep them out of version control and delete them according to your retention policy.

## Install for Codex

```bash
git clone https://github.com/sekhouwan2024-ui/meeting-readiness-auditor.git
cd meeting-readiness-auditor
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p ~/.codex/skills
ln -s "$(pwd)/skill/meeting-readiness-auditor" ~/.codex/skills/meeting-readiness-auditor
```

Restart Codex after installation. Then invoke it explicitly:

```text
Use $meeting-readiness-auditor to audit this presentation against the attached source files and prepare me for the review meeting.
```

## Local smoke test

```bash
.venv/bin/python examples/create_demo_materials.py --out demo-input
.venv/bin/python skill/meeting-readiness-auditor/scripts/prepare_materials.py demo-input --out demo-output --no-render
.venv/bin/python skill/meeting-readiness-auditor/scripts/validate_workspace.py demo-output
.venv/bin/python skill/meeting-readiness-auditor/scripts/query_evidence.py demo-output --query revenue --limit 10
.venv/bin/python skill/meeting-readiness-auditor/scripts/validate_audit.py examples/audit_result.example.json
.venv/bin/python skill/meeting-readiness-auditor/scripts/render_report.py examples/audit_result.example.json --out demo-report
```

Run the automated checks with:

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python /path/to/skill-creator/scripts/quick_validate.py skill/meeting-readiness-auditor
```

LibreOffice and Poppler are optional. When both are installed, PPTX slides can also be rendered to preview images for visual inspection.

## Repository layout

```text
skill/meeting-readiness-auditor/  # installable Codex Skill
examples/                         # synthetic, non-sensitive demo inputs/results
tests/                            # end-to-end script smoke tests
.github/workflows/                # continuous integration
```

## Important limits

This is a pre-meeting review aid, not a financial audit, legal opinion, or management decision maker. Scanned documents, image-only charts, complex embedded objects, macros, and domain-specific accounting rules may require manual or professional review. Every generated conclusion should be checked by the person responsible for the presentation.

## Contributing

Bug reports, reproducible edge cases, new domain lenses, and improvements to evidence validation are welcome. Please use synthetic or properly anonymized fixtures and never commit confidential business material. See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the public [roadmap](ROADMAP.md).

## License

[MIT](LICENSE)
