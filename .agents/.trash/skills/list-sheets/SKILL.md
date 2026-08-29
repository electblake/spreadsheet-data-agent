---
name: list-sheets
description: List worksheet indexes and names in an Excel workbook using Spreadsheet Data Agent. Use when choosing a worksheet by name or zero-based index for another workbook operation.
---

# List Sheets

Run the project tool from the repository root:

```powershell
uv run python -m SpreadsheetDataAgent.tools.list_sheets --file <workbook-path-or-name>
```

The file argument is resolved with the project's workbook search rules. The tool opens the workbook read-only and prints one zero-based worksheet index and worksheet name per line in workbook order.

Preserve worksheet names exactly when passing them to another tool. Use `$search-workbooks` first when the intended workbook is ambiguous. The command does not create an output file. Let lookup, workbook parsing, and dependency failures surface directly.
