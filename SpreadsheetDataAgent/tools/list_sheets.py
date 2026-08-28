import argparse
from pathlib import Path

from SpreadsheetDataAgent.helpers.workbooks import (
    list_sheets,
    load_workbook,
    search_workbooks,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="List worksheets in a workbook."
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        type=Path,
        help="Workbook filename or path.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    workbook_path = search_workbooks(args.file)
    workbook = load_workbook(workbook_path)
    for sheet_index, sheet_name in list_sheets(workbook):
        print(sheet_index, sheet_name)
    workbook.close()


if __name__ == "__main__":
    main()
