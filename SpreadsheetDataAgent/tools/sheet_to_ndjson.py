import argparse
import posixpath
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

# VENDOR_DIR = Path(__file__).resolve().parents[1] / "vendor"
# sys.dont_write_bytecode = True
# sys.path.insert(0, str(VENDOR_DIR))

import ndjson

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

BUILTIN_NUMBER_FORMATS = {
    0: "General",
    1: "0",
    2: "0.00",
    3: "#,##0",
    4: "#,##0.00",
    9: "0%",
    10: "0.00%",
    11: "0.00E+00",
    12: "# ?/?",
    13: "# ??/??",
    14: "mm-dd-yy",
    15: "d-mmm-yy",
    16: "d-mmm",
    17: "mmm-yy",
    18: "h:mm AM/PM",
    19: "h:mm:ss AM/PM",
    20: "h:mm",
    21: "h:mm:ss",
    22: "m/d/yy h:mm",
    37: "#,##0;(#,##0)",
    38: "#,##0;[Red](#,##0)",
    39: "#,##0.00;(#,##0.00)",
    40: "#,##0.00;[Red](#,##0.00)",
    45: "mm:ss",
    46: "[h]:mm:ss",
    47: "mmss.0",
    48: "##0.0E+0",
    49: "@",
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert an XLSX workbook to transco.sheet-ndjson records."
    )
    parser.add_argument("input_xlsx", type=Path)
    parser.add_argument("output_ndjson", type=Path)
    return parser

def workbook_records(input_path):
    def qualified(namespace, tag):
        return f"{{{namespace}}}{tag}"

    def column_number(address):
        letters = "".join(character for character in address if character.isalpha())
        number = 0
        for letter in letters:
            number = number * 26 + ord(letter.upper()) - 64
        return number

    with zipfile.ZipFile(input_path) as archive:
        workbook_root = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationships = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in relationships_root.findall(qualified(PACKAGE_REL_NS, "Relationship"))
        }

        if "xl/sharedStrings.xml" not in archive.namelist():
            strings = []
        else:
            shared_strings_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [
                "".join(node.text or "" for node in item.iter(qualified(MAIN_NS, "t")))
                for item in shared_strings_root.findall(qualified(MAIN_NS, "si"))
            ]

        if "xl/styles.xml" not in archive.namelist():
            formats = ["General"]
        else:
            root = ET.fromstring(archive.read("xl/styles.xml"))
            custom = {
                int(node.attrib["numFmtId"]): node.attrib["formatCode"]
                for node in root.findall(f"{qualified(MAIN_NS, 'numFmts')}/{qualified(MAIN_NS, 'numFmt')}")
            }
            cell_xfs = root.find(qualified(MAIN_NS, "cellXfs"))
            formats = [
                custom.get(int(node.attrib.get("numFmtId", "0")), BUILTIN_NUMBER_FORMATS.get(int(node.attrib.get("numFmtId", "0")), "General"))
                for node in cell_xfs # pyright: ignore[reportOptionalIterable]
            ]

        yield {
            "record_type": "workbook",
            "schema": "transco.sheet-ndjson",
            "version": 1,
            "source_name": input_path.name,
        }

        sheets = workbook_root.find(qualified(MAIN_NS, "sheets"))
        for sheet_index, sheet in enumerate(sheets): # pyright: ignore[reportArgumentType]
            sheet_name = sheet.attrib["name"]
            relationship_id = sheet.attrib[qualified(REL_NS, "id")]
            target = relationships[relationship_id]
            target_path = target.lstrip("/")
            sheet_path = target_path if target_path.startswith("xl/") else posixpath.normpath(posixpath.join("xl", target_path))
            sheet_root = ET.fromstring(archive.read(sheet_path))
            dimension = sheet_root.find(qualified(MAIN_NS, "dimension"))
            yield {
                "record_type": "sheet",
                "sheet_index": sheet_index,
                "sheet_name": sheet_name,
                "dimension": dimension.attrib.get("ref", "A1") if dimension is not None else "A1",
            }

            merge_cells = sheet_root.find(qualified(MAIN_NS, "mergeCells"))
            if merge_cells is not None:
                for merged in merge_cells:
                    yield {
                        "record_type": "merged_range",
                        "sheet_index": sheet_index,
                        "sheet_name": sheet_name,
                        "range": merged.attrib["ref"],
                    }

            def decode_value(cell, strings):
                cell_type = cell.attrib.get("t", "n")
                value_node = cell.find(qualified(MAIN_NS, "v"))
                inline = cell.find(qualified(MAIN_NS, "is"))
                text = value_node.text if value_node is not None else None

                if cell_type == "s":
                    return strings[int(text)], "string" # pyright: ignore[reportArgumentType]
                if cell_type == "inlineStr":
                    return "".join(node.text or "" for node in inline.iter(qualified(MAIN_NS, "t"))), "string"
                if cell_type == "b":
                    return text == "1", "boolean"
                if cell_type == "e":
                    return text, "error"
                if cell_type == "str":
                    return text or "", "string"
                if text is None:
                    return None, "blank"

                # parse number
                if "." not in text and "e" not in text.lower():
                    return int(text), "number"
                return float(text), "number"

            for cell in sheet_root.iter(qualified(MAIN_NS, "c")):
                address = cell.attrib["r"]
                value, value_type = decode_value(cell, strings)
                formula_node = cell.find(qualified(MAIN_NS, "f"))
                formula = f"={formula_node.text or ''}" if formula_node is not None else None
                style_index = int(cell.attrib.get("s", "0"))
                yield {
                    "record_type": "cell",
                    "sheet_index": sheet_index,
                    "sheet_name": sheet_name,
                    "address": address,
                    "row": int("".join(character for character in address if character.isdigit())),
                    "column": column_number(address),
                    "value_type": value_type,
                    "value": value,
                    "formula": formula,
                    "number_format": formats[style_index],
                }


def main():
    args = build_parser().parse_args()
    with args.output_ndjson.open("w", encoding="utf-8", newline="\n") as output_file:
        writer = ndjson.writer(output_file, ensure_ascii=False, separators=(",", ":"))
        for record in workbook_records(args.input_xlsx):
            writer.writerow(record)


if __name__ == "__main__":
    main()
