import argparse

from SpreadsheetDataAgent.helpers.workbooks import list_workbooks


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="List workbook files available under the data directory."
    )


def main() -> None:
    parser = build_parser()
    parser.parse_args()

    for workbook_name, workbook_path in list_workbooks():
        print(workbook_name, workbook_path)


if __name__ == "__main__":
    main()
