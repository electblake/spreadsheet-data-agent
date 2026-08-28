import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.utils.cell import range_boundaries
from openpyxl.worksheet.worksheet import Worksheet


def predict_layout_options(wb: Workbook):
    return {
        "sheetnames": wb.sheetnames,

    }

def load_workbook(file_path: str | Path) -> Workbook | None:
    """returns read-only file handler for xlsx/xlsm files"""
    file_path = Path(file_path)
    from openpyxl import load_workbook
    if file_path and file_path.exists and file_path.is_file():
        # https://openpyxl.readthedocs.io/en/stable/tutorial.html#loading-from-a-file
        return load_workbook(filename=file_path, read_only=True, keep_vba=True, rich_text=True, keep_links=True, data_only=False)
    return None

def read_defined_name_ranges(wb: Workbook) -> list[tuple[str, str, list[str]]]:
    defined_names = list(wb.defined_names.items())
    for sheet in wb.worksheets:
        defined_names.extend(sheet.defined_names.items())

    ranges_by_name_and_sheet = {}
    for name, defined_name in defined_names:
        for sheet_name, cell_range in defined_name.destinations:
            ranges_by_name_and_sheet.setdefault((name, sheet_name), []).append(
                cell_range.replace("$", "")
            )

    return [
        (name, sheet_name, cell_ranges)
        for (name, sheet_name), cell_ranges in ranges_by_name_and_sheet.items()
    ]

def named_range_to_data(wb: Workbook, named_range:str) -> list[list[int|str|float]]:
    named_range_data = []
    for sheet_name, cell_range in wb.defined_names[named_range].destinations:
        min_col, min_row, max_col, max_row = range_boundaries(cell_range)
        named_range_data.extend(
            [
                value
                if type(value) in (str, int, float)
                else ""
                if value is None
                else str(value)
                for value in row
            ]
            for row in wb[sheet_name].iter_rows(
                min_row=min_row,
                max_row=max_row,
                min_col=min_col,
                max_col=max_col,
                values_only=True,
            )
        )
    return named_range_data

def sheet_to_data(ws: Worksheet) -> list:
    """"""
    wb_data=[]
    wb_data.extend(
        [
            value
            if type(value) in (str, int, float)
            else ""
            if value is None
            else str(value)
            for value in row
        ]
        for row in ws.iter_rows(values_only=True)
    )
    return wb_data

def to_data(wb: Workbook) -> list[list[str|int|float]]:
    wb_data = []
    for ws in wb.worksheets:
        wb_data.append({
            "worksheet_title": ws.title,
            "worksheet_max_rows": ws.max_row,
            "worksheet_max_column": ws.max_column,
            "named_ranges": read_defined_name_ranges(wb)
        })
        wb_data.extend(sheet_to_data(ws))
    return wb_data

def to_text(wb: Workbook) -> str:
    wb_data = to_data(wb)
    return json.dumps(wb_data, ensure_ascii=False)
