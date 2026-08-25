"""Plan deterministic summarize-sheet artifact names without parsing workbook data."""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def build_parser():
    parser = argparse.ArgumentParser(
        description="Emit a deterministic JSON output plan for one XLSX workbook."
    )
    parser.add_argument("input_path", type=Path, help="Source XLSX workbook")
    parser.add_argument("--date", required=True, help="Reporting date")
    parser.add_argument(
        "--date-format",
        required=True,
        help="datetime.strptime format for --date, such as %%Y-%%m-%%d",
    )
    parser.add_argument("--sheet", help="Exact worksheet title; omit for the first sheet")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("data/processed/tables"),
        help="Artifact directory (default: data/processed/tables)",
    )
    return parser


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def output_info(path):
    exists = path.is_file()
    return {
        "exists": exists,
        "filename": path.name,
        "path": str(path),
        "sha256": sha256_file(path) if exists else None,
        "size_bytes": path.stat().st_size if exists else None,
    }


def make_plan(args):
    source = args.input_path.resolve(strict=True)
    output_root = args.output_root.resolve()
    report_date = datetime.strptime(args.date, args.date_format).date().isoformat()
    source_sha256 = sha256_file(source)
    source_slug = slugify(source.stem)
    sheet_slug = f"--sheet-{slugify(args.sheet)}" if args.sheet else ""
    artifact_id = (
        f"{report_date}--{source_slug}{sheet_slug}--sha256-{source_sha256[:16]}"
    )
    title = f"{source.stem} ({report_date})"
    if args.sheet:
        title = f"{title} [{args.sheet}]"

    output_paths = {
        "summary_markdown": output_root / f"{artifact_id}--summary.md",
        "model_context": output_root / f"{artifact_id}--model-context.txt",
        "sheet_ndjson": output_root / f"{artifact_id}--sheet.ndjson",
    }
    outputs = {role: output_info(path) for role, path in output_paths.items()}

    return {
        "artifact_id": artifact_id,
        "complete": all(item["exists"] for item in outputs.values()),
        "output_root": str(output_root),
        "outputs": outputs,
        "reporting_date": {
            "input": args.date,
            "input_format": args.date_format,
            "iso": report_date,
        },
        "schema": "summarize-sheet.output-plan",
        "schema_version": 1,
        "selection": {
            "mode": "named" if args.sheet else "first",
            "sheet": args.sheet,
        },
        "source": {
            "filename": source.name,
            "modified_utc": datetime.fromtimestamp(
                source.stat().st_mtime, timezone.utc
            ).isoformat(),
            "path": str(source),
            "sha256": source_sha256,
            "size_bytes": source.stat().st_size,
            "stem": source.stem,
        },
        "title": title,
    }


def main():
    args = build_parser().parse_args()
    print(json.dumps(make_plan(args), indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
