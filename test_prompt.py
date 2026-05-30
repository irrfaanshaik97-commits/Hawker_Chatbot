"""
Manual test for the hawker chatbot system prompt.
Run this to see how the bot responds to various inputs.
Delete before final submission.
"""

from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL, validate_config
from prompts import HAWKER_CHATBOT_SYSTEM_PROMPT

# Make sure config is valid before doing anything else.
validate_config()

# Create the Gemini client using our API key.
client = genai.Client(api_key=GEMINI_API_KEY)


def ask_bot(user_message: str) -> str:
    """Send one message to Gemini with the system prompt and return the reply."""
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        # The system_instruction parameter is where the system prompt goes.
        # It is separate from the user's message.
        config=types.GenerateContentConfig(
            system_instruction=HAWKER_CHATBOT_SYSTEM_PROMPT
        ),
        contents=user_message,
    )
    return response.text


# A list of test scenarios to evaluate the prompt's quality.
test_inputs = [
    "I'm hungry.",                                          # Vague — should ask 1 question
    "I want something spicy near Bugis MRT.",               # Specific — should recommend
    "I'm vegetarian and craving noodles.",                  # Dietary + craving
    "What's the weather today?",                            # Out of scope — should redirect
    "Recommend me 10 dishes.",                              # Should still cap at 3
]

# Run each test and print the response with a separator.
for i, user_input in enumerate(test_inputs, 1):
    print(f"\n{'=' * 60}")
    print(f"TEST {i} — User: {user_input}")
    print(f"{'=' * 60}")
    print(ask_bot(user_input))