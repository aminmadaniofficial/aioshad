"""
04_send_media.py: Uploading and sending photos, files, and voice notes in aioshad.
"""
import asyncio
from aioshad import Client, F
from aioshad.filters import Command, IsPhoto
from aioshad.types import Message

client = Client(session="my_shad_account")


@client.on_message(Command("photo", prefix="!."))
async def send_photo_demo(msg: Message):
    await msg.reply("در حال ارسال عکس نمونه...")
    # Supports file path, bytes, or Path object
    await client.send_photo(
        object_guid=msg.chat_guid,
        photo="sample.jpg",
        caption="📸 ارسال شده توسط aioshad selfbot",
        reply_to_message_id=msg.id,
    )


@client.on_message(Command("doc", prefix="!."))
async def send_document_demo(msg: Message):
    await msg.reply("در حال ارسال فایل...")
    await client.send_file(
        object_guid=msg.chat_guid,
        file="document.pdf",
        file_name="گزارش_پروژه.pdf",
        caption="📄 فایل ضمیمه شده",
        reply_to_message_id=msg.id,
    )


# Automatically download any received photo
@client.on_message(IsPhoto())
async def download_incoming_photo(msg: Message):
    if msg.file_inline:
        file_bytes = await client.download_file(msg.file_inline)
        print(f"Downloaded photo with size: {len(file_bytes)} bytes")


if __name__ == "__main__":
    client.run()
