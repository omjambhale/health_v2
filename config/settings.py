import os
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# API Configuration - works both locally and on Streamlit Cloud
try:
    import streamlit as st
    # Try to get from Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    else:
        # Fallback to environment variable (for local development)
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
except ImportError:
    # If streamlit is not available, use environment variable
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-4"

# Storage Configuration
STORAGE_DIR = "storage"
USER_DATA_FILE = f"{STORAGE_DIR}/user_data.json"

# App Configuration
APP_TITLE = "Health Coach V2"
