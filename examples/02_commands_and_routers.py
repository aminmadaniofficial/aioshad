"""
02_commands_and_routers.py: Modular router architecture with command filters in aioshad.
"""
import asyncio
from aioshad import Client, Dispatcher, Router, F
from aioshad.filters import Command, CommandObject, IsGroup, IsPrivate
from aioshad.types import Message

# Create routers
user_router = Router("user_commands")
group_router = Router("group_commands")


@user_router.message(Command("start", "help", prefix="/!."))
async def cmd_start_help(msg: Message, command: CommandObject):
    await msg.reply(
        f"🤖 **به سلف‌بات شاد خوش آمدید!**\\n"
        f"دستور اجرا شده: `{command.prefix}{command.command}`\\n"
        f"آرگومان‌ها: `{command.args or 'ندارد'}`"
    )


@group_router.message(IsGroup(), Command("info", prefix="!"))
async def cmd_group_info(msg: Message):
    chat = await msg.get_chat()
    await msg.reply(
        f"👥 **اطلاعات گروه:**\\n"
        f"• نام: {chat.title}\\n"
        f"• تعداد اعضا: {chat.members_count}\\n"
        f"• شناسه: `{chat.guid}`"
    )


async def main():
    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(group_router)

    client = Client(session="my_account", dispatcher=dp)
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
