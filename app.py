"""
Streamlit web interface for the Singapore Hawker Food Recommendation Chatbot.

Run with:
    streamlit run app.py

This file handles UI and session state only. All OpenAI logic lives in
openai_service.py. All persistence lives in storage.py.
"""

import streamlit as st

from openai_service import create_chat_session, send_message
from storage import load_sessions, save_sessions


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
    if "saved_sessions" not in st.session_state:
        st.session_state.saved_sessions = load_sessions()
    if "viewing_index" not in st.session_state:
        st.session_state.viewing_index = None


def reset_conversation():
    """Wipe the LIVE conversation. Does not touch saved sessions."""
    st.session_state.chat_history = create_chat_session()
    st.session_state.display_messages = []


def truncate(text: str, max_length: int = 50) -> str:
    """Shorten text to max_length chars, adding an ellipsis if cut."""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"


def get_user_questions() -> list[str]:
    """Return only the user messages from the live display history."""
    return [
        m["content"]
        for m in st.session_state.display_messages
        if m["role"] == "user"
    ]


def make_session_label(display_messages: list, max_length: int = 40) -> str:
    """Build a sidebar label from the first user question in a session."""
    for m in display_messages:
        if m["role"] == "user":
            return truncate(m["content"], max_length)
    return "Untitled session"


def archive_current_chat():
    """Archive the live chat into saved sessions, then reset for a new chat."""
    if not st.session_state.display_messages:
        st.toast("Nothing to clear yet.", icon="💬")
        return

    session = {
        "label": make_session_label(st.session_state.display_messages),
        "display_messages": st.session_state.display_messages.copy(),
    }
    st.session_state.saved_sessions.insert(0, session)

    if not save_sessions(st.session_state.saved_sessions):
        st.toast("Could not save the session to disk.", icon="⚠️")

    reset_conversation()


def view_saved_session(index: int):
    """Enter Viewing mode for a saved session."""
    st.session_state.viewing_index = index


def return_to_live():
    """Exit Viewing mode and return to the live chat."""
    st.session_state.viewing_index = None


# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.title("🍜 MakanBot")
st.caption(
    "Your friendly Singapore hawker food guide. "
    "Tell me what you're craving, where you are, and any dietary needs."
)


# -----------------------------------------------------------------------------
# Initialize session state (must run before sidebar reads from it).
# -----------------------------------------------------------------------------
initialize_session_state()


# -----------------------------------------------------------------------------
# Sidebar — controls, history, saved sessions, and about info.
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        archive_current_chat()
        st.rerun()

    st.divider()

    # --- Current session questions ---
    st.header("💬 Your Questions")
    questions = get_user_questions()
    if not questions:
        st.caption("Your questions will appear here as we chat.")
    else:
        for i, question in enumerate(questions, start=1):
            st.markdown(f"**{i}.** {truncate(question)}")

    st.divider()

    # --- Saved sessions ---
    st.header("📚 Saved Sessions")
    if not st.session_state.saved_sessions:
        st.caption("Cleared chats will be saved here.")
    else:
        for i, session in enumerate(st.session_state.saved_sessions):
            if st.button(
                f"📄 {session['label']}",
                key=f"saved_session_{i}",
                use_container_width=True,
            ):
                view_saved_session(i)
                st.rerun()

    st.divider()

    st.markdown(
        "### About\n"
        "**MakanBot** recommends Singapore hawker dishes based on what "
        "you're craving, where you are, and your dietary needs.\n\n"
        "Built for the DigiPen AI Bootcamp Capstone 2026."
    )


# -----------------------------------------------------------------------------
# Main area — Live chat OR archived session, depending on mode.
# -----------------------------------------------------------------------------
if st.session_state.viewing_index is not None:
    # ===== Viewing mode (read-only) =====
    session = st.session_state.saved_sessions[st.session_state.viewing_index]

    st.info(
        f"📖 Viewing a saved session: **{session['label']}** (read-only)"
    )

    if st.button("↩ Back to Live Chat"):
        return_to_live()
        st.rerun()

    for message in session["display_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # No st.chat_input here — input is intentionally disabled in Viewing mode.

else:
    # ===== Live mode =====
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

    # --- Live chat input ---
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
            else:
                st.error(result["error"])