Routers and Handlers
====================

``aioshad`` uses an architecture directly inspired by **aiogram 3**, allowing modular separation of concerns across multiple files using `Router` and `Dispatcher`.

Architecture Overview
---------------------

- **Dispatcher**: The central event coordinator. Handles update loops, middleware execution, and dispatches events to registered routers.
- **Router**: A sub-tree of event handlers and nested sub-routers.
- **Handler**: An asynchronous function that processes an incoming update matching certain filters.

Basic Handler Registration
--------------------------

On a `Client` or `Router`, handlers can be registered via decorators:

.. code-block:: python

   from aioshad import Client, Router, F
   from aioshad.types import Message

   router = Router()

   @router.message(F.text == "hello")
   async def handle_hello(msg: Message):
       await msg.reply("Hello there! How can I help you today?")

Modular Project Structure
-------------------------

For scalable projects, split your bot logic into distinct router modules:

.. code-block:: text

   my_bot/
   ├── main.py
   └── handlers/
       ├── __init__.py
       ├── user_commands.py
       ├── admin_commands.py
       └── group_moderation.py

In `handlers/user_commands.py`:

.. code-block:: python

   from aioshad import Router, F
   from aioshad.types import Message

   user_router = Router()

   @user_router.message(F.text == "/help")
   async def help_cmd(msg: Message):
       await msg.reply("Available commands: /help, /status, /info")

In `main.py`:

.. code-block:: python

   from aioshad import Client
   from handlers.user_commands import user_router

   client = Client(session="bot")
   client.include_router(user_router)

   if __name__ == "__main__":
       client.run()
