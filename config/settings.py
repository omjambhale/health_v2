import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# API Configuration - simplified for Streamlit Cloud
def get_openai_api_key():
    try:
        import streamlit as st
        # Check if we're in Streamlit Cloud environment
        if hasattr(st, 'secrets'):
            return st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
        else:
            return os.getenv("OPENAI_API_KEY")
    except:
        return os.getenv("OPENAI_API_KEY")

OPENAI_API_KEY = get_openai_api_key()
OPENAI_MODEL = "gpt-4"

# Storage Configuration
STORAGE_DIR = "storage"
USER_DATA_FILE = f"{STORAGE_DIR}/user_data.json"

# App Configuration
APP_TITLE = "Health Coach V2"
