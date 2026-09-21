Filters and Magic Filter (F)
=============================

Filters allow you to declaratively determine whether an incoming update should trigger a specific handler. You can filter by text content, author identity, chat type, or complex nested attributes.

Magic Filter (F)
----------------

``aioshad`` supports magic filter expressions via ``F``. This allows writing intuitive condition trees without verbose lambda functions.

Text Matching
~~~~~~~~~~~~~

.. code-block:: python

   from aioshad import F

   # Exact equality
   @client.on_message(F.text == "hello")

   # Prefix and suffix
   @client.on_message(F.text.startswith("!"))
   @client.on_message(F.text.endswith(".zip"))

   # In-string containment
   @client.on_message(F.text.contains("shadi"))

   # Case-insensitive checks
   @client.on_message(F.text.lower() == "ping")

Attribute Checks
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Match only replies to another message
   @client.on_message(F.reply_to_message_id.is_not(None))

   # Match only forwarded messages
   @client.on_message(F.forwarded_from.is_not(None))

   # Match specific sender GUIDs
   @client.on_message(F.author_guid == "u0abc1234567890")

Combining Filters
~~~~~~~~~~~~~~~~~

Filters can be combined with standard bitwise operators:

- ``&`` : Logical AND
- ``|`` : Logical OR
- ``~`` : Logical NOT

.. code-block:: python

   # Only handle commands starting with ! or / sent in a group
   @client.on_message(IsGroup() & (F.text.startswith("!") | F.text.startswith("/")))
   async def handle_commands(msg: Message):
       pass

Built-in Filters
----------------

Command Filter
~~~~~~~~~~~~~~

The ``Command`` filter matches command names, optionally with prefixes and case-sensitivity, and injects a ``CommandObject``:

.. code-block:: python

   from aioshad.filters import Command, CommandObject

   @client.on_message(Command("start", "help", prefix="/"))
   async def cmd_handler(msg: Message, command: CommandObject):
       cmd_name = command.command   # "start" or "help"
       args = command.args          # Remaining text arguments
       await msg.reply(f"Executed /{cmd_name} with arguments: {args}")

IsMe Filter
~~~~~~~~~~~

Matches updates sent from your own logged-in account (ideal for self-bots):

.. code-block:: python

   from aioshad.filters import IsMe

   @client.on_message(IsMe(), F.text == "!status")
   async def self_status(msg: Message):
       await msg.edit("All systems operational.")

Chat Type Filters
~~~~~~~~~~~~~~~~~

Direct messages to appropriate scopes:

.. code-block:: python

   from aioshad.filters import IsPrivate, IsGroup, IsChannel

   @client.on_message(IsPrivate())
   async def private_chat_only(msg: Message):
       pass

   @client.on_message(IsGroup())
   async def group_chat_only(msg: Message):
       pass

   @client.on_message(IsChannel())
   async def channel_post_only(msg: Message):
       pass

Custom Filters
--------------

Create custom reusable filter classes by inheriting from ``BaseFilter``:

.. code-block:: python

   from aioshad.filters import BaseFilter
   from aioshad.types import Message

   class AdminFilter(BaseFilter):
       def __init__(self, admin_guids: set[str]):
           self.admin_guids = admin_guids

       async def __call__(self, msg: Message) -> bool:
           return msg.author_guid in self.admin_guids

   admins = {"u0abc111...", "u0abc222..."}

   @client.on_message(AdminFilter(admins), F.text == "!restart")
   async def admin_restart(msg: Message):
       await msg.reply("Restarting worker nodes...")
