# 🚀 aioshad Examples

This directory contains practical, production-ready examples showcasing `aioshad` features:

1. **`01_quickstart.py`**: Quickstart echo bot and ping command with the `@client.on_message` decorator.
2. **`02_commands_and_routers.py`**: Modular architecture using `Dispatcher`, `Router`, and command handlers.
3. **`03_fsm_conversation.py`**: Step-by-step interactive questionnaire using the `Conversation` context manager.
4. **`04_send_media.py`**: Uploading and downloading photos, documents, and voice notes.
5. **`05_voice_chat.py`**: Interacting with group and channel WebRTC voice chats.
6. **`06_anti_spam_moderator.py`**: Automated moderation bot that detects and deletes spam/links in groups.
7. **`07_multi_account.py`**: Running multiple accounts concurrently on a single event loop with `ClientManager`.

### How to Run:
```bash
python 01_quickstart.py
```

On first execution, the client prompts for your phone number and OTP code, then securely caches the session in `<session_name>.session`. Subsequent runs connect automatically using the saved credentials.
