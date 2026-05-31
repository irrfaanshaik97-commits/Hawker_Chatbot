"""
Streamlit web interface for the Singapore Hawker Food Recommendation Chatbot.

Run with:
    streamlit run app.py

This file handles UI and session state only. All OpenAI logic lives in
openai_service.py. All persistence lives in storage.py.
"""

import streamlit as st

from openai_service import (
    create_chat_session,
    send_message,
    generate_tagline,
    parse_dish_blocks,
)
from storage import load_bookmarks, save_bookmarks


# -----------------------------------------------------------------------------
# Page configuration — must be the FIRST Streamlit command.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MakanBot - Hawker Food Recommender",
    page_icon="🍜",
    layout="centered",
)


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def initialize_session_state():
    """Set up session state on first run (or after a reset)."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = create_chat_session()
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "bookmarks" not in st.session_state:
        st.session_state.bookmarks = load_bookmarks()


def reset_conversation():
    """Wipe the live conversation. Does not touch bookmarks."""
    st.session_state.chat_history = create_chat_session()
    st.session_state.display_messages = []


def find_preceding_user_message(messages: list, assistant_index: int) -> str:
    """Find the most recent user message before the given assistant index."""
    for i in range(assistant_index - 1, -1, -1):
        if messages[i]["role"] == "user":
            return messages[i]["content"]
    return ""


def add_bookmark(dish_name: str, dish_block: str, user_message: str):
    """Create a bookmark from a dish, persist it, and notify the user."""
    # Dedup: skip if the same dish was already bookmarked from the same question.
    for b in st.session_state.bookmarks:
        if b["dish_name"] == dish_name and b["original_question"] == user_message:
            st.toast(f"'{dish_name}' is already bookmarked.", icon="ℹ️")
            return

    tagline = generate_tagline(user_message)

    bookmark = {
        "tagline": tagline,
        "dish_name": dish_name,
        "dish_block": dish_block,
        "original_question": user_message,
    }
    st.session_state.bookmarks.append(bookmark)

    if save_bookmarks(st.session_state.bookmarks):
        st.toast(f"Bookmarked '{dish_name}'", icon="🔖")
    else:
        st.toast("Bookmarked, but couldn't save to disk.", icon="⚠️")


def remove_bookmark(index: int):
    """Remove a bookmark by index and persist the change."""
    if 0 <= index < len(st.session_state.bookmarks):
        removed = st.session_state.bookmarks.pop(index)
        save_bookmarks(st.session_state.bookmarks)
        st.toast(f"Removed '{removed['dish_name']}'", icon="🗑️")


def render_assistant_message_with_bookmarks(message: dict, message_index: int):
    """Render an assistant message and bookmark buttons for each dish."""
    with st.chat_message("assistant"):
        st.markdown(message["content"])

        dishes = parse_dish_blocks(message["content"])

        if dishes:
            user_message = find_preceding_user_message(
                st.session_state.display_messages, message_index
            )
            st.caption("Bookmark a recommendation:")

            cols = st.columns(min(len(dishes), 3))
            for i, dish in enumerate(dishes):
                col = cols[i % len(cols)]
                with col:
                    if st.button(
                        f"🔖 {dish['name']}",
                        key=f"bookmark_{message_index}_{i}",
                        use_container_width=True,
                    ):
                        add_bookmark(
                            dish_name=dish["name"],
                            dish_block=dish["block"],
                            user_message=user_message,
                        )
                        st.rerun()


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("🍜 MakanBot")
st.caption(
    "Your friendly Singapore hawker food guide. "
    "Tell me what you're craving, where you are, and any dietary needs."
)


# -----------------------------------------------------------------------------
# Initialize session state.
# -----------------------------------------------------------------------------
initialize_session_state()


# -----------------------------------------------------------------------------
# Sidebar — controls, bookmarks, and about info.
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        reset_conversation()
        st.rerun()

    st.divider()

    # --- Bookmarks ---
    st.header("🔖 Bookmarks")

    if not st.session_state.bookmarks:
        st.caption("Bookmark a dish from the chat to save it here.")
    else:
        for i, bookmark in enumerate(st.session_state.bookmarks):
            with st.expander(f"📍 {bookmark['tagline']}"):
                st.markdown(f"**{bookmark['dish_name']}**")
                st.markdown(bookmark["dish_block"])
                if st.button(
                    "Remove",
                    key=f"remove_bookmark_{i}",
                    use_container_width=True,
                ):
                    remove_bookmark(i)
                    st.rerun()

    st.divider()

    st.markdown(
        "### About\n"
        "**MakanBot** recommends Singapore hawker dishes based on what "
        "you're craving, where you are, and your dietary needs.\n\n"
        "Built for the DigiPen AI Bootcamp Capstone 2026."
    )


# -----------------------------------------------------------------------------
# Main chat area
# -----------------------------------------------------------------------------
if not st.session_state.display_messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hi! I'm **MakanBot**, your Singapore hawker food guide.\n\n"
            "Tell me what you're craving, and I'll point you to a "
            "great hawker dish. You can mention:\n"
            "- 🌶️ A flavor or mood (*spicy, soupy, sweet*)\n"
            "- 📍 An MRT station or area (*Bugis, Tiong Bahru*)\n"
            "- 🥦 Dietary needs (*halal, vegetarian, no pork*)\n\n"
            "**Try one of these to start:**"
        )
        st.markdown(
            "- *I want something spicy near Bugis MRT.*\n"
            "- *Recommend a vegetarian dish in Chinatown.*\n"
            "- *Halal soupy noodles, please.*"
        )
else:
    # Render every past message. Assistant messages get bookmark buttons.
    for idx, message in enumerate(st.session_state.display_messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            render_assistant_message_with_bookmarks(message, idx)


# -----------------------------------------------------------------------------
# Chat input
# -----------------------------------------------------------------------------
user_input = st.chat_input("What are you craving today?")

if user_input:
    cleaned_input = user_input.strip()
    if not cleaned_input:
        st.toast("Please type a message before sending.", icon="✍️")
        st.stop()

    with st.chat_message("user"):
        st.markdown(cleaned_input)

    st.session_state.display_messages.append(
        {"role": "user", "content": cleaned_input}
    )

    with st.chat_message("assistant"):
        with st.spinner("MakanBot is thinking..."):
            result = send_message(
                st.session_state.chat_history, cleaned_input
            )

        if result["success"]:
            st.markdown(result["text"])
            st.session_state.display_messages.append(
                {"role": "assistant", "content": result["text"]}
            )
            # Trigger a rerun so the bookmark buttons appear for this
            # newly-added message via the normal rendering loop above.
            st.rerun()
        else:
            st.error(result["error"])