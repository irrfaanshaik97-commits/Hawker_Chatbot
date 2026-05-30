"""
Streamlit web interface for the Singapore Hawker Food Recommendation Chatbot.

This file is the application entry point. Run it with:
    streamlit run app.py

It is intentionally thin — all OpenAI logic lives in openai_service.py.
This file only handles user interface and session state.
"""

import streamlit as st

from openai_service import create_chat_session, send_message


# -----------------------------------------------------------------------------
# Page configuration — must be the FIRST Streamlit command in the script.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="MakanBot - Hawker Food Recommender",
    page_icon="🍜",
    layout="centered",
)


# -----------------------------------------------------------------------------
# Header — what the user sees at the top of the page.
# -----------------------------------------------------------------------------
st.title("🍜 MakanBot")
st.caption(
    "Your friendly Singapore hawker food guide. "
    "Tell me what you're craving, where you are, and any dietary needs."
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
# Streamlit re-runs this entire script on every user interaction. To keep
# data alive between reruns, we store it in st.session_state.

# Initialize the OpenAI message history once per session.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = create_chat_session()

# Initialize the visible message list (user + assistant only).
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []


# -----------------------------------------------------------------------------
# Render Past Messages
# -----------------------------------------------------------------------------
for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------------------------------------------------
# Chat Input — pinned at the bottom of the page.
# -----------------------------------------------------------------------------
user_input = st.chat_input("What are you craving today?")

if user_input:
    # 1. Show the user's message immediately.
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Save it for future reruns.
    st.session_state.display_messages.append(
        {"role": "user", "content": user_input}
    )

    # 3. Send to OpenAI with a loading spinner.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = send_message(st.session_state.chat_history, user_input)

        # 4. Show the reply, or a friendly error message.
        if result["success"]:
            st.markdown(result["text"])
            st.session_state.display_messages.append(
                {"role": "assistant", "content": result["text"]}
            )
        else:
            st.error(result["error"])