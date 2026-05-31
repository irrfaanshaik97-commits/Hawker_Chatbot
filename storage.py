"""
Local persistence layer for saved chat sessions.

Saved sessions are stored as a JSON file in the project root. This module
handles all reading and writing — the rest of the app should only interact
with saved sessions through load_sessions() and save_sessions().
"""

import json
import os

# The file lives next to this module, in the project root.
# Using a constant makes it easy to find and change if needed.
SAVED_SESSIONS_FILE = "saved_sessions.json"


def load_sessions() -> list:
    """
    Read the saved sessions from disk and return them as a list.
    Returns an empty list if the file doesn't exist or is corrupted —
    we prefer 'start fresh' over crashing.
    """
    # If the file has never been created, that's fine — return an empty list.
    if not os.path.exists(SAVED_SESSIONS_FILE):
        return []

    try:
        with open(SAVED_SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Defensive: make sure the file actually contains a list.
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        # Corrupted file or unreadable for any reason — treat as empty.
        # We deliberately don't crash; the user can keep using the app.
        return []


def save_sessions(sessions: list) -> bool:
    """
    Write the sessions list to disk as JSON.
    Returns True on success, False if writing failed — the caller can
    decide whether to warn the user.
    """
    try:
        with open(SAVED_SESSIONS_FILE, "w", encoding="utf-8") as f:
            # indent=2 makes the file human-readable, helpful for debugging.
            json.dump(sessions, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        # Disk full, permission denied, etc. — don't crash the app.
        return False