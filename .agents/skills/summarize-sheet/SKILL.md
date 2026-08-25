---
name: summarize-sheet
description: "Summarize a local XLSX workbook into three deterministically named project artifacts: a grounded Markdown business summary, a direct model-inference context, and a lossless Transco sheet NDJSON conversion. Use when spreadsheet contents need both human and model-readable summaries without modifying the workbook."
---

# Summarize Sheet

Create exactly three files under the current project's `data/processed/tables/`. Do
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

Use `title` and the three `outputs.*.path` values verbatim. Never invent, shorten, or
normalize artifact names separately. The naming convention is:

```text
YYYY-MM-DD--source-slug[--sheet-<sheet-slug>]--sha256-<first-16-hex>--<role>.<ext>
```

The full source SHA-256 is recorded at `source.sha256`. If `complete` is `true`, the
same source bytes, reporting date, and worksheet selection already have all three
artifacts; return those paths without regenerating them. Otherwise create only the
outputs whose `exists` value is `false`.

## Outputs

### `outputs.summary_markdown.path`

Write an agent-authored summary grounded in the workbook's labels, values, and stored
formula results. Include:

- company or account, reporting date, workbook scope, and primary units;
- inventory, order, production, and sales totals that the workbook supports;
- the largest positions and meaningful demand or coverage signals;
- shortage, excess, data-quality, identifier, and external-link concerns;
- a note distinguishing stored formula results from recalculation.

Do not invent company facts or assign a business meaning to an unlabeled field.

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

## Verification

Run the planner again with the same arguments and require `complete` to be `true`.
Confirm that its output hashes the current source, the model context matches the
selected sheet and 100-by-50 bounds, the Markdown claims reconcile to source cells
or stored totals, and every NDJSON line parses with the first record declaring
`transco.sheet-ndjson` version `1`.
