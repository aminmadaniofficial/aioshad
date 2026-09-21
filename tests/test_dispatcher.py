import pytest
from aioshad.dispatcher import Dispatcher, Router
from aioshad.filters import Command
from aioshad.middlewares import BaseMiddleware
from aioshad.types import Message


class CustomLoggingMiddleware(BaseMiddleware):
    def __init__(self):
        self.called = False

    async def __call__(self, handler, event, data):
        self.called = True
        data["injected"] = "custom_data"
        return await handler(event, data)


@pytest.mark.asyncio
async def test_dispatcher_event_routing():
    dp = Dispatcher()
    mw = CustomLoggingMiddleware()
    dp.middleware(mw)

    received_messages = []

    @dp.message(Command("hello"))
    async def handle_hello(msg: Message, command, injected=None):
        received_messages.append((msg.text, command.command, injected))

    msg = Message(id="1", text="/hello world", author_guid="u0author", chat_guid="g0chat")
    await dp.dispatch("message", msg)

    assert mw.called is True
    assert len(received_messages) == 1
    text, cmd, injected = received_messages[0]
    assert text == "/hello world"
    assert cmd == "hello"
    assert injected == "custom_data"


@pytest.mark.asyncio
async def test_include_router():
    dp = Dispatcher()
    router = Router("test_router")

    handled = []

    @router.message()
    async def router_handler(msg: Message):
        handled.append(msg.id)

    dp.include_router(router)

    msg = Message(id="99", text="anything", author_guid="u0", chat_guid="g0")
    await dp.dispatch("message", msg)

    assert handled == ["99"]
