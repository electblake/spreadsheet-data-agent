---
name: list-workbooks
description: List Excel workbook files available under Spreadsheet Data Agent's configured data directory. Use when locating workbook inputs before running another project tool.
---

# List Workbooks

Run the project tool from the repository root:

```powershell
uv run python -m SpreadsheetDataAgent.tools.list_workbooks
```

The tool recursively scans `SpreadsheetDataAgent.config.DATA_PATH` for formats supported by `openpyxl` and prints one workbook filename and absolute path per line, sorted by path.

Use the printed absolute path as the `--file` value for workbook tools when duplicate filenames could exist. The command does not create an output file. Let dependency, configuration, and filesystem failures surface directly.
