from pathlib import Path

from openpyxl.reader.excel import SUPPORTED_FORMATS
from pydantic import BaseModel
from SpreadsheetDataAgent.config import DOCUMENTS_DATA_PATH


class WorkbookFile(BaseModel):
    name: str
    path: str

class WorkbookFiles(BaseModel):
    files: list[WorkbookFile]

def document_output_path(subdir: str, original_file_path: Path, suffix: str):
    output_path = (
        DOCUMENTS_DATA_PATH
        / Path(subdir).as_posix()
        / original_file_path.with_suffix(suffix).name
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path

def save_as_csv(columns, rows, original_file_path: Path, subdir: str = "processed/csv"):
    import csv
    output_path = document_output_path(subdir, original_file_path, ".csv")
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(columns)
        writer.writerows(rows)
    return output_path

def save_as_jsonl(rows, original_file_path: Path, subdir: str = "processed/jsonl"):
    output_path = document_output_path(subdir, original_file_path, ".jsonl")
    # ...
    return output_path

def list_workbook_files(path: str | Path = DOCUMENTS_DATA_PATH):
    """returns names and absolute paths for supported files under DOCUMENTS_DATA_PATH"""
    import os
    for entry in os.scandir(path):
        if entry.is_file():
            if Path(entry.name).suffix.lower() in SUPPORTED_FORMATS:
                yield Path(entry.path)
        elif entry.is_dir():
            yield from list_workbook_files(entry.path)

def select_file_from_name(namelike: str | Path) -> Path | None:
    """primary file input resolver with built-in checking rules in order"""

    # 1. if its a path to file
    file_path = Path(namelike)
    if file_path.is_file():
        return file_path.resolve()

    # 2. if its file at document data root
    DOCUMENTS_DATA_PATH_file = DOCUMENTS_DATA_PATH / file_path
    if DOCUMENTS_DATA_PATH_file.is_file():
        return DOCUMENTS_DATA_PATH_file.resolve()

    # 3. if its exact name of any supported workbook file
    for pathstring in list_workbook_files(DOCUMENTS_DATA_PATH):
        p = Path(pathstring)
        if p.name == namelike:
            return p

    return None
