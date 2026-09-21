Multi-Account Management
========================

``aioshad`` includes a native `ClientManager` designed to run and coordinate dozens or hundreds of accounts concurrently under a single async event loop.

Concurrent Execution
--------------------

.. code-block:: python

   import asyncio
   from aioshad import Client, ClientManager

   manager = ClientManager()

   bot1 = Client(session="account_support")
   bot2 = Client(session="account_sales")
   bot3 = Client(session="account_moderator")

   manager.add_client(bot1)
   manager.add_client(bot2)
   manager.add_client(bot3)

   if __name__ == "__main__":
       asyncio.run(manager.start_all())

Sharing Routers Across Accounts
-------------------------------

You can attach the same router to multiple client instances:

.. code-block:: python

   from aioshad import Router, F
   from aioshad.types import Message

   shared_router = Router()

   @shared_router.message(F.text == "!status")
   async def status_handler(msg: Message):
       await msg.reply("System online.")

   bot1.include_router(shared_router)
   bot2.include_router(shared_router)
