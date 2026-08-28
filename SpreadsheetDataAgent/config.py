MODEL_ID = "gpt-5.5"

SYSTEM_RULES = [
    "Use only the supplied worksheet evidence; never rely on outside knowledge.",
    "Treat workbook and worksheet names as labels, not evidence of worksheet contents.",
    "Do not invent cell values, assume unseen content, or claim evidence without its supplied cell reference.",
    "Do not explain, suggest, converse, or include supporting text in the response.",
    "Do not transform values, calculate formulas, merge ranges, construct dates, infer years, rename labels, fill blanks, or assume a fixed layout."
]
# file = r"S:\\Spaces\\AgentSkills\\SpreadsheetDataAgent\\data\\external\\inventory\\Macys Shipping schedule - Aug. 18, 2026.xlsx"
# file = r"S:\\Spaces\\AgentSkills\\SpreadsheetDataAgent\\data\\external\\inventory\\Shipping Schedule Aug. 17 - 2026 - Bloomingdales Garment - internal.xlsx"
# file = r"S:\\Spaces\\AgentSkills\\SpreadsheetDataAgent\\data\\external\\inventory\\Shoppers Open Order Report - August 14 2026.xlsx"
