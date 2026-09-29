import json
from pathlib import Path

from loguru import logger
from openai import OpenAI
from openpyxl import Workbook
from pydantic import BaseModel
from spreadsheet_data_agent.config import MODEL_ID
from spreadsheet_data_agent.helpers import document_files
from spreadsheet_data_agent.helpers.embeddings import num_tokens
from spreadsheet_data_agent.helpers.workbooks import (
    sheet_to_data,
    to_data,
)

QUESTION_PROMPT = """Convert the supplied workbook values into a product usage timeline.

Workbook evidence:
{workbook_evidence}
"""

NAMED_RANGE = "USAGE_TIMELINE"

class ProductUsageTimeline(BaseModel):
    columns: list[str]
    rows: list[list[str | int | float]]

def run_task(
    wb: Workbook,
    sheet_name: str | None = None,
    sheet_index: int | None = None,
) -> dict:
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

    if sheet_name is not None:
        workbook_values = sheet_to_data(wb[sheet_name])
    elif sheet_index is not None:
        workbook_values = sheet_to_data(wb.worksheets[sheet_index])
    else:
        workbook_values = to_data(wb)

    logger.trace("workbook_values: {} tokens", num_tokens(json.dumps(workbook_values)))

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
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="Workbook path; absolute or relative to the current directory or data directory.",
    )
    sheet_selector = parser.add_mutually_exclusive_group()
    sheet_selector.add_argument(
        "-s",
        "--sheet",
        help="Limit usage inference to one worksheet.",
    )
    sheet_selector.add_argument(
        "-i",
        "--index",
        type=int,
        help="Limit usage inference to a worksheet by zero-based index.",
    )
    args = parser.parse_args()

    if file_path := document_files.select_file_from_name(args.file):
        if wb := document_files.load_workbook_file(file_path):
            usage_timeline = run_task(
                wb,
                sheet_name=args.sheet,
                sheet_index=args.index,
            )
            output_path = document_files.save_as_csv(usage_timeline["columns"], usage_timeline["rows"], file_path)
            wb.close()
        else:
            logger.critical("load_workbook_file failed given {}", file_path)
    else:
        logger.critical("select_file_from_name returned None for {}", args.file)

# TODO: define fastmcp-compatible interface below
