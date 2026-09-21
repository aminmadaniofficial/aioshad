# 🚀 aioshad

[![CI Test Suite](https://github.com/aminmadaniofficial/aioshad-py/actions/workflows/ci.yml/badge.svg)](https://github.com/aminmadaniofficial/aioshad-py/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/aioshad-py.svg?color=blue)](https://pypi.org/project/aioshad-py/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **فریم‌ورک و کتابخانه مدرن، بسیار سریع و کاملاً ناهمگام (Async) پایتون برای پیام‌رسان شاد (شاد/Shad Messenger).**

---

## 🌟 ویژگی‌های برجسته (Key Features)

- ⚡ **کاملاً بر پایه AsyncIO و HTTP/2:** عملکرد فوق‌العاده بالا و سبک با استفاده از ارتباطات مالتی‌پکسینگ HTTP/2.
- 🔐 **رمزنگاری اختصاصی شاد:** پیاده‌سازی کامل و امن الگوریتم‌های AES-256-CBC، کلیدهای RSA-1024 با دیکریپشن OAEP SHA1، امضای داده‌ها و کلیدهای موقت (tmp_session).
- 🔄 **پایداری بالا و چرخش سرورها (Multi-Host Failover):** استخر اتصال به هاست‌های شاد (`*.iranlms.ir`) همراه با سوییچ خودکار هنگام قطعی یا افت کیفیت شبکه.
- 🛡️ **پشتیبانی مستقیم از پروکسی:** سازگاری آسان با پروکسی‌های محلی و خارجی (HTTP/HTTPS/SOCKS5) جهت دور زدن اختلالات و تست.
- 🎯 **معماری الهام‌گرفته از Aiogram و Pyrogram:**
  - دکوراتورهای سرراست `@client.on_message` برای ساخت سریع سلف‌بات
  - روترها و دیسپچر قدرتمند (`Dispatcher`, `Router`) برای پروژه‌های بزرگ
  - فیلترهای جادویی `F` (MagicFilter)
- 🧠 **ماشین حالت پیشرفته (FSM):** مدیریت استیت‌های گفتگو با ذخیره‌سازی در حافظه موقت (`MemoryStorage`) یا دیتابیس پایدار (`SQLiteStorage`).
- 🎙️ **پشتیبانی از ویس‌چت (WebRTC Voice Chat):** ایجاد، بستن، مدیریت وضعیت صحبت و دریافت لیست شرکت‌کنندگان ویس‌چت گروه‌ها و کانال‌ها.
- 💬 **مکالمات مرحله‌به‌مرحله (Conversation):** کانتکست منیجر `async with client.conversation(...)` جهت پرسش و پاسخ خطی تعاملی.
- 👥 **مدیریت چند اکانت همزمان (`ClientManager`):** اجرای چندین اکانت سلف‌بات به صورت همزمان روی یک ایونت‌لوپ واحد.
- 🛠️ **ابزار خط فرمان (CLI):** لاگین آسان و استخراج سشن با `aioshad login` و تولید ساختار پروژه استاندارد با `aioshad init`.

---

## 📦 نصب (Installation)

```bash
pip install aioshad-py
```

یا از طریق `uv`:

```bash
uv add aioshad-py
```

---

## ⚡ شروع سریع (Quickstart)

یک ربات اکو و پاسخ به دستور `!ping`:

```python
import asyncio
from aioshad import Client, F
from aioshad.filters import IsMe
from aioshad.types import Message

# در صورت نیاز می‌توانید پروکسی هم ست کنید:
# client = Client(session="my_shad_bot", proxy="http://127.0.0.1:7897")
client = Client(session="my_shad_bot")

# پاسخ به پیام‌هایی که با "echo " شروع می‌شوند
@client.on_message(F.text.startswith("echo "))
async def echo_handler(msg: Message):
    content = msg.text[5:].strip()
    await msg.reply(f"📣 {content}")

# پاسخ به دستور پینگ ارسالی توسط خودتان
@client.on_message(IsMe(), F.text == "!ping")
async def ping_handler(msg: Message):
    await msg.edit("🏓 Pong! سلف‌بات فعال است.")

if __name__ == "__main__":
    client.run()
```

> **نکته:** در اولین اجرا، کتابخانه شماره تلفن و کد تایید ارسالی را در ترمینال از شما می‌پرسد و نشست را در فایل `my_shad_bot.session` ذخیره می‌کند. در دفعات بعدی لاگین کاملاً خودکار انجام می‌شود.

---

## 🧩 استفاده از ساختار روترها (Routers & Commands)

برای پروژه‌های ماژولار می‌توانید از روترها استفاده کنید:

```python
import asyncio
from aioshad import Client, Dispatcher, Router
from aioshad.filters import Command, CommandObject, IsGroup
from aioshad.types import Message

router = Router(name="main_router")

@router.message(Command("start", "help", prefix="/!."))
async def handle_start(msg: Message, command: CommandObject):
    await msg.reply(
        f"👋 سلام!\\n"
        f"دستور: `{command.prefix}{command.command}`\\n"
        f"آرگومان: `{command.args or 'ندارد'}`"
    )

@router.message(IsGroup(), Command("info", prefix="!"))
async def handle_group_info(msg: Message):
    chat = await msg.get_chat()
    await msg.reply(f"نام گروه: {chat.title}\\nتعداد اعضا: {chat.members_count}")

async def main():
    dp = Dispatcher()
    dp.include_router(router)
    client = Client(session="my_bot", dispatcher=dp)
    await client.start()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 💬 مکالمات مرحله‌به‌مرحله (Conversation)

```python
@client.on_message(Command("register", prefix="!"))
async def register_flow(msg: Message):
    async with client.conversation(msg.chat_guid, timeout=60) as conv:
        await conv.send_message("لطفاً نام خود را وارد کنید:")
        name_msg = await conv.get_response()
        
        await conv.send_message(f"خوش‌آمدید {name_msg.text}! حالا سن خود را بفرمایید:")
        age_msg = await conv.get_response()
        
        await conv.send_message(f"اطلاعات شما با موفقیت ثبت شد: {name_msg.text} ({age_msg.text} سال)")
```

---

## 📸 ارسال و دریافت مدیا (Media & Files)

```python
# ارسال عکس
await client.send_photo(chat_guid, "picture.jpg", caption="تصویر نمونه")

# ارسال فایل یا سند
await client.send_file(chat_guid, "report.pdf", file_name="گزارش.pdf", caption="فایل ضمیمه")

# ارسال پیام صوتی
await client.send_voice(chat_guid, "voice.ogg")

# دانلود فایل از پیام دریافتی
if msg.file_inline:
    file_bytes = await client.download_file(msg.file_inline, destination="downloaded.jpg")
```

---

## 🛠️ دستورات CLI

پکیج `aioshad-py` همراه با ابزار خط فرمان عرضه می‌شود:

```bash
# ایجاد اسکلت پروژه کامل و آماده توسعه
aioshad init my_project

# لاگین به حساب کاربری و ساخت فایل سشن
aioshad login -s my_account

# بررسی و مشاهده مشخصات یک نشست ذخیره شده
aioshad session-info my_account.session
```

---

## 👥 اجرای چند اکانت به صورت همزمان (ClientManager)

```python
from aioshad import Dispatcher, F
from aioshad.client.manager import ClientManager
from aioshad.types import Message

dp = Dispatcher()

@dp.message(F.text == "!status")
async def check_status(msg: Message, client):
    await msg.reply(f"اکانت فعال است! شناسه کاربری: {client.me}")

def main():
    manager = ClientManager(dispatcher=dp)
    manager.add_client(session="acc1", phone_number="09121111111")
    manager.add_client(session="acc2", phone_number="09122222222")
    manager.run_all()

if __name__ == "__main__":
    main()
```

---

## 📄 لایسنس (License)

این پروژه تحت مجوز [MIT](LICENSE) منتشر شده است.
Copyright (c) 2026 Mohammadamin Madani.
