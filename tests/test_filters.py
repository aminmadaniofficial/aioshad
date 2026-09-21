import pytest
from aioshad.filters import (
    Command,
    CommandObject,
    IsGroup,
    IsChannel,
    IsPrivate,
    IsMe,
    IsAdmin,
    IsText,
    IsMedia,
    TextEquals,
    TextContains,
)
from aioshad.types import Message
from aioshad import F


@pytest.mark.asyncio
async def test_command_filter():
    cmd = Command("start", "help", prefix="/!")

    msg1 = Message(id="1", text="/start 12345", author_guid="u0", chat_guid="g0")
    res1 = await cmd(msg1)
    assert isinstance(res1, dict)
    cmd_obj: CommandObject = res1["command"]
    assert cmd_obj.command == "start"
    assert cmd_obj.args == "12345"
    assert cmd_obj.prefix == "/"

    msg2 = Message(id="2", text="!help", author_guid="u0", chat_guid="g0")
    res2 = await cmd(msg2)
    assert isinstance(res2, dict)
    assert res2["command"].command == "help"

    msg3 = Message(id="3", text="other text", author_guid="u0", chat_guid="g0")
    assert await cmd(msg3) is False


@pytest.mark.asyncio
async def test_chat_filters():
    group_msg = Message(id="1", text="hi", author_guid="u0", chat_guid="g0abcdef")
    channel_msg = Message(id="2", text="hi", author_guid="u0", chat_guid="c0abcdef")
    pv_msg = Message(id="3", text="hi", author_guid="u0", chat_guid="u0abcdef")

    assert await IsGroup()(group_msg) is True
    assert await IsGroup()(channel_msg) is False

    assert await IsChannel()(channel_msg) is True
    assert await IsChannel()(group_msg) is False

    assert await IsPrivate()(pv_msg) is True
    assert await IsPrivate()(group_msg) is False


@pytest.mark.asyncio
async def test_is_admin_filter():
    admin_filter = IsAdmin("u0admin1", "u0admin2")
    msg1 = Message(id="1", text="hi", author_guid="u0admin1", chat_guid="g0")
    msg2 = Message(id="2", text="hi", author_guid="u0user", chat_guid="g0")

    assert await admin_filter(msg1) is True
    assert await admin_filter(msg2) is False


@pytest.mark.asyncio
async def test_magic_filter():
    msg = Message(id="1", text="Salam Shad!", author_guid="u0author", chat_guid="g0group")

    assert F.text.startswith("Salam").resolve(msg)
    assert not F.text.startswith("Bye").resolve(msg)
    assert (F.chat_guid == "g0group").resolve(msg)
    assert (F.author_guid == "u0author").resolve(msg)
