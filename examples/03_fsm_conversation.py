"""
03_fsm_conversation.py: Interactive multi-step conversations using Conversation context manager.
"""
import asyncio
from aioshad import Client, F
from aioshad.filters import Command
from aioshad.types import Message

client = Client(session="my_account")


@client.on_message(Command("survey", prefix="!."))
async def start_survey(msg: Message):
    chat_guid = msg.chat_guid

    # Start a direct interactive conversation with the chat
    async with client.conversation(chat_guid, timeout=60.0) as conv:
        await conv.send_message("سلام! لطفاً نام خود را وارد کنید:")
        name_msg = await conv.get_response()
        user_name = name_msg.text.strip()

        await conv.send_message(f"خوشبختم {user_name}! حالا بگو چند سالته؟")
        age_msg = await conv.get_response()
        user_age = age_msg.text.strip()

        await conv.send_message(
            f"✅ **اطلاعات ثبت شد:**\\n"
            f"• نام: {user_name}\\n"
            f"• سن: {user_age}"
        )


if __name__ == "__main__":
    client.run()
