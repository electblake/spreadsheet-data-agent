from platformdirs import user_documents_path

DATA_PATH = user_documents_path() / "SpreadsheetDataAgent" / "data"
EMBEDDINGS_PATH = DATA_PATH / "interim" / "embeddings"

MODEL_ID = "gpt-5.5"
GPT_MODELS = ["gpt-5.5", "gpt-4o", "gpt-4o-mini"]
EMBEDDING_MODEL = "text-embedding-3-small"

SYSTEM_RULES = [
    "Use only the supplied worksheet evidence; never rely on outside knowledge.",
    "Treat workbook and worksheet names as labels, not evidence of worksheet contents.",
    "Do not invent cell values, assume unseen content, or claim evidence without its supplied cell reference.",
    "Do not explain, suggest, converse, or include supporting text in the response.",
    "Do not transform values, calculate formulas, merge ranges, construct dates, infer years, rename labels, fill blanks, or assume a fixed layout."
]
