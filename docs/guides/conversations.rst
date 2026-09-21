Conversation Manager
====================

For linear step-by-step dialogs (like filling out forms, quizzes, or waiting for confirmation), `aioshad` provides an asynchronous conversation context manager.

Basic Conversation
------------------

.. code-block:: python

   from aioshad import Client, F
   from aioshad.types import Message

   client = Client(session="my_account")

   @client.on_message(F.text == "!register")
   async def register_flow(msg: Message):
       async with client.conversation(chat_id=msg.object_guid, timeout=60) as conv:
           await conv.send("What is your name?")
           name_msg = await conv.get_response()
           user_name = name_msg.text.strip()

           await conv.send(f"Nice to meet you, {user_name}! How old are you?")
           age_msg = await conv.get_response()
           user_age = age_msg.text.strip()

           await conv.send(f"Registration complete! Name: {user_name}, Age: {user_age}")

Timeout Handling
----------------

If the user does not respond within the configured timeout, a `TimeoutError` is raised:

.. code-block:: python

   import asyncio

   try:
       async with client.conversation(chat_id=msg.object_guid, timeout=30) as conv:
           await conv.send("Confirm action? Reply with 'yes'.")
           reply = await conv.get_response()
           if reply.text.lower() == "yes":
               await conv.send("Confirmed.")
   except asyncio.TimeoutError:
       await msg.reply("Operation timed out due to inactivity.")
