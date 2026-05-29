"""
Quick connectivity test for the Gemini API.
Run this once to verify your API key works.
Delete this file before final submission.
"""

from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL, validate_config

# Fail fast and clearly if the API key isn't configured.
validate_config()

# Create a client that authenticates with our API key.
client = genai.Client(api_key=GEMINI_API_KEY)

# Send a single test message to Gemini.
print("Sending test message to Gemini...")
response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents="Say hello in one short sentence."
)

# Print whatever Gemini said back.
print("\nGemini replied:")
print(response.text)