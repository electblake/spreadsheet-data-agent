from loguru import logger
from openai import OpenAI
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from pandas import DataFrame
from spreadsheet_data_agent.config import EMBEDDING_MODEL, MODEL_ID


def sheet_to_df(sheet: Worksheet) -> DataFrame:
    rows = sheet.values
    columns = next(rows)
    return DataFrame(rows, columns=columns)

def calc_embeddings(wb: Workbook) -> list[list[str | list[float]]]:
    workbook_embeddings = []
    for ws in wb:
        sheet_embeddings, embeddings_text = calc_sheet_embeddings(ws)
        workbook_embeddings.append([ws.title, embeddings_text, sheet_embeddings])
    return workbook_embeddings

def calc_sheet_embeddings(sheet: Worksheet):

    client = OpenAI()
    df = sheet_to_df(sheet)
    sheet_title = sheet.title
    embedding_input = (
        f"Worksheet title: {sheet_title}\n"
        f"Worksheet data:\n{df.to_csv(index=False, lineterminator='\n')}"
    )
    logger.debug("Creating sheet embeddings response: {}", sheet_title)
    response = client.embeddings.create(
        input=embedding_input, model=EMBEDDING_MODEL
    )
    logger.debug("Created sheet embeddings response: {}", sheet_title)

    print(response.data[0].embedding)
    return response.data

def num_tokens(text: str, model: str = MODEL_ID) -> int:
    """Return the number of tokens in a string."""
    import tiktoken  # for counting tokens
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
