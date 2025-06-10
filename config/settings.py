import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4"

# Storage Configuration
STORAGE_DIR = "storage"
USER_DATA_FILE = f"{STORAGE_DIR}/user_data.json"

# App Configuration
APP_TITLE = "Health Coach V2"
