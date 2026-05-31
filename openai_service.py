"""
OpenAI Service Layer.
All communication with the OpenAI API lives here. The rest of the app
(app.py) talks to OpenAI ONLY through the functions in this file.

This module is responsible for:
  - Creating chat sessions seeded with the system prompt.
  - Sending user messages and returning responses.
  - Maintaining the conversation history list for multi-turn memory.
  - Catching every kind of API failure and converting it into a clean
    result the UI can display safely.
"""

import openai
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, validate_config
from prompts import HAWKER_CHATBOT_SYSTEM_PROMPT


def create_chat_session() -> list:
    """
    Create a new chat session for the hawker chatbot.

    Unlike Gemini, OpenAI's API is stateless — there is no chat 'object'
    that remembers history. Instead, we maintain conversation memory
    ourselves as a list of message dicts. The list starts with the
    system prompt so every reply is shaped by it.

    Returns:
        A messages list (chat history) ready to be passed to send_message().
    """
    # Validate config first so we fail with a clear error if the API key
    # is missing, rather than crashing somewhere deeper in the SDK.
    validate_config()

    # The conversation history starts with one entry: the system prompt.
    # Every subsequent user/assistant message gets appended to this list.
    messages = [
        {"role": "system", "content": HAWKER_CHATBOT_SYSTEM_PROMPT}
    ]

    return messages


def send_message(messages: list, user_message: str) -> dict:
    """
    Send one user message and return the assistant's reply. Mutates the
    `messages` list in place to add both the user message and the reply,
    enabling multi-turn memory.

    Args:
        messages: The conversation history list from create_chat_session().
        user_message: The user's text input.

    Returns:
        dict with keys:
          - "success" (bool): True if we got a usable reply.
          - "text" (str): The model's reply, if successful.
          - "error" (str): A user-friendly error message, if not.
    """
    # Guard against empty input before we waste an API call.
    if not user_message or not user_message.strip():
        return {
            "success": False,
            "error": "Please type a message before sending.",
        }

    # Add the user's message to the history BEFORE calling the API,
    # because the API needs to see it.
    messages.append({"role": "user", "content": user_message})

    try:
        # Create the OpenAI client. It reads OPENAI_API_KEY from env by
        # default, but we pass it explicitly for clarity.
        client = OpenAI(api_key=OPENAI_API_KEY)

        # The actual API call. We send the ENTIRE history every time —
        # that is how OpenAI maintains multi-turn context.
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
        )

        # Extract the reply text. OpenAI returns a list of 'choices';
        # we only requested one, so we read choices[0].
        reply_text = response.choices[0].message.content

        # Defensive check: even a 200 OK could return empty content
        # (rare, but possible with content filters).
        if not reply_text:
            # Roll back the user message we just appended, so retrying
            # doesn't duplicate it.
            messages.pop()
            return {
                "success": False,
                "error": (
                    "I couldn't generate a response for that. "
                    "Could you rephrase your question?"
                ),
            }

        # Add the assistant's reply to history so future turns remember it.
        messages.append({"role": "assistant", "content": reply_text})

        return {"success": True, "text": reply_text}

    except openai.AuthenticationError:
        # Bad or revoked API key.
        messages.pop()  # Roll back the user message on failure.
        return {
            "success": False,
            "error": (
                "There's a configuration issue with the AI service. "
                "Please contact the developer."
            ),
        }

    except openai.RateLimitError:
        # Too many requests, or out of quota.
        messages.pop()
        return {
            "success": False,
            "error": (
                "I'm getting too many requests right now. "
                "Please wait a moment and try again."
            ),
        }

    except openai.APIConnectionError:
        # Network problem — DNS, timeout, no internet.
        messages.pop()
        return {
            "success": False,
            "error": (
                "I can't reach the AI service right now. "
                "Please check your connection and try again."
            ),
        }

    except openai.APIError:
        # Any other OpenAI-side error (5xx, malformed response, etc).
        messages.pop()
        return {
            "success": False,
            "error": (
                "The AI service is having trouble. "
                "Please try again in a moment."
            ),
        }

    except Exception:
        # Last-resort safety net for anything we didn't anticipate.
        # We deliberately do NOT show the raw exception text — it could
        # leak technical details or look scary to the user.
        messages.pop()
        return {
            "success": False,
            "error": (
                "Something went wrong. Please try again."
            ),
        }
    
    
# =============================================================================
# Bookmark support functions
# =============================================================================

# A focused mini-prompt for generating tag lines. Kept short to minimize cost.
TAGLINE_SYSTEM_PROMPT = (
    "You write very short tag lines summarizing a user's food request. "
    "Output ONLY the tag line — no quotes, no preamble, no full sentences. "
    "Include only key facts: location, flavor/mood, dietary needs. "
    "Maximum 10 words, comma-separated. "
    "Example input: 'I want something spicy near Bedok MRT, not too oily, no pork please.' "
    "Example output: Bedok MRT, spicy, less oily, no pork"
)


def generate_tagline(user_message: str) -> str:
    """
    Use OpenAI to compress the user's last question into a short tag line.
    Falls back to a truncated raw message if the API call fails — we never
    want bookmarking to fail because of a summarization hiccup.
    """
    # Build a fallback up front so any failure path has something to return.
    fallback = user_message.strip()
    if len(fallback) > 60:
        fallback = fallback[:60].rstrip() + "…"

    if not user_message or not user_message.strip():
        return fallback

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": TAGLINE_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            # Keep the summary short and deterministic.
            max_tokens=40,
            temperature=0.3,
        )
        tagline = response.choices[0].message.content
        if tagline:
            return tagline.strip().strip('"').strip("'")
        return fallback
    except Exception:
        # Any failure (network, API, parse) — just use the fallback.
        return fallback


def parse_dish_blocks(response_text: str) -> list[dict]:
    """
    Split a bot response into individual dish blocks.

    Looks for lines starting with '**Dish Name**' (Markdown bold) and
    treats each as the start of a dish block. Each block runs from its
    header until the next header or the end of the text.

    Returns a list of dicts: [{"name": "...", "block": "..."}, ...]
    If no dish headers are found, returns an empty list — the caller can
    handle that case (e.g., offer to bookmark the whole response).
    """
    import re

    if not response_text:
        return []

    # Find each occurrence of '**Something**' that appears at the start
    # of a line (with optional whitespace). Capture both the name and
    # the position so we can slice the original text between matches.
    pattern = re.compile(r"^\s*\*\*([^*\n]+)\*\*", re.MULTILINE)
    matches = list(pattern.finditer(response_text))

    if not matches:
        return []

    dishes = []
    for i, match in enumerate(matches):
        # Block starts at this match, ends at the next match (or EOF).
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(response_text)
        block = response_text[start:end].strip()
        name = match.group(1).strip()
        dishes.append({"name": name, "block": block})

    return dishes