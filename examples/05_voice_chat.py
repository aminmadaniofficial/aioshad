"""
05_voice_chat.py: Managing Shad WebRTC group voice chats.
"""
import asyncio
from aioshad import Client
from aioshad.filters import Command, IsMe
from aioshad.types import Message

client = Client(session="my_shad_account")


@client.on_message(IsMe(), Command("startvc", prefix="!."))
async def start_vc(msg: Message):
    chat_guid = msg.chat_guid
    await msg.edit("در حال راه‌اندازی ویس چت گروه...")
    res = await client.create_voice_chat(chat_guid)
    await msg.edit("🎙️ ویس چت با موفقیت ایجاد شد!")


@client.on_message(IsMe(), Command("stopvc", prefix="!."))
async def stop_vc(msg: Message):
    chat_guid = msg.chat_guid
    await msg.edit("در حال بستن ویس چت...")
    await client.discard_voice_chat(chat_guid)
    await msg.edit("🛑 ویس چت بسته شد.")


@client.on_message(IsMe(), Command("speaking", prefix="!."))
async def set_speaking(msg: Message):
    chat = await msg.get_chat()
    if chat.voice_chat_id:
        await client.set_voice_chat_state(
            chat_guid=msg.chat_guid,
            voice_chat_id=chat.voice_chat_id,
            activity="Speaking",
        )
        await msg.reply("حالت صحبت کردن فعال شد.")


if __name__ == "__main__":
    client.run()
