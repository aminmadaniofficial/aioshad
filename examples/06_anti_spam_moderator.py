"""
06_anti_spam_moderator.py: Group moderation & anti-link filter.
"""
import asyncio
import re
from aioshad import Client, F
from aioshad.filters import IsGroup
from aioshad.types import Message

client = Client(session="moderator_account")

LINK_REGEX = re.compile(r"(https?://\S+|shad\.ir/\S+|rubika\.ir/\S+)", re.IGNORECASE)


@client.on_message(IsGroup())
async def anti_link_checker(msg: Message):
    if not msg.text:
        return

    # Check if message contains links
    if LINK_REGEX.search(msg.text):
        try:
            # Delete the link message globally
            await msg.delete(delete_type="Global")
            print(f"Deleted link from user {msg.author_guid} in {msg.chat_guid}")
        except Exception as exc:
            print(f"Failed to delete message: {exc}")


if __name__ == "__main__":
    client.run()
