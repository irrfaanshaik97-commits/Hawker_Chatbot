"""
Configuration module.
Loads environment variables from .env (locally) or from the host environment
(when deployed to a cloud platform, which injects secrets automatically).
"""

import os
from dotenv import load_dotenv

# Load variables from a local .env file if it exists.
load_dotenv()

# Read the OpenAI API key from the environment.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Read the model name, defaulting to gpt-4o-mini if not set.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def validate_config():
    """Raises a clear error if any required config value is missing."""
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is not set. "
            "Copy .env.example to .env and fill in your OpenAI API key."
        )