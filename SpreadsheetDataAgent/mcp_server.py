import argparse

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from SpreadsheetDataAgent.config import DOCUMENTS_DATA_PATH
from SpreadsheetDataAgent.helpers import document_files
from SpreadsheetDataAgent.helpers.workbooks import load_workbook_file
from SpreadsheetDataAgent.tasks.create_product_usage_timeline import ProductUsageTimeline
from SpreadsheetDataAgent.tasks.create_product_usage_timeline import (
    run_task as run_product_usage_timeline_task,
)

mcp = FastMCP(
    name="Spreadsheet Data Agent",
    instructions=(
        "Use list_workbook_files to discover available workbooks, then use "
        "create_product_usage_timeline to create a continuous monthly usage table."
    ),
)


@mcp.tool(
    name="list_workbook_files",
    title="List workbook files",
    description="List supported workbook files under a local directory.",
    output_schema=document_files.WorkbookFiles.model_json_schema(),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def list_workbook_files_tool(
    path: str = str(DOCUMENTS_DATA_PATH),
) -> document_files.WorkbookFiles:
    return document_files.WorkbookFiles(
        files=[
            document_files.WorkbookFile(name=file_path.name, path=str(file_path.resolve())) for file_path in document_files.list_workbook_files(path)
        ]
    )


@mcp.tool(
    name="create_product_usage_timeline",
    title="Create product usage timeline",
    description=(
        "Create a continuous monthly product usage timeline from a workbook, optionally limited to one worksheet."
    ),
    output_schema=ProductUsageTimeline.model_json_schema(),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
def create_product_usage_timeline_tool(
    file: str,
    sheet_name: str | None = None,
    sheet_index: int | None = None,
) -> ProductUsageTimeline:
    file_path = document_files.select_file_from_name(file)
    workbook = load_workbook_file(file_path)  # pyright: ignore[reportArgumentType]
    timeline = run_product_usage_timeline_task(
        workbook,  # pyright: ignore[reportArgumentType]
        sheet_name=sheet_name,
        sheet_index=sheet_index,
    )
    workbook.close()  # pyright: ignore[reportOptionalMemberAccess]
    return ProductUsageTimeline.model_validate(timeline)


def main(transport, host, port, path, *, no_banner, log_level):
    if transport == "stdio":
        mcp.run(
            transport="stdio",
            show_banner=not no_banner,
            log_level=log_level,
        )
        return

    mcp.run(
        transport="http",
        host=host,
        port=port,
        path=path,
        log_level=log_level,
        show_banner=not no_banner,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Spreadsheet Data Agent MCP server.")
    parser.add_argument(
        "--transport",
        choices=("stdio", "http"),
        default="stdio",
        help="MCP transport (default: stdio).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP bind address (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP bind port (default: 8000).",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="HTTP endpoint path (default: /mcp).",
    )
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
        default="INFO",
        help="Server log level (default: INFO).",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Hide the FastMCP startup banner.",
    )
    args = parser.parse_args()
    main(args.transport, args.host, args.port, args.path, args.no_banner, args.log_level)
