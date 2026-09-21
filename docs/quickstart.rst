Quickstart
==========

Welcome to ``aioshad``! This tutorial will guide you through installing the package, authenticating with your Shad account, and writing your first event-driven bot or self-bot in minutes.

Prerequisites
-------------

- Python 3.9 or higher.
- A valid phone number registered on Shad Messenger (شاد).

Installation
------------

Install ``aioshad-py`` via `pip`:

.. code-block:: bash

   pip install aioshad-py

Or using `uv`:

.. code-block:: bash

   uv add aioshad-py

Your First Script
-----------------

Create a new file named ``bot.py``:

.. code-block:: python

   import asyncio
   from aioshad import Client, F
   from aioshad.filters import Command, IsMe
   from aioshad.types import Message

   # Initialize client with persistent session storage
   client = Client(session="my_account")

   # Self-bot command: triggers only when you type !ping in any chat
   @client.on_message(IsMe(), F.text == "!ping")
   async def ping_handler(msg: Message):
       await msg.edit("Pong! aioshad is active.")

   # Public responder: triggers when anyone sends "echo <text>"
   @client.on_message(F.text.startswith("echo "))
   async def echo_handler(msg: Message):
       text_to_echo = msg.text[5:].strip()
       await msg.reply(f"Echo: {text_to_echo}")

   if __name__ == "__main__":
       client.run()

First Run & Authentication
--------------------------

When executing your script for the first time:

.. code-block:: text

   Enter phone number (e.g. 0912...): 09123456789
   Enter OTP code sent to 989123456789: 12345

1. You will be prompted in the terminal to enter your phone number.
2. An SMS or in-app OTP code will be sent to your account.
3. Once entered, the decrypted authentication keypair is safely stored in ``my_account.session``.
4. All future runs authenticate automatically with zero user interaction!

Using asyncio Directly
----------------------

If you prefer to integrate ``aioshad`` into an existing asynchronous event loop, use ``client.start()``:

.. code-block:: python

   import asyncio
   from aioshad import Client

   client = Client(session="my_account")

   async def main():
       # Connect, authenticate, and listen for events
       await client.start()

   if __name__ == "__main__":
       asyncio.run(main())

Next Steps
----------

Now that you have a running client, explore the guides:

- :doc:`guides/routers_handlers` - Structure large projects using Routers and Dispatchers.
- :doc:`guides/filters` - Deep dive into Magic Filter ``F`` and built-in filters.
- :doc:`guides/sessions` - Learn about SQLite and secure session storage.
- :doc:`guides/conversations` - Build linear step-by-step interactive flows.
- :doc:`guides/fsm` - Manage multi-step user states with Finite State Machines.
