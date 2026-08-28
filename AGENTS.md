# Spreadsheet Data Agent

## Local skills

- [`$ndjson-for-sheet`](.agents/skills/ndjson-for-sheet/SKILL.md) — Convert an XLSX workbook into structured, line-oriented NDJSON.
- [`$summarize-sheet`](.agents/skills/summarize-sheet/SKILL.md) — Create Markdown, model-context, and NDJSON summaries from an XLSX workbook.
- [`$inventory-creator`](.agents/skills/inventory-creator/SKILL.md) — Standardize monthly product usage into reusable NDJSON and a single-company inventory workbook.

## Data

- [`data/`](data/AGENTS.override.md) — Data layout and source-versus-generated-data guidance.

## Agent-created files

- Agents must place every generated task artifact, temporary file, cache, report, workbook, export, sidecar, and generated directory under `data/processed/` or `data/interim/`.
- Use `data/processed/` for final, reproducible deliverables and `data/interim/` for temporary or intermediate artifacts.
- Never create `output/`, `outputs/`, `artifacts/`, or any other task-output directory outside `data/processed/` and `data/interim/`.
- Do not create files elsewhere in the repository unless the user explicitly requests a change to project source code, configuration, documentation, or agent skills.
