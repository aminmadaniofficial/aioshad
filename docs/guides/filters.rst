Filters and Magic F
====================

Filters allow you to declaratively determine whether an incoming update should trigger a handler.

Magic Filter (F)
----------------

``aioshad`` supports magic filter expressions via `F` (from `aioshad.filters.magic` or top-level `aioshad`):

.. code-block:: python

   from aioshad import F

   # Match exact text
   @client.on_message(F.text == "hello")

   # Match prefix or suffix
   @client.on_message(F.text.startswith("/"))
   @client.on_message(F.text.endswith(".pdf"))

   # Case-insensitive checks
   @client.on_message(F.text.lower() == "ping")

   # Check message attributes
   @client.on_message(F.reply_to_message_id.is_not(None))

Built-in Filters
----------------

``aioshad.filters`` provides several standard filters:

Command Filter
~~~~~~~~~~~~~~

Matches bot commands, parsing arguments automatically:

.. code-block:: python

   from aioshad.filters import Command

   @client.on_message(Command("start", "help"))
   async def handle_commands(msg: Message, command: CommandObject):
       await msg.reply(f"Command triggered: {command.command} with args: {command.args}")

IsMe Filter
~~~~~~~~~~~

Matches messages sent by your own logged-in account (useful for self-bots):

.. code-block:: python

   from aioshad.filters import IsMe

   @client.on_message(IsMe(), F.text == "!ping")
   async def handle_self_ping(msg: Message):
       await msg.edit("Pong! Active.")

Chat Type Filters
~~~~~~~~~~~~~~~~~

Filter by group, private, or channel contexts:

.. code-block:: python

   from aioshad.filters import IsGroup, IsPrivate, IsChannel

   @client.on_message(IsGroup())
   async def group_only_handler(msg: Message):
       pass

Custom Filters
--------------

Any callable accepting an event and returning a boolean (or truthy value/dict) can be used as a filter:

.. code-block:: python

   from aioshad.filters import BaseFilter
   from aioshad.types import Message

   class AdminFilter(BaseFilter):
       def __init__(self, admin_guids: list[str]):
           self.admin_guids = admin_guids

       async def __call__(self, msg: Message) -> bool:
           return msg.author_guid in self.admin_guids

   @client.on_message(AdminFilter(["u0abc...", "u0def..."]))
   async def handle_admin(msg: Message):
       await msg.reply("Welcome, administrator.")
