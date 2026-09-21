"""
01_quickstart.py: Simple Echo Selfbot for Shad Messenger using aioshad.
"""
import asyncio
from aioshad import Client, F
from aioshad.filters import IsMe
from aioshad.types import Message

# Initialize client with session name (e.g. my_account saved by `aioshad login -s my_account`)
client = Client(session="my_account")


# Reply to any text message starting with "echo "
@client.on_message(F.text.startswith("echo "))
async def echo_handler(msg: Message):
    text_to_repeat = msg.text[5:].strip()
    await msg.reply(f"Echo: {text_to_repeat}")


# Self command: only trigger if YOU sent the message
@client.on_message(IsMe(), F.text == "!ping")
async def ping_handler(msg: Message):
    await msg.edit("Pong from aioshad selfbot!")


if __name__ == "__main__":
    # Start the client (prompts for phone number/OTP on first run)
    client.run()
