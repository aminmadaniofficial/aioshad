# 🚀 aioshad-py

[![CI Test Suite](https://github.com/aminmadaniofficial/aioshad/actions/workflows/ci.yml/badge.svg)](https://github.com/aminmadaniofficial/aioshad/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/aioshad-py.svg?color=blue)](https://pypi.org/project/aioshad-py/)
[![Documentation](https://img.shields.io/badge/docs-website-blue?style=flat&logo=github)](https://aminmadaniofficial.github.io/aioshad/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **A modern, blazingly fast, fully asynchronous Python framework & self-bot library for Shad Messenger (شاد), built on HTTP/2 and AsyncIO.**
>
> 📖 **Interactive Documentation & Showcase:** [https://aminmadaniofficial.github.io/aioshad/](https://aminmadaniofficial.github.io/aioshad/)

---

## 🌟 Key Features

- ⚡ **Fully Asynchronous & HTTP/2 Driven:** Maximizes throughput and minimizes latency with multiplexed HTTP/2 persistent connections.
- 🔐 **Native Cryptographic Engine:** Robust implementation of Shad's protocol security—AES-256-CBC with PKCS7 padding, RSA-1024 keypair generation, OAEP SHA1 decryption, and payload signing.
- 🔄 **Multi-Host Failover & Gateway Pooling:** Dynamic health checks and automatic switching across official Shad edge gateways (`*.iranlms.ir`).
- 🎯 **Aiogram & Pyrogram Inspired Architecture:**
  - Intuitive `@client.on_message` decorators for rapid prototyping.
  - Hierarchical `Dispatcher` and `Router` system for enterprise-grade, modular applications.
  - Expressive `F` (MagicFilter) conditions for filtering updates cleanly.
- 🧠 **Finite State Machine (FSM):** Multi-step user dialog management with in-memory (`MemoryStorage`) or persistent SQLite (`SQLiteStorage`) backends.
- 💬 **Interactive Conversations:** Built-in `async with client.conversation(...)` context manager for linear question-and-answer workflows.
- 🎙️ **WebRTC Voice Chat Engine:** Create, join, leave, mute/unmute, and monitor participants in group or channel voice chats.
- 📸 **High-Performance Media Handling:** Upload and download images, animated GIFs, videos, audio, voice notes, and arbitrary files with automatic thumbnail generation.
- 👥 **Multi-Account Orchestration (`ClientManager`):** Run dozens of bot or self-bot sessions concurrently on a single asyncio event loop.
- 🛠️ **Developer-First CLI:** Authenticate accounts, scaffold production-ready project directories, and inspect session metadata directly from your terminal.

---

## 📦 Installation

Install `aioshad-py` via `pip`:

```bash
pip install aioshad-py
```

Or using `uv`:

```bash
uv add aioshad-py
```

---

## ⚡ Quickstart

Here is a complete, working example creating a simple self-bot with an echo response and a `!ping` command:

```python
import asyncio
from aioshad import Client, F
from aioshad.filters import IsMe
from aioshad.types import Message

# Initialize client with a persistent session name
client = Client(session="my_account")

# Echo any incoming text message starting with "echo "
@client.on_message(F.text.startswith("echo "))
async def echo_handler(msg: Message):
    content = msg.text[5:].strip()
    await msg.reply(f"📣 {content}")

# Respond to "!ping" command sent by your own account
@client.on_message(IsMe(), F.text == "!ping")
async def ping_handler(msg: Message):
    await msg.edit("🏓 Pong! aioshad is running smoothly.")

if __name__ == "__main__":
    # Automatically manages event loop and long-polling updates
    client.run()
```

> **Note:** On the first execution, you will be prompted in the terminal to enter your phone number and OTP code. An authenticated session file (`my_account.session`) will be safely stored locally. Future runs will log in automatically without user interaction.

---

## 🧩 Routers and Modular Handlers

For larger applications, structure your handlers across routers and handle commands with parsed arguments:

```python
import asyncio
from aioshad import Client, Dispatcher, Router
from aioshad.filters import Command, CommandObject, IsGroup
from aioshad.types import Message

router = Router(name="main_router")

@router.message(Command("start", "help", prefix="/!."))
async def handle_start(msg: Message, command: CommandObject):
    await msg.reply(
        f"👋 Hello!\n"
        f"Command: `{command.prefix}{command.command}`\n"
        f"Arguments: `{command.args or 'None'}`"
    )

@router.message(IsGroup(), Command("info", prefix="!"))
async def handle_group_info(msg: Message):
    chat = await msg.get_chat()
    await msg.reply(f"Group: {chat.title}\nMembers: {chat.members_count}")

async def main():
    dp = Dispatcher()
    dp.include_router(router)
    client = Client(session="my_account", dispatcher=dp)
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💬 Linear Conversations

Simplify interactive surveys or step-by-step registration forms using the `conversation` context manager:

```python
@client.on_message(Command("survey", prefix="!"))
async def survey_handler(msg: Message):
    async with client.conversation(msg.chat_guid, timeout=60) as conv:
        await conv.send_message("What is your name?")
        name_msg = await conv.get_response()

        await conv.send_message(f"Nice to meet you, {name_msg.text}! How old are you?")
        age_msg = await conv.get_response()

        await conv.send_message(
            f"✅ Survey complete!\n"
            f"Name: {name_msg.text}\n"
            f"Age: {age_msg.text}"
        )
```

---

## 📸 Media Uploads & Downloads

Send photos, documents, and voice messages effortlessly:

```python
# Send a photo with an optional caption
await client.send_photo(chat_guid, "photo.jpg", caption="Beautiful landscape")

# Send a document or file
await client.send_file(chat_guid, "report.pdf", file_name="Q3_Report.pdf", caption="Quarterly Report")

# Send a voice note
await client.send_voice(chat_guid, "voice_note.ogg")

# Download a file from an incoming message
if msg.file_inline:
    downloaded_path = await client.download_file(
        msg.file_inline,
        destination="downloaded_file.jpg"
    )
```

---

## 🛠️ Command Line Interface (CLI)

`aioshad-py` includes an official CLI tool for bootstrapping and managing sessions:

```bash
# Scaffold a new production-ready project structure
aioshad init my_bot_project

# Authenticate an account and save its session file
aioshad login -s my_account

# Inspect an existing session file (GUID, connection host, auth status)
aioshad session-info my_account.session
```

---

## 👥 Multi-Account Management (`ClientManager`)

Run multiple accounts concurrently within a single process:

```python
from aioshad import Dispatcher, F
from aioshad.client.manager import ClientManager
from aioshad.types import Message

dp = Dispatcher()

@dp.message(F.text == "!status")
async def check_status(msg: Message, client):
    await msg.reply(f"Account active! GUID: {client.me}")

def main():
    manager = ClientManager(dispatcher=dp)
    manager.add_client(session="acc_primary", phone_number="09121111111")
    manager.add_client(session="acc_secondary", phone_number="09122222222")
    manager.run_all()

if __name__ == "__main__":
    main()
```

---

## 🔒 Security & Privacy Notice

- **Session Files:** Never share or commit your `.session` files. They contain your account's decrypted authentication tokens and private keys.
- **Git Ignore:** Keep `*.session` in your `.gitignore` to prevent leaking credentials to public repositories.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
Copyright (c) 2026 Mohammadamin Madani.
