"""
Streamlit web interface for the Singapore Hawker Food Recommendation Chatbot.

Run with:
    streamlit run app.py

This file handles UI and session state only. All OpenAI logic lives in
openai_service.py.
"""

import streamlit as st

from openai_service import create_chat_session, send_message


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


def reset_conversation():
    """Wipe the conversation and start a fresh chat session."""
    st.session_state.chat_history = create_chat_session()
    st.session_state.display_messages = []


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("🍜 MakanBot")
st.caption(
    "Your friendly Singapore hawker food guide. "
    "Tell me what you're craving, where you are, and any dietary needs."
)


# -----------------------------------------------------------------------------
# Sidebar — controls and project info.
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        reset_conversation()
        st.rerun()

    st.divider()

    st.markdown(
        "### About\n"
        "**MakanBot** recommends Singapore hawker dishes based on what "
        "you're craving, where you are, and your dietary needs.\n\n"
        "Built for the DigiPen AI Bootcamp Capstone 2026."
    )


# -----------------------------------------------------------------------------
# Initialize session state.
# -----------------------------------------------------------------------------
initialize_session_state()


# -----------------------------------------------------------------------------
# Render past messages — or a welcome message if the chat is empty.
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
    for message in st.session_state.display_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# -----------------------------------------------------------------------------
# Chat input — pinned at the bottom.
# -----------------------------------------------------------------------------
user_input = st.chat_input("What are you craving today?")

if user_input:
    # Defensive: strip whitespace and silently ignore empty input.
    cleaned_input = user_input.strip()
    if not cleaned_input:
        st.toast("Please type a message before sending.", icon="✍️")
        st.stop()

    # Show the user's message immediately.
    with st.chat_message("user"):
        st.markdown(cleaned_input)

    st.session_state.display_messages.append(
        {"role": "user", "content": cleaned_input}
    )

    # Send to OpenAI with a spinner for visual feedback.
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
        else:
            st.error(result["error"])