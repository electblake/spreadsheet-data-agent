import csv
import json
from pathlib import Path

from loguru import logger
from openai import OpenAI
from openpyxl import Workbook
from workbook import load_workbook, to_data

from SpreadsheetDataAgent.config import DATA_PATH, MODEL_ID

QUESTION_PROMPT = """Convert the supplied workbook values into a product usage timeline.

Workbook evidence:
{workbook_evidence}
"""

NAMED_RANGE = "USAGE_TIMELINE"

def predict_usage_timeline(wb: Workbook) -> dict:
    """Return a continuous monthly product usage timeline."""

    client = OpenAI()

    system_prompt = """You convert workbook values into a normalized product usage timeline.

Use only the supplied literal values.

Output rules:
- Return a rectangular table represented by one columns array and one rows array.
- The first two columns must be exactly product_id and product_description.
- Copy each product identifier and product description from the supplied values.
- Determine the earliest and latest calendar month represented by the supplied values.
- After product_description, include every calendar month from the earliest through the latest month, in chronological order, formatted as YYYY-MM.
- Do not skip intervening months.
- Return exactly one row per product.
- Each row must contain the product identifier, product description, and one numeric total for every month column.
- Sum values when the source contains multiple usage entries for the same product and month.
- Use numeric zero when a product has no usage in a month within the continuous month range.
- Every row must have exactly the same number of values as the columns array.
- Do not return worksheet names, named ranges, cell ranges, cell coordinates, source references, explanations, or supporting text.
"""

    workbook_values = to_data(wb)
    logger.trace("workbook_values: {}", workbook_values)

    workbook_evidence = json.dumps(workbook_values, ensure_ascii=False)

    logger.debug("Creating product usage timeline response")
    response = client.responses.create(
        model=MODEL_ID,
        instructions=system_prompt,
        input=QUESTION_PROMPT.format(
            workbook_evidence=workbook_evidence,
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "product_usage_timeline",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": [
                                        "string",
                                        "number",
                                    ]
                                },
                            },
                        },
                    },
                    "required": ["columns", "rows"],
                    "additionalProperties": False,
                },
            }
        },
    )
    logger.debug("Created product usage timeline response")

    out = json.loads(response.output_text)
    logger.trace("predicted response: {}", out)
    return out

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True)
    args = parser.parse_args()

    if wb := load_workbook(args.file):
        logger.debug("Opened workbook: {}", args.file)
        usage_timeline = predict_usage_timeline(wb)
        output_path = DATA_PATH / "processed" / "inventory" / Path(args.file).with_suffix(".csv").name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(usage_timeline["columns"])
            writer.writerows(usage_timeline["rows"])
        wb.close()
    else:
        raise FileNotFoundError(args.file)
