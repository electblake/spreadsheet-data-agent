---
name: summarize-sheet
description: "Summarize a local XLSX workbook into five deterministic project artifacts: a factual Markdown table summary, isolated company/account metadata, direct model context, lossless Transco sheet NDJSON, and a JSON manifest. Use when spreadsheet contents need human- and model-readable summaries without modifying the workbook."
---

# Summarize Sheet

Create exactly five files under the current project's `data/processed/tables/`. Do
not modify the source workbook or create temporary, staging, or helper files.

Use the installed `Spreadsheets` skill for read-only local workbook inspection. Do
not import, call, or copy code from the Spreadsheet Data Agent app. Use the installed
project-local `$ndjson-for-sheet` skill for the NDJSON conversion.

## Inputs

- A local `.xlsx` path.
- An optional worksheet name. When omitted, select the workbook's first worksheet,
  matching the app workflow.
- A reporting date and its Python `datetime.strptime` format. Use an explicit date
  supplied by the user or an unambiguous reporting date stated by the workbook; do
  not guess an ambiguous date.

## Plan deterministic outputs

Before reading workbook cells, run:

```powershell
python .agents/skills/summarize-sheet/scripts/plan_outputs.py <workbook.xlsx> --date <date> --date-format <format> [--sheet <exact-title>]
```

This stdlib-only script reads file metadata and bytes for SHA-256 identity. It does
not parse workbook contents or write files. Its JSON is the authority for the
canonical title, source identity, worksheet selection, and all output paths.

Use the five `outputs.*.path` values verbatim. Use `title` verbatim only in the
company artifact; never place it in the summary because it may contain the company
or account name. Never invent, shorten, or normalize artifact names separately. The
naming convention is:

```text
YYYY-MM-DD--source-slug[--sheet-<sheet-slug>]--sha256-<first-16-hex>--v3--<role>.<ext>
```

The full source SHA-256 is recorded at `source.sha256`. If `complete` is `true`, the
same source bytes, reporting date, and worksheet selection already have all five
artifacts; return those paths without regenerating them. Otherwise create only the
outputs whose `exists` value is `false`.

## Outputs

### `outputs.summary_markdown.path`

This is the entry point that agents read first. Write a factual summary of the
selected worksheet's table content, grounded only in explicit labels, values, and
stored formula results. Include the reporting date, selected worksheet, used range,
table dimensions, primary units when explicitly labeled, and directly stored or
formula-produced totals that are clearly labeled in the workbook. Identify source
cell or range addresses for summarized values.

Start with an `Artifacts` section containing Markdown links to every other artifact.
Use the exact filenames from the plan as relative link targets and give each link a
single factual sentence describing its contents:

- `outputs.company_markdown.filename`
- `outputs.model_context.filename`
- `outputs.sheet_ndjson.filename`
- `outputs.manifest_json.filename`

Do not repeat the company/account name or its identifying details in this file; the
link to the company artifact is the only company/account reference.

This is a table summary, not a business analysis. Do not add conclusions,
observations, interpretations, implications, recommendations, concerns, rankings,
comparisons, trends, signals, anomalies, or inferred business meaning. Do not
calculate new ratios, shares, concentrations, shortages, excesses, or other derived
metrics. Do not characterize values as large, small, high, low, good, bad, current,
stale, unusual, meaningful, or problematic. Describe what the labeled table stores,
without judging or explaining it.

End with a factual note that stored formula results were read without recalculating
the workbook.

### `outputs.company_markdown.path`

Isolate workbook-local company or account identity in this artifact. Record only:

- the exact company/account/customer label or title stated by the workbook;
- the source worksheet and cell or range containing each identifying label;
- the reporting date and its source cell when the workbook explicitly stores it.

Do not research, enrich, profile, analyze, or infer facts about the company. Do not
copy table totals, operational details, conclusions, or observations into this file.

### `outputs.model_context.path`

Write plain text in this exact shape:

```text
Workbook overview:
Sheet,Active,Used range,Rows,Columns
<one CSV record per worksheet in workbook order>

Selected sheet preview (<sheet name>, first 100 rows and 50 columns):
A,B,C,<remaining Excel column letters through the preview width>
<CSV records for worksheet rows 1 through min(used rows, 100)>
```

For this file, read formulas as formula text rather than cached results. Preserve cell
values and blank cells; do not normalize, fill, aggregate, infer headers, or
reinterpret them.

The overview fields mean:

- `Sheet`: exact, case-sensitive worksheet title.
- `Active`: `True` only for the workbook's active worksheet; otherwise `False`.
- `Used range`: Excel A1-style populated extent reported by workbook inspection.
- `Rows` and `Columns`: the used extent's last row and column counts.

The preview covers columns 1 through `min(used columns, 50)` and uses Excel column
letters as its CSV header. Row 1 remains data; never promote it to headers.

Serialize both tables as CSV: comma delimiter, quote fields containing commas,
quotes, or line breaks, double embedded quotes, and emit empty fields for blank
cells. Preserve worksheet order and cell order. Include the single blank line shown
between the two sections, matching the app's CSV serialization. End the output after
the final CSV record.

### `outputs.sheet_ndjson.path`

Run the bundled conversion from `$ndjson-for-sheet` against the source workbook and
write its output directly to this path.

### `outputs.manifest_json.path`

Create this last. Use [the sheet manifest schema](assets/sheet-manifest.schema.json)
and include the source identity, reporting date, worksheet selection, and the other
four output files with their roles, filenames, media types, SHA-256 hashes, and byte
sizes. Keep filenames relative and do not include the manifest in its own `files`
array. Set `$schema` to
`../../../.agents/skills/summarize-sheet/assets/sheet-manifest.schema.json`.

## Verification

Run the planner again with the same arguments and require `complete` to be `true`.
Confirm that its output hashes the current source, the model context matches the
selected sheet and 100-by-50 bounds, the summary links all four companion artifacts,
the company/account identity appears only in the company artifact, every Markdown
claim is a direct description of a labeled source cell or stored total, and every
NDJSON line parses with the first record declaring `transco.sheet-ndjson` version
`1`. Validate the manifest against `assets/sheet-manifest.schema.json` and
confirm it lists the other four outputs.
