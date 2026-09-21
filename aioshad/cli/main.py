from __future__ import annotations

import argparse
import asyncio
import os
import pathlib
import sys
from colorama import Fore, Style, init

from aioshad import __version__
from aioshad.session import FileSessionStorage, Session

init(autoreset=True)

BOT_PY_TEMPLATE = """import asyncio
from aioshad import Client, Dispatcher, F
from aioshad.filters import Command
from aioshad.types import Message
from config import SESSION_NAME, ADMIN_GUIDS
from handlers import common_router
from middlewares import LoggingMiddleware

async def main():
    dp = Dispatcher()
    dp.middleware(LoggingMiddleware())
    dp.include_router(common_router)

    # Initialize Shad client
    client = Client(session=SESSION_NAME, dispatcher=dp)
    
    print("[+] Starting aioshad Selfbot...")
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())
"""

CONFIG_PY_TEMPLATE = """# aioshad Selfbot Configuration
SESSION_NAME = "my_account"
ADMIN_GUIDS = []  # Add authorized GUIDs here
PROXY = None  # Optional proxy URL if needed
"""

HANDLERS_INIT_TEMPLATE = """from .common import router as common_router

__all__ = ("common_router",)
"""

HANDLERS_COMMON_TEMPLATE = """from aioshad import Router, F
from aioshad.filters import Command, CommandObject, IsMe
from aioshad.types import Message

router = Router(name="common")

@router.message(Command("ping", prefix="!."))
async def cmd_ping(msg: Message):
    await msg.reply("Pong! aioshad is active.")

@router.message(Command("info", prefix="!."))
async def cmd_info(msg: Message):
    chat = await msg.get_chat()
    await msg.reply(
        f"**اطلاعات چت:**\\n"
        f"• عنوان: {chat.title}\\n"
        f"• شناسه چت: `{chat.guid}`\\n"
        f"• شناسه فرستنده: `{msg.author_guid}`"
    )
"""

MIDDLEWARES_INIT_TEMPLATE = """from .logging import LoggingMiddleware

__all__ = ("LoggingMiddleware",)
"""

MIDDLEWARES_LOGGING_TEMPLATE = """from aioshad import BaseMiddleware
from typing import Any, Callable, Dict, Awaitable

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        # Simple logging before and after event handling
        return await handler(event, data)
"""

REQUIREMENTS_TEMPLATE = """aioshad-py>=0.1.0
"""


def cmd_startproject(name: str) -> None:
    target_dir = pathlib.Path(name).resolve()
    if target_dir.exists():
        print(Fore.RED + f"[!] Directory '{name}' already exists!")
        return

    print(Fore.CYAN + f"[*] Generating aioshad Selfbot project in '{name}'...")

    (target_dir / "handlers").mkdir(parents=True, exist_ok=True)
    (target_dir / "middlewares").mkdir(parents=True, exist_ok=True)

    files = {
        target_dir / "main.py": BOT_PY_TEMPLATE,
        target_dir / "config.py": CONFIG_PY_TEMPLATE,
        target_dir / "requirements.txt": REQUIREMENTS_TEMPLATE,
        target_dir / "handlers" / "__init__.py": HANDLERS_INIT_TEMPLATE,
        target_dir / "handlers" / "common.py": HANDLERS_COMMON_TEMPLATE,
        target_dir / "middlewares" / "__init__.py": MIDDLEWARES_INIT_TEMPLATE,
        target_dir / "middlewares" / "logging.py": MIDDLEWARES_LOGGING_TEMPLATE,
    }

    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    print(Fore.GREEN + f"[+] Project created successfully at {target_dir}")
    print(Fore.YELLOW + f"Next steps:\\n  cd {name}\\n  aioshad login\\n  python main.py")


async def _async_login(session_name: str, phone: Optional[str] = None, proxy: Optional[str] = None) -> None:
    from aioshad.client.client import Client

    client = Client(session=session_name, phone_number=phone, proxy=proxy)
    await client.connect()
    print(Fore.GREEN + f"[+] Successfully logged in! Session saved to '{session_name}.session'")
    if client.session.user_guid:
        print(Fore.CYAN + f"User GUID: {client.session.user_guid}")
    print(Fore.MAGENTA + f"String session: {client.session.export_string()}")
    await client.stop()


def cmd_login(session_name: str, phone: Optional[str] = None, proxy: Optional[str] = None) -> None:
    asyncio.run(_async_login(session_name, phone, proxy))


def cmd_session_info(session_file: str) -> None:
    path = pathlib.Path(session_file)
    if not path.exists():
        print(Fore.RED + f"[!] Session file '{session_file}' not found.")
        return

    storage = FileSessionStorage(session_file)
    session = storage.load(session_file)
    print(Fore.CYAN + f"=== Session Info: {session_file} ===")
    print(f"Phone: {session.phone_number or 'N/A'}")
    print(f"User GUID: {session.user_guid or 'N/A'}")
    print(f"Host: {session.messenger_host}")
    print(f"Has Auth: {'Yes' if session.has_auth() else 'No'}")
    print(f"Last State: {session.state}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aioshad",
        description="CLI tool for aioshad Python framework & selfbot library for Shad Messenger.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    init_parser = subparsers.add_parser("init", help="Create a new aioshad project")
    init_parser.add_argument("name", nargs="?", default="my_shad_bot", help="Project name / directory")

    # login
    login_parser = subparsers.add_parser("login", help="Log in and create a .session file")
    login_parser.add_argument("-s", "--session", default="my_account", help="Session file name")
    login_parser.add_argument("-p", "--phone", default=None, help="Phone number with country code")
    login_parser.add_argument("--proxy", default=None, help="HTTP/SOCKS5 Proxy URL")

    # session-info
    info_parser = subparsers.add_parser("session-info", help="Inspect session credentials")
    info_parser.add_argument("file", help="Path to .session file")

    args = parser.parse_args()

    if args.command == "init":
        cmd_startproject(args.name)
    elif args.command == "login":
        cmd_login(args.session, args.phone, args.proxy)
    elif args.command == "session-info":
        cmd_session_info(args.file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
