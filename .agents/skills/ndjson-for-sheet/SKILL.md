---
name: ndjson-for-sheet
description: Convert an Excel .xlsx workbook into structured NDJSON records for workbook metadata, worksheets, merged ranges, cells, formulas, cached values, value types, and number formats. Use when Codex needs a portable, line-oriented representation of spreadsheet contents for inventory data exchange, inspection, indexing, or downstream processing.
---

# NDJSON for Sheet

Convert an `.xlsx` workbook with the bundled script. The skill vendors `ndjson` 0.3.1 under `vendor/`; do not create a virtual environment or install packages.

## Run

```powershell
python scripts/sheet_to_ndjson.py input.xlsx output.ndjson
```

Resolve the script path relative to this skill directory when invoking it elsewhere. Let command failures surface directly.

## Output contract

Write records in this order:

1. One `workbook` record with schema `transco.sheet-ndjson` version `1`.
2. One `sheet` record per worksheet.
3. Zero or more `merged_range` and `cell` records for that worksheet.

Cell records preserve the worksheet index and name, A1 address, row, column, typed value, formula, cached formula value, and number format. Empty cells without formulas are omitted.

Use `$ndjson-to-sheet` for the inverse conversion.
