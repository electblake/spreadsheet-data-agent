# Spreadsheet Data Agent

## Local skills

- [`$list-workbooks`](.agents/skills/list-workbooks/SKILL.md) — List workbook files under the configured data directory.
- [`$search-workbooks`](.agents/skills/search-workbooks/SKILL.md) — Resolve a workbook filename or path.
- [`$list-sheets`](.agents/skills/list-sheets/SKILL.md) — List zero-based worksheet indexes and names.
- [`$predict-usage-sheet-name`](.agents/skills/predict-usage-sheet-name/SKILL.md) — Identify the worksheet that records product usage history.
- [`$predict-usage-timeline`](.agents/skills/predict-usage-timeline/SKILL.md) — Normalize workbook values into a monthly product-usage CSV.
- [`$sheet-to-ndjson`](.agents/skills/sheet-to-ndjson/SKILL.md) — Convert an XLSX workbook into structured, line-oriented NDJSON.

## Data

- [`data/`](data/AGENTS.override.md) — Data layout and source-versus-generated-data guidance.

## Agent-created files

- Agents must place every generated task artifact, temporary file, cache, report, workbook, export, sidecar, and generated directory under `data/processed/` or `data/interim/`.
- Use `data/processed/` for final, reproducible deliverables and `data/interim/` for temporary or intermediate artifacts.
- Never create `output/`, `outputs/`, `artifacts/`, or any other task-output directory outside `data/processed/` and `data/interim/`.
- Do not create files elsewhere in the repository unless the user explicitly requests a change to project source code, configuration, documentation, or agent skills.
