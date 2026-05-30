"""
Manual test for openai_service.py.
Runs a multi-turn conversation in the terminal to verify:
  - The bot maintains memory across turns.
  - The error-handling wrapper returns clean dicts.
Delete before final submission.
"""

from openai_service import create_chat_session, send_message

# Create one chat session (a messages list).
chat_history = create_chat_session()

# A scripted conversation that requires memory to work properly.
conversation = [
    "I'm vegetarian and looking for something near Bugis MRT.",
    "Something soupy please.",
    "Got any other ideas? I'm not in the mood for the first one.",
]

for i, user_input in enumerate(conversation, 1):
    print(f"\n{'=' * 60}")
    print(f"TURN {i} — User: {user_input}")
    print(f"{'=' * 60}")

    result = send_message(chat_history, user_input)

    if result["success"]:
        print(result["text"])
    else:
        print(f"[ERROR] {result['error']}")