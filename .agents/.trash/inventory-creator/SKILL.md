---
name: inventory-creator
description: Create a standardized single-company monthly inventory-usage workbook and reusable NDJSON intermediates from an XLSX worksheet whose product and monthly usage columns are identified explicitly. Use when client usage history must span every month from the source's earliest through latest available month without shipping, VPO, order, quarterly-value, or other operational fields.
---

# Inventory Creator

Create one product-usage history sheet with `Product ID`, `Product Name`, and one
usage column per calendar month. The source workbook is read-only. Write NDJSON under
`data/interim/` and the generated workbook under `data/processed/`.

## Inputs

Identify these exact source locations before running the script:

- worksheet title and header row;
- product ID column;
- product name column;
- monthly usage columns only.

Pass monthly columns as Excel letters or inclusive ranges. Omit quarterly totals,
shipping, VPO, order, forecast, and other non-usage columns. Each selected monthly
header must contain a month and year as an Excel date or parseable date label.

## Run

```powershell
python .agents/skills/inventory-creator/scripts/create_inventory.py run <input.xlsx> <output.xlsx> --sheet <exact-title> --header-row <row> --product-id-column <letter> --product-name-column <letter> --month-columns <letter-or-range> [<letter-or-range> ...] --interim-dir <directory>
```

Example selection that excludes quarter columns between monthly groups:

```powershell
python .agents/skills/inventory-creator/scripts/create_inventory.py run data/external/inventory/source.xlsx data/processed/inventory/source-usage.xlsx --sheet Usage --header-row 3 --product-id-column A --product-name-column B --month-columns C:E G:I K:M --interim-dir data/interim/source-usage
```

The script invokes `$ndjson-for-sheet` to create a lossless source NDJSON file, reads
the selected cells from NDJSON, aggregates usage by product and month, writes a
normalized inventory NDJSON file, and creates the XLSX from that normalized NDJSON.
Let failures surface directly.

## Output contract

- One worksheet named `Usage History`.
- One row per distinct Product ID and Product Name pair, in source order.
- Month labels from the earliest selected source month through the latest, including
  intervening calendar months.
- Blank product-month cells when the source has no usage value; never substitute zero.
- Summed usage when duplicate source rows or selected columns represent the same
  product and month.
- No company column because each workbook represents one company.
- No quarter usage values or extraneous operational fields.
- Two reusable `transco.sheet-ndjson` version `1` files in the interim directory:
  the imported source workbook and the normalized inventory sheet.

## Verify

Confirm the normalized NDJSON begins with the declared schema and that its month
headers match the generated workbook from earliest through latest month. Open the
XLSX and confirm that blank usage remains blank, duplicate product/month usage is
summed, headers are legible, and the sheet contains no unrelated fields.
