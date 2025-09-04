# config/settings.py
import os
from pathlib import Path

# Project paths
BASE_DIR = Path("/content/Output")
EXCEL_FILE_PATH = "Names.xlsx"
EXCEL_SHEET_NAME = "sheet"

# API Settings
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 4000
OPENAI_TEMPERATURE = 0.7

# Content settings
MAX_TEXT_LENGTH = 20000  # Characters to use from PDF text
