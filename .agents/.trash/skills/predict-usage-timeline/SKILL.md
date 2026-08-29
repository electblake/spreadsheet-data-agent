---
name: predict-usage-timeline
description: Convert workbook values into a continuous monthly product-usage CSV with the configured OpenAI model. Use when product identifiers, descriptions, and monthly quantities must be normalized from a workbook or one selected worksheet.
---

# Predict Usage Timeline

Run the project tool from the repository root with `OPENAI_API_KEY` available to the OpenAI client:

```powershell
uv run python -m SpreadsheetDataAgent.tools.predict_usage_timeline --file <workbook-path-or-name>
```

Optionally limit the evidence to exactly one worksheet by name or zero-based index:

```powershell
uv run python -m SpreadsheetDataAgent.tools.predict_usage_timeline --file <workbook> --sheet <exact-sheet-name>
uv run python -m SpreadsheetDataAgent.tools.predict_usage_timeline --file <workbook> --index <zero-based-index>
```

Do not pass both selectors. With neither selector, the tool sends values from every worksheet. Use `$predict-usage-sheet-name` first when the authoritative usage sheet is unknown, or `$list-sheets` when it is known but its exact selector is needed.

The response is normalized to `product_id`, `product_description`, and every calendar month from the earliest through latest observed month. Duplicate product-month values are summed and missing intervening months become numeric zero.

The tool writes `<input-stem>.csv` under `SpreadsheetDataAgent.config.DATA_PATH/processed/inventory/`. Treat the configured location as the output contract. Let API, authentication, parsing, lookup, and filesystem failures surface directly.
