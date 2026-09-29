import argparse

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from spreadsheet_data_agent.config import DOCUMENTS_DATA_PATH
from spreadsheet_data_agent.helpers import document_files
from spreadsheet_data_agent.tasks.create_product_usage_timeline import ProductUsageTimeline
from spreadsheet_data_agent.tasks.create_product_usage_timeline import (
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
    return document_files.to_models(document_files.list_workbook_files(path))

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
    workbook = document_files.load_workbook_file(file_path)  # pyright: ignore[reportArgumentType]
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
