Quickstart
==========

Installation
------------

Install ``aioshad-py`` from PyPI:

.. code-block:: bash

   pip install aioshad-py

Or using ``uv``:

.. code-block:: bash

   uv add aioshad-py

Your First Selfbot
------------------

Here is a complete, minimal example implementing an echo responder and a ``!ping`` command:

.. code-block:: python

   import asyncio
   from aioshad import Client, F
   from aioshad.filters import IsMe
   from aioshad.types import Message

   client = Client(session="my_account")

   @client.on_message(F.text.startswith("echo "))
   async def echo_handler(msg: Message):
       content = msg.text[5:].strip()
       await msg.reply(f"Echo: {content}")

   @client.on_message(IsMe(), F.text == "!ping")
   async def ping_handler(msg: Message):
       await msg.edit("Pong! aioshad is active.")

   if __name__ == "__main__":
       client.run()

First Run & Authentication
--------------------------

When executing this script for the first time:

1. You will be prompted in the terminal to enter your phone number.
2. An SMS or in-app OTP code will be sent to your account.
3. Once entered, the decrypted authentication keypair is safely stored in ``my_account.session``.
4. All future runs authenticate automatically with zero user interaction.
