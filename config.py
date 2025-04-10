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

# Instagram account credentials
PARTICIPANT_IG_USERNAME = os.getenv("PARTICIPANT_IG_USERNAME")
PARTICIPANT_IG_PASSWORD = os.getenv("PARTICIPANT_IG_PASSWORD")
AUNT_IG_USERNAME = os.getenv("AUNT_IG_USERNAME")
AUNT_IG_PASSWORD = os.getenv("AUNT_IG_PASSWORD")
# TODO: add the following once the accounts are set up
# CLOSE_FRIEND_IG_USERNAME = os.getenv("CLOSE_FRIEND_IG_USERNAME")
# CLOSE_FRIEND_IG_PASSWORD = os.getenv("CLOSE_FRIEND_IG_PASSWORD")
# HEALTHY_EATING_COACH_IG_USERNAME = os.getenv("HEALTHY_EATING_COACH_IG_USERNAME")
# HEALTHY_EATING_COACH_IG_PASSWORD = os.getenv("HEALTHY_EATING_COACH_IG_PASSWORD")
# FOOD_CONNOISSEUR_IG_USERNAME = os.getenv("FOOD_CONNOISSEUR_IG_USERNAME")
# FOOD_CONNOISSEUR_IG_PASSWORD = os.getenv("FOOD_CONNOISSEUR_IG_PASSWORD")
# FAN_IG_USERNAME = os.getenv("FAN_IG_USERNAME")
# FAN_IG_PASSWORD = os.getenv("FAN_IG_PASSWORD")
# CURIOUS_CASUAL_VISITOR_IG_USERNAME = os.getenv("CURIOUS_CASUAL_VISITOR_IG_USERNAME")
# CURIOUS_CASUAL_VISITOR_IG_PASSWORD = os.getenv("CURIOUS_CASUAL_VISITOR_IG_PASSWORD")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Google Cloud
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCP_CREDENTIALS_PATH = os.getenv("GCP_CREDENTIALS_PATH")

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
        "PARTICIPANT_FB_PAGE_NAME",
        "PARTICIPANT_IG_USERNAME",
        "PARTICIPANT_IG_PASSWORD",
        "AUNT_IG_USERNAME",
        "AUNT_IG_PASSWORD",
        # "FRIEND_IG_USERNAME",
        # "FRIEND_IG_PASSWORD",
        # "COACH_IG_USERNAME",
        # "COACH_IG_PASSWORD",
        # "CONNOISSEUR_IG_USERNAME",
        # "CONNOISSEUR_IG_PASSWORD",
        # "FAN_IG_USERNAME",
        # "FAN_IG_PASSWORD",
        # "VISITOR_IG_USERNAME",
        # "VISITOR_IG_PASSWORD",
        "GCS_BUCKET_NAME",
        "GCP_CREDENTIALS_PATH",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Validate configuration on import
validate_config()
