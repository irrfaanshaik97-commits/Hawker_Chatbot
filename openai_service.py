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