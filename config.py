"""
Configuration module.
Loads environment variables from .env (locally) or from the host environment
(when deployed to Streamlit Cloud, which injects secrets automatically).
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file if it exists.
# In cloud deployments, .env may not exist — that's fine, os.getenv()
# will read from the platform's injected environment variables instead.
load_dotenv()

# Read the Gemini API key from the environment.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Read the model name, defaulting to gemini-2.5-flash if not set.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def validate_config():
    """Raises a clear error if any required config value is missing."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Copy .env.example to .env and fill in your Gemini API key."
        )