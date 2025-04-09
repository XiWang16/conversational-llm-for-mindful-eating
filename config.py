"""
Configuration Management Module

This module acts as the central hub for managing application configurations. 
It loads environment variables, validates them, and provides default values 
where necessary. This ensures that configuration values are easily accessible 
throughout the codebase.

Key Features:
- Centralizes configuration management for the application.
- Validates required environment variables at startup.
- Provides type-safe access to configuration values.
- Maintains consistent API versions across the application.
- Offers default values for optional configurations.

Usage Example:
    from config import INSTAGRAM_APP_ID, GRAPH_API_VERSION
    
    # Use configuration values directly
    api_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)  # Load .env

# Instagram Graph API credentials
INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v22.0")
INSTAGRAM_REDIRECT_URI = os.getenv("INSTAGRAM_REDIRECT_URI")
PARTICIPANT_FB_PAGE_NAME = os.getenv("PARTICIPANT_FB_PAGE_NAME")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Google Cloud
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

# Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# Hugging Face
HF_TOKEN = os.getenv("HF_TOKEN")

# Base Prompt
with open(os.getenv('BASE_PROMPT_FILE'), 'r') as f:
    BASE_PROMPT = f.read()

# File paths
PERSONA_FILE = "personas.json"
COMMENT_LOG_FILE = "comments.db"

# Constructed values
GRAPH_API_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Validation
def validate_config():
    required_vars = [
        "INSTAGRAM_APP_ID",
        "INSTAGRAM_APP_SECRET",
        "GCS_BUCKET_NAME",
        "GCP_CREDENTIALS_PATH",
        "OPENAI_API_KEY",
        "FLASK_SECRET_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on import
validate_config()
