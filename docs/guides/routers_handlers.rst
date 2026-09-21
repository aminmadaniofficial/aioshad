Routers and Handlers
====================

``aioshad`` follows an architecture directly inspired by **aiogram 3**, allowing complete modularity across files and packages using `Router` and `Dispatcher`.

Architecture Overview
---------------------

- **Dispatcher**: The root event processor. It manages the update pipeline, middleware chain, and dispatches updates down into registered routers.
- **Router**: An isolated sub-tree of event handlers and nested child routers.
- **Handler**: An asynchronous callable that processes an incoming update matching certain filters.

Registering Handlers
--------------------

You can register handlers on a ``Client`` directly, or on an independent ``Router``:

.. code-block:: python

   from aioshad import Router, F
   from aioshad.types import Message

   router = Router(name="moderation_router")

   @router.message(F.text == "!warn")
   async def warn_user(msg: Message):
       if msg.reply_to_message_id:
           await msg.reply("User has been issued a warning.")

Structuring Modular Applications
--------------------------------

For production projects, decouple feature areas into separate modules:

.. code-block:: text

   my_bot/
   ├── main.py
   └── handlers/
       ├── __init__.py
       ├── user_commands.py
       ├── admin_commands.py
       └── group_moderation.py

In ``handlers/user_commands.py``:

.. code-block:: python

   from aioshad import Router, F
   from aioshad.filters import Command
   from aioshad.types import Message

   user_router = Router()

   @user_router.message(Command("help"))
   async def help_command(msg: Message):
       await msg.reply("Available commands: /start, /help, /settings")

In ``handlers/admin_commands.py``:

.. code-block:: python

   from aioshad import Router, F
   from aioshad.filters import Command, IsGroup
   from aioshad.types import Message

   admin_router = Router()

   @admin_router.message(IsGroup(), Command("ban"))
   async def ban_command(msg: Message):
       await msg.reply("Action logged.")

In ``main.py``:

.. code-block:: python

   from aioshad import Client
   from handlers.user_commands import user_router
   from handlers.admin_commands import admin_router

   client = Client(session="my_bot")

   # Register sub-routers onto the main client
   client.include_router(user_router)
   client.include_router(admin_router)

   if __name__ == "__main__":
       client.run()

Execution Flow
--------------

When an incoming message arrives:

1. The root dispatcher receives the raw update from the Shad connection.
2. It evaluates routers in the order they were included.
3. Within each router, handlers are evaluated sequentially.
4. The first handler whose filters all return truthy executes.
5. Once a handler finishes, dispatching terminates for that event.
