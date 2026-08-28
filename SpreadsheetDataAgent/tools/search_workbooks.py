import argparse
from pathlib import Path

from SpreadsheetDataAgent.helpers.workbooks import search_workbooks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search for a workbook under the data directory."
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

    print(search_workbooks(args.file))


if __name__ == "__main__":
    main()
