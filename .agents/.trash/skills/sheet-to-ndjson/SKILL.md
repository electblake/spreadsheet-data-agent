---
name: sheet-to-ndjson
description: Convert an XLSX workbook into transco.sheet-ndjson version 1 records using the project's tool. Use when workbook, worksheet, merged-range, cell, formula, value-type, and number-format data is needed as line-oriented JSON.
---

# Sheet to NDJSON

Run the project tool from the repository root:

```powershell
uv run python -m SpreadsheetDataAgent.tools.sheet_to_ndjson <input.xlsx> <output.ndjson>
```

Place generated output under `data/processed/` for a final reproducible deliverable or `data/interim/` for temporary work. The output parent directory must already exist.

The tool reads the XLSX ZIP/XML structure directly and writes compact UTF-8 NDJSON in this order:

1. One `workbook` record declaring schema `transco.sheet-ndjson` version `1`.
2. One `sheet` record for each worksheet.
3. Any `merged_range` records for that worksheet.
4. One `cell` record for each serialized cell, including its address, numeric row and column, typed value, formula, and number format.

This tool accepts `.xlsx` input; it is not the general workbook lookup tool and does not search the configured data directory. Let invalid archives, unsupported workbook structures, missing dependencies, and write failures surface directly.
