---
name: search-workbooks
description: Resolve an Excel workbook filename or path using Spreadsheet Data Agent's workbook search rules. Use when a workbook must be located before inspection or processing.
---

# Search Workbooks

Run the project tool from the repository root:

```powershell
uv run python -m SpreadsheetDataAgent.tools.search_workbooks --file <workbook-path-or-name>
```

The tool checks, in order, whether the argument is an existing path, whether it is directly under `SpreadsheetDataAgent.config.DATA_PATH`, and whether its exact basename occurs in the configured data tree. It prints the resolved absolute path, or `None` when there is no exact match.

Prefer an absolute path when duplicate basenames may exist. This tool only resolves workbook locations; use `$list-workbooks` to inventory every supported workbook. Let command failures surface directly.
