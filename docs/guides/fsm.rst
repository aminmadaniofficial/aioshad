Finite State Machine (FSM)
===========================

The Finite State Machine allows you to manage multi-step user workflows across independent messages without blocking event loops.

Defining States
---------------

Subclass `StatesGroup` and declare `State` attributes:

.. code-block:: python

   from aioshad.fsm import StatesGroup, State

   class SupportTicket(StatesGroup):
       waiting_for_subject = State()
       waiting_for_description = State()
       waiting_for_confirmation = State()

Handling State Transitions
--------------------------

.. code-block:: python

   from aioshad import Client, F
   from aioshad.types import Message
   from aioshad.fsm.context import FSMContext

   client = Client(session="bot")

   @client.on_message(F.text == "/ticket")
   async def start_ticket(msg: Message, state: FSMContext):
       await state.set_state(SupportTicket.waiting_for_subject)
       await msg.reply("Please enter the subject of your ticket:")

   @client.on_message(SupportTicket.waiting_for_subject)
   async def process_subject(msg: Message, state: FSMContext):
       await state.update_data(subject=msg.text)
       await state.set_state(SupportTicket.waiting_for_description)
       await msg.reply("Subject recorded. Now please describe the issue in detail:")

   @client.on_message(SupportTicket.waiting_for_description)
   async def process_description(msg: Message, state: FSMContext):
       data = await state.get_data()
       subject = data.get("subject")
       description = msg.text

       await state.clear()
       await msg.reply(
           f"Ticket submitted successfully!\n\n"
           f"Subject: {subject}\n"
           f"Description: {description}"
       )
