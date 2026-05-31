"""
Local persistence layer for bookmarks.

Bookmarks are stored as a JSON file in the project root. This module
handles all reading and writing — the rest of the app should only interact
with bookmarks through load_bookmarks() and save_bookmarks().
"""

import json
import os

# The file lives next to this module, in the project root.
BOOKMARKS_FILE = "bookmarks.json"


def load_bookmarks() -> list:
    """
    Read bookmarks from disk and return them as a list of dicts.
    Returns an empty list if the file doesn't exist or is corrupted —
    we prefer 'start fresh' over crashing.
    """
    if not os.path.exists(BOOKMARKS_FILE):
        return []

    try:
        with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        return data
    except (json.JSONDecodeError, OSError):
        return []


def save_bookmarks(bookmarks: list) -> bool:
    """
    Write the bookmarks list to disk as JSON.
    Returns True on success, False on failure.
    """
    try:
        with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False