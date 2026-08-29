---
name: predict-usage-sheet-name
description: Ask the configured OpenAI model to identify the worksheet that directly records recurring inventory or product usage over time. Use when a workbook has multiple sheets and the authoritative usage-history sheet is unknown.
---

# Predict Usage Sheet Name

Run the project tool from the repository root with `OPENAI_API_KEY` available to the OpenAI client:

```powershell
uv run python -m SpreadsheetDataAgent.tools.predict_usage_sheet_name --file <workbook-path-or-name>
```

The tool resolves the workbook through the project data search, extracts candidate header evidence from every worksheet, and asks `SpreadsheetDataAgent.config.MODEL_ID` to select exactly one sheet. It is designed to reject logistics detail, audit, reconciliation, exception, and error-report sheets.

Read the suggested sheet name and zero-based index from the Loguru output. If the supplied evidence is insufficient or tied, the model returns `UNDETERMINED` and the tool fails. Let that and all API, authentication, workbook, and dependency failures surface directly.

Use `$list-sheets` when deterministic worksheet enumeration is sufficient. This command does not create a data artifact.
